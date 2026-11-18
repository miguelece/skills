#!/usr/bin/env python3
"""Account for one subagent attempt from its Claude Code transcript.

Reads the transcript a worker, integrator or analyst left on disk and prints
one JSON record with the figures the supervisor's allocation log needs:

- API calls, and per model the input, five-minute and one-hour cache-write,
  cache-read and output tokens and web search requests;
- the list-price cost, per model and in total, from the dated table in
  `prices.json` beside this script;
- the effort the calls ran at;
- the tool calls, the verification calls among them, and their share.

    scripts/account_attempt.py <transcript.jsonl>
    scripts/account_attempt.py <transcript.jsonl> --grant "standard: 40 calls" \\
        --justification "first attempt" --also qa-suite --reconcile
    scripts/account_attempt.py --match-rate ~/.claude/projects/<project> --last 20

Counting rules:

- **An API call is one distinct message id carrying usage.** A streamed
  response repeats its usage over several entries; it is counted once, at the
  entry with the largest output count.
- **A verification call is a shell call that invokes a checker** in at least
  one of its command segments. A mention, such as `grep pytest`, does not
  count, a heredoc's body is data, and a compound command counts once.
  Reviewing a change (`git diff`, `git show` of a commit) counts, because the
  measurement that set the supervisor's 25% ceiling counted it. `--also NAME`
  adds a checker for one run: an executable or a script's file name.
- **A call the table cannot price is reported, never priced as zero.** An
  unknown model, an unknown inference geography, or fast mode on a model with
  no fast price makes the total `null`; `priced_cost_usd` still sums the rest.

`--reconcile` prices the whole session the transcript belongs to (the main
transcript and every subagent's) and compares it, per model, with the last
`cost-state` entry Claude Code wrote to the main transcript, its own record of
the session's cost. Each model reports `match` when the two agree within
`TOLERANCE`, and the session is `match` when every model does.

**One session's mismatch is not evidence of a stale table**, so nothing is
warned here. The harness records calls that no transcript holds (Haiku side
calls, a few percent of extra Opus spend), and its record can cover more or
less than one transcript. A stale price instead breaks the exact match in
every session that used it. So the signal is a *match rate* across sessions.
Claude Code writes the record when a session ends, so a running supervisor's
own session has none yet: `--match-rate PROJECT_DIR` reads the project's most
recent finished sessions instead, and the supervisor's gate report shows the
rate. A rate near zero flags the table. A session that cannot be matched reports `unexplained`, one with an
unpriced call `incomplete`, and one with no `cost-state` `absent`: the entry
is undocumented and may disappear.

Standard library only, deterministic, and no network. Exits 0 with a record,
2 when the transcript cannot be read.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PRICES = Path(__file__).with_name("prices.json")

# Largest relative difference between the priced and recorded cost of one
# model that still counts as a match. A correct table matches to the cent, so
# this only absorbs rounding; it is not a tolerance for a stale price. Set from
# this lab's 46 sessions with a cost record.
TOLERANCE = 0.005

TOKEN_CLASSES = ("input", "cache_write_5m", "cache_write_1h", "cache_read", "output")
SHELL_TOOLS = {"Bash", "PowerShell"}

# --- verification classifier ------------------------------------------------

SEGMENT_SPLIT = re.compile(r"&&|\|\||;|\||\n|\$\(|`")
LEADING_NOISE = re.compile(
    r"^(?:(?:do|then|else|time|!|&|\(|\{|[A-Za-z_]\w*=(?:\"[^\"]*\"|'[^']*'|\S*))\s+"
    r"|timeout\s+\S+\s+)+"
)

# Executables that are checkers whatever their arguments.
CHECKERS = {
    "pytest", "py.test", "tox", "nox", "jest", "vitest", "mocha", "ava",
    "playwright", "cypress", "phpunit", "rspec", "ctest",
    "eslint", "ruff", "flake8", "pylint", "mypy", "pyright", "shellcheck",
    "golangci-lint", "hadolint", "stylelint",
    "markdownlint", "markdownlint-cli", "markdownlint-cli2",
}
# Executables that are checkers only with one of these subcommands or flags.
CHECKER_SUBCOMMANDS = {
    "go": {"test", "vet"},
    "cargo": {"test", "clippy", "check", "nextest"},
    "npm": {"test", "t"},
    "pnpm": {"test", "t"},
    "yarn": {"test"},
    "bun": {"test"},
    "deno": {"test", "lint", "check"},
    "dotnet": {"test"},
    "mvn": {"test", "verify"},
    "gradle": {"test", "check"},
    "gradlew": {"test", "check"},
    "make": {"test", "check"},
    "tsc": {"--noEmit"},
    "black": {"--check"},
    "prettier": {"--check"},
    "biome": {"check", "lint", "ci"},
}
# `npm run test`, `pnpm run lint`: a script named like a checker.
RUN_SCRIPT_NAMES = {"test", "tests", "lint", "check", "typecheck", "verify"}
# Package runners whose next argument is the real executable.
PACKAGE_RUNNERS = {"npx", "pnpx", "bunx"}
RUNNER_SUBCOMMANDS = {"pnpm": {"dlx", "exec"}, "yarn": {"dlx", "exec"}, "npm": {"exec"}}
# Python modules run as `python -m <module>` that are checkers.
PYTHON_MODULES = {
    "pytest", "unittest", "mypy", "ruff", "pyright", "flake8", "pylint",
    "py_compile", "compileall",
}
# Scripts that are checkers whatever their arguments: the board and research
# base validators that ship with the published skills.
CHECK_SCRIPTS = {"validate_board.py", "validate_base.py", "linkscan.py", "bytecode_guard.py"}
# Scripts that are checkers only when run with --check.
CHECK_FLAG_SCRIPTS = {"build.py", "index.py", "generate_index.py", "relink.py"}
# Any other script whose name says it checks.
CHECKING_SCRIPT_NAME = re.compile(r"(check|verif|validat|mutat)", re.IGNORECASE)


def _executable(token: str) -> str:
    name = token.replace("\\", "/").rsplit("/", 1)[-1].lower()
    for suffix in (".exe", ".cmd", ".bat"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    return name.split("@", 1)[0] if not name.startswith("@") else name


def _is_python(name: str) -> bool:
    return name == "py" or re.fullmatch(r"python[\d.]*", name) is not None


def _script_is_checker(script: str, args: list[str], also: set[str]) -> bool:
    name = script.replace("\\", "/").rsplit("/", 1)[-1]
    if name in also or name in CHECK_SCRIPTS:
        return True
    if name in CHECK_FLAG_SCRIPTS:
        return "--check" in args
    return CHECKING_SCRIPT_NAME.search(Path(name).stem) is not None


def _tokens_are_checker(tokens: list[str], also: set[str]) -> bool:
    if not tokens:
        return False
    exe, args = _executable(tokens[0]), tokens[1:]
    raw = tokens[0].replace("\\", "/").rsplit("/", 1)[-1]
    if exe in also or raw in also:
        return True
    if exe in CHECKERS:
        return True
    if exe in PACKAGE_RUNNERS:
        return _tokens_are_checker(_without_flags(args), also)
    if exe in RUNNER_SUBCOMMANDS and args and args[0] in RUNNER_SUBCOMMANDS[exe]:
        return _tokens_are_checker(_without_flags(args[1:]), also)
    if exe in {"npm", "pnpm", "yarn", "bun"} and len(args) >= 2 and args[0] == "run":
        return args[1] in RUN_SCRIPT_NAMES or args[1] in also
    if exe in CHECKER_SUBCOMMANDS:
        return any(a in CHECKER_SUBCOMMANDS[exe] for a in args)
    if _is_python(exe):
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "-m":
                return i + 1 < len(args) and args[i + 1] in PYTHON_MODULES | also
            if arg in ("-c", "-"):  # inline code or stdin: no script to judge
                return False
            if arg.startswith("-"):
                i += 2 if arg in ("-X", "-W") else 1
                continue
            return _script_is_checker(arg, args[i + 1 :], also)
        return False
    if exe == "git":
        return _git_reviews(args)
    if exe == "claude":
        return "validate" in args
    if "=" in tokens[0]:  # an assignment, not a command
        return False
    if raw.endswith(".py") or raw.endswith(".sh") or raw.endswith(".ps1"):
        return _script_is_checker(raw, args, also)
    return False


# Package-runner flags that take a value, which is not the executable.
RUNNER_VALUE_FLAGS = {"--prefix", "--package", "-p", "--cwd", "-C", "--dir", "--config", "-c"}


def _without_flags(args: list[str]) -> list[str]:
    """A package runner's arguments with its own flags, and their values, dropped."""
    kept: list[str] = []
    skip = False
    for arg in args:
        if skip:
            skip = False
        elif arg in RUNNER_VALUE_FLAGS:
            skip = True
        elif not arg.startswith("-"):
            kept.append(arg)
    return kept


def _git_reviews(args: list[str]) -> bool:
    """`git diff`, and `git show` of a commit: reviewing a change.

    Counted because the measurement that set the 25% verification ceiling
    counted them, so the meter counts on the basis the ceiling was calibrated
    on. `git show <rev>:<path>` reads a file and is not counted.
    """
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in ("-C", "-c") else 1
    if i >= len(args):
        return False
    sub, rest = args[i], args[i + 1 :]
    if sub == "diff":
        return True
    if sub == "show":
        return not any(":" in r for r in rest if not r.startswith("-"))
    return False


HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?\n.*?\n\1\b", re.DOTALL)


def is_verification(command: str, also: set[str]) -> bool:
    """True when any segment of a shell command invokes a checker.

    A heredoc's body is data written to a file or a stdin, not commands, so it
    is dropped before the command is split.
    """
    command = HEREDOC.sub(" ", command)
    for segment in SEGMENT_SPLIT.split(command):
        segment = re.sub(r"[(){}]", " ", segment)
        segment = LEADING_NOISE.sub("", segment.strip())
        tokens = segment.replace('"', " ").replace("'", " ").split()
        if _tokens_are_checker(tokens, also):
            return True
    return False


# --- reading a transcript ----------------------------------------------------


def read_entries(path: Path):
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def collect(paths: list[Path]) -> tuple[dict, dict, list[str], list[dict]]:
    """Calls by message id, tool uses by id, efforts, and cost-state entries."""
    calls: dict[str, tuple[str, dict]] = {}
    tools: dict[str, dict] = {}
    efforts: set[str] = set()
    cost_states: list[dict] = []
    for path in paths:
        for entry in read_entries(path):
            if entry.get("type") == "cost-state":
                cost_states.append(entry)
                continue
            message = entry.get("message")
            if not isinstance(message, dict):
                continue
            use = message.get("usage")
            model = message.get("model") or ""
            if isinstance(use, dict) and not model.startswith("<"):
                key = message.get("id") or f"{path.name}:{len(calls)}"
                kept = calls.get(key)
                if kept is None or (use.get("output_tokens") or 0) > (kept[1].get("output_tokens") or 0):
                    calls[key] = (model, use)
                effort = entry.get("effort")
                if isinstance(effort, str):
                    efforts.add(effort)
            content = message.get("content")
            if message.get("role") == "assistant" and isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tools.setdefault(block.get("id") or f"{path.name}:{len(tools)}", block)
    return calls, tools, sorted(efforts), cost_states


def token_counts(use: dict) -> dict[str, int]:
    tiers = use.get("cache_creation") or {}
    w5 = int(tiers.get("ephemeral_5m_input_tokens") or 0)
    w1 = int(tiers.get("ephemeral_1h_input_tokens") or 0)
    if not tiers:  # an older entry with only the total: the five-minute tier
        w5 = int(use.get("cache_creation_input_tokens") or 0)
    return {
        "input": int(use.get("input_tokens") or 0),
        "cache_write_5m": w5,
        "cache_write_1h": w1,
        "cache_read": int(use.get("cache_read_input_tokens") or 0),
        "output": int(use.get("output_tokens") or 0),
    }


def price_call(model: str, use: dict, counts: dict, table: dict) -> float | None:
    """List-price cost of one call, or None when the table cannot price it."""
    rates = table["models"].get(model)
    if rates is None:
        return None
    multiplier = table["geo_multipliers"].get(use.get("inference_geo") or "global")
    if multiplier is None:
        return None
    speed = use.get("speed") or "standard"
    if speed == "fast":
        if "fast_multiplier" not in rates:
            return None
        multiplier *= rates["fast_multiplier"]
    elif speed != "standard":
        return None
    long_context = rates.get("long_context")
    if long_context:
        prompt = counts["input"] + counts["cache_write_5m"] + counts["cache_write_1h"] + counts["cache_read"]
        if prompt > long_context["above_prompt_tokens"]:
            rates = long_context
    tokens = sum(counts[k] * rates[k] for k in TOKEN_CLASSES) / 1_000_000
    searches = int((use.get("server_tool_use") or {}).get("web_search_requests") or 0)
    return tokens * multiplier + searches * table["web_search_per_request"]


def tally(calls: dict, table: dict) -> tuple[dict, list[dict], bool]:
    models: dict[str, dict] = {}
    unpriced: dict[tuple, int] = {}
    for model, use in calls.values():
        counts = token_counts(use)
        row = models.setdefault(
            model,
            {**{k: 0 for k in TOKEN_CLASSES}, "calls": 0, "web_search_requests": 0, "cost_usd": 0.0},
        )
        row["calls"] += 1
        for k in TOKEN_CLASSES:
            row[k] += counts[k]
        row["web_search_requests"] += int((use.get("server_tool_use") or {}).get("web_search_requests") or 0)
        cost = price_call(model, use, counts, table)
        if cost is None:
            key = (model, use.get("speed") or "standard", use.get("inference_geo") or "global")
            unpriced[key] = unpriced.get(key, 0) + 1
        else:
            row["cost_usd"] += cost
    for row in models.values():
        row["cost_usd"] = round(row["cost_usd"], 9)
    rows = [
        {"model": m, "speed": s, "geo": g, "calls": n}
        for (m, s, g), n in sorted(unpriced.items())
    ]
    return models, rows, bool(rows)


# --- reconciliation ------------------------------------------------------------


def session_files(transcript: Path) -> list[Path]:
    """The main transcript and every subagent transcript of one session."""
    if transcript.parent.name == "subagents":
        session_dir = transcript.parent.parent
        main = session_dir.parent / f"{session_dir.name}.jsonl"
    else:
        main = transcript
        session_dir = transcript.with_suffix("")
    files = [main] if main.is_file() else []
    files += sorted((session_dir / "subagents").glob("*.jsonl"))
    return files


def reconcile(transcript: Path, table: dict) -> dict:
    files = session_files(transcript)
    calls, _, _, cost_states = collect(files)
    if not cost_states:
        return {"status": "absent"}
    recorded = {
        model: float(row.get("costUSD") or 0.0)
        for model, row in (cost_states[-1].get("modelUsage") or {}).items()
    }
    models, unpriced, _ = tally(calls, table)
    report: dict[str, dict] = {}
    unexplained = False
    for model in sorted(set(recorded) | set(models)):
        priced = models.get(model, {}).get("cost_usd", 0.0)
        got = recorded.get(model, 0.0)
        diff = abs(priced - got) / got if got else (0.0 if priced == 0 else None)
        ok = diff is not None and diff <= TOLERANCE
        unexplained = unexplained or not ok
        report[model] = {
            "match": ok,
            "priced_usd": round(priced, 6),
            "recorded_usd": round(got, 6),
            "relative_difference": None if diff is None else round(diff, 6),
        }
    status = "incomplete" if unpriced else ("unexplained" if unexplained else "match")
    result = {
        "status": status,
        "tolerance": TOLERANCE,
        "session_transcripts": len(files),
        "models": report,
    }
    if cost_states[-1].get("hasUnknownModelCost"):
        result["harness_had_unknown_model_cost"] = True
    return result


def match_rate(project: Path, last: int, table: dict) -> dict:
    """Reconcile the project's most recent main transcripts; count the matches.

    A session without a cost record is still running, or never wrote one, and
    is counted apart rather than as a mismatch.
    """
    mains = sorted(
        project.glob("*.jsonl"), key=lambda p: (-p.stat().st_mtime, p.name)
    )[:last]
    statuses = [reconcile(main, table)["status"] for main in mains]
    compared = sum(1 for s in statuses if s != "absent")
    matched = statuses.count("match")
    return {
        "sessions_read": len(mains),
        "compared": compared,
        "matched": matched,
        "unexplained": statuses.count("unexplained"),
        "incomplete": statuses.count("incomplete"),
        "absent": statuses.count("absent"),
        "rate": round(matched / compared, 6) if compared else None,
        "tolerance": TOLERANCE,
        "prices": {"read_on": table["read_on"], "source": table["source"]},
    }


# --- the record ------------------------------------------------------------------


def account(transcript: Path, also: set[str], table: dict) -> dict:
    calls, tools, efforts, _ = collect([transcript])
    models, unpriced, incomplete = tally(calls, table)
    priced = round(sum(row["cost_usd"] for row in models.values()), 9)
    verification = sum(
        1
        for block in tools.values()
        if block.get("name") in SHELL_TOOLS
        and is_verification(str((block.get("input") or {}).get("command") or ""), also)
    )
    return {
        "transcript": transcript.name,
        "api_calls": len(calls),
        "models": dict(sorted(models.items())),
        "effort": efforts,
        "cost_usd": None if incomplete else priced,
        "priced_cost_usd": priced,
        "unpriced": unpriced,
        "tool_calls": len(tools),
        "verification_calls": verification,
        "verification_share": round(verification / len(tools), 6) if tools else None,
        "prices": {"read_on": table["read_on"], "source": table["source"]},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("transcript", type=Path, nargs="?", help="a subagent transcript (.jsonl)")
    parser.add_argument("--grant", default=None, help="the grant applied, as the supervisor states it")
    parser.add_argument("--justification", default=None, help="why that grant")
    parser.add_argument(
        "--also", action="append", default=[], metavar="NAME",
        help="count this executable or script name as a checker for this run (repeatable)",
    )
    parser.add_argument(
        "--reconcile", action="store_true",
        help="compare the session's priced cost with Claude Code's own record",
    )
    parser.add_argument(
        "--match-rate", type=Path, default=None, metavar="PROJECT_DIR",
        help="instead of one transcript: the match rate over a project's finished sessions",
    )
    parser.add_argument(
        "--last", type=int, default=20,
        help="with --match-rate: how many of the most recent sessions to read (default 20)",
    )
    args = parser.parse_args(argv)

    if (args.transcript is None) == (args.match_rate is None):
        parser.error("give either a transcript or --match-rate PROJECT_DIR")
    table = json.loads(PRICES.read_text(encoding="utf-8"))
    if args.match_rate is not None:
        if not args.match_rate.is_dir():
            print(f"error: no project folder at {args.match_rate}", file=sys.stderr)
            return 2
        rate = match_rate(args.match_rate, args.last, table)
        sys.stdout.write(json.dumps(rate, indent=2, sort_keys=True) + "\n")
        return 0
    if not args.transcript.is_file():
        print(f"error: no transcript at {args.transcript}", file=sys.stderr)
        return 2
    record = account(args.transcript, set(args.also), table)
    record["grant"] = args.grant
    record["justification"] = args.justification
    if args.reconcile:
        record["reconciliation"] = reconcile(args.transcript, table)
    sys.stdout.write(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
