#!/usr/bin/env python3
"""Account for one subagent attempt from its Claude Code transcript.

Reads the transcript a worker, integrator or analyst left on disk and prints
one JSON record with the figures the supervisor's allocation log needs:

- API calls, and per model the input, five-minute and one-hour cache-write,
  cache-read and output tokens and web search requests;
- the list-price cost, per model and in total, from the dated table in
  `prices.json` beside this script;
- the effort the calls ran at;
- the tool calls, the verification calls among them, and their share, a
  logged figure that never escalates;
- the episodes in which the attempt was stuck, and whether there were any.

    scripts/account_attempt.py <transcript.jsonl>
    scripts/account_attempt.py <transcript.jsonl> --grant "standard: 40 calls" \\
        --justification "first attempt" --also qa-suite --reconcile
    scripts/account_attempt.py --match-rate ~/.claude/projects/<project> --last 20
    scripts/account_attempt.py --sessions <run-dir>/leases.md \\
        --project ~/.claude/projects/<project> [--json]

Counting rules:

- **An API call is one distinct message id carrying usage.** A streamed
  response repeats its usage over several entries; it is counted once, at the
  entry with the largest output count.
- **A verification call is a shell call that invokes a checker** in at least
  one of its command segments. A mention, such as `grep pytest`, does not
  count, a heredoc's body is data, and a compound command counts once.
  Reviewing a change (`git diff`, `git show` of a commit) counts, because the
  measurement behind the share's earlier ceiling counted it, and the share is
  kept as a data series on that basis. `--also NAME` adds a checker for one
  run: an executable or a script's file name.
- **A stuck episode is a check repeated without getting anywhere**: the same
  check failing the same way 3 times; the same result 4 times with no edit
  between; or 6 steps alternating an edit and a check whose result does not
  change. "The same" is the command text and the result with timings
  stripped, and a changed result clears it. An edit is an `Edit`,
  `MultiEdit`, `Write` or `NotebookEdit` call. `stuck_episodes` lists each
  one, with the calls it spans counted from 1.
- **A call the table cannot price is reported, never priced as zero.** An
  unknown model, an unknown inference geography, or fast mode on a model with
  no fast price makes the total `null`; `priced_cost_usd` still sums the rest.

`--reconcile` prices the whole session the transcript belongs to (the main
transcript and every subagent's) and compares it, per model, with the last
`cost-state` entry Claude Code wrote to the main transcript, its own record of
the session's cost. It reports both figures and their ratio, priced over
recorded, per model and for the session, and judges nothing: an exact match is
not the normal reading. The harness bills calls no transcript holds (Haiku
side calls no transcript shows at all, and a few percent more Opus), so a
correct table prices a session a few percent under its record, and an
attempt's priced cost reads about 4% under what it was billed. Costs are
reported beside the record, never scaled to it.

**One session's ratio is not evidence of a stale table**, so nothing is
warned here. A stale price instead shifts every session that used it by one
factor, so the signal is each called model's *median* ratio across sessions,
which one outlier does not move. Claude Code writes the record when a session
ends, so a running supervisor's own session has none yet: `--match-rate
PROJECT_DIR` reads the project's most recent finished sessions instead, and
the supervisor's gate report shows the medians. **`table_flagged` is true
when a model's median leaves 0.90 to 1.02**, a band fitted on 2026-11-18 to
the lab's 17 sessions with a recorded Opus cost (median 0.960, 16 of them
between 0.916 and 0.985); a change in what the harness bills outside
transcripts would move it. A billed model no transcript called is listed
under `uncalled`, by name and recorded cost, and never flags the table. A
session with an unpriced call reports `incomplete` and one with no
`cost-state` `absent`; both are left out of the medians. The entry is
undocumented and may disappear.

`--sessions LEASES_MD --project PROJECT_DIR` prints the allocation log's
session table at a tranche's close: it reads every row of the lease table,
whose columns are the template's in `references/run-state.md`, finds each
attempt's transcript by its agent id (`*/subagents/agent-<id>.jsonl`), groups
the attempts by the session they ran in and reconciles each session once. One
Markdown row per session, in lease order; a session with no `cost-state`
prints `absent` for its harness total and ratio; `--json` prints the same rows
as JSON. A lease row whose transcript is not found is named on stderr and the
run exits 1, never dropped.

Standard library only, deterministic, and no network. Exits 0 with a record,
2 when the transcript, project folder or lease table cannot be read.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

PRICES = Path(__file__).with_name("prices.json")

# The band a called model's median ratio of priced over recorded cost must sit
# in, or the price table is flagged. Fitted, not derived: on 2026-11-18 the
# lab's 17 sessions with a recorded Opus cost had a median of 0.960, 16 of them
# between 0.916 and 0.985, because the harness bills calls no transcript holds.
# A change in what it bills that way would move the band.
BAND = (0.90, 1.02)

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

    Counted because the measurement behind the share's earlier ceiling counted
    them, so the logged series keeps one basis. `git show <rev>:<path>` reads a
    file and is not counted.
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
        models, unpriced, _ = tally(calls, table)
        return {
            "status": "absent",
            "session_transcripts": len(files),
            "priced_usd": round(sum(row["cost_usd"] for row in models.values()), 6),
            "unpriced_calls": bool(unpriced),
        }
    recorded = {
        model: float(row.get("costUSD") or 0.0)
        for model, row in (cost_states[-1].get("modelUsage") or {}).items()
    }
    models, unpriced, _ = tally(calls, table)
    report: dict[str, dict] = {}
    for model in sorted(set(recorded) | set(models)):
        priced = models.get(model, {}).get("cost_usd", 0.0)
        got = recorded.get(model, 0.0)
        report[model] = {
            "called": model in models,
            "priced_usd": round(priced, 6),
            "recorded_usd": round(got, 6),
            "ratio": _ratio(priced, got),
        }
    priced_total = sum(row["cost_usd"] for row in models.values())
    recorded_total = sum(recorded.values())
    result = {
        "status": "incomplete" if unpriced else "compared",
        "session_transcripts": len(files),
        "priced_usd": round(priced_total, 6),
        "recorded_usd": round(recorded_total, 6),
        "ratio": _ratio(priced_total, recorded_total),
        "models": report,
    }
    if cost_states[-1].get("hasUnknownModelCost"):
        result["harness_had_unknown_model_cost"] = True
    return result


def _ratio(priced: float, recorded: float) -> float | None:
    """Priced over recorded, or None against a recorded zero."""
    return round(priced / recorded, 6) if recorded else None


def match_rate(project: Path, last: int, table: dict) -> dict:
    """Each called model's median ratio over the project's recent sessions.

    A session without a cost record is still running, or never wrote one, and
    one with an unpriced call understates its priced cost; both are counted
    apart and left out of the medians. A billed model no transcript called is
    reported apart and never flags the table.
    """
    mains = sorted(
        project.glob("*.jsonl"), key=lambda p: (-p.stat().st_mtime, p.name)
    )[:last]
    results = [reconcile(main, table) for main in mains]
    compared = [r for r in results if r["status"] == "compared"]
    ratios: dict[str, list[float]] = {}
    uncalled: dict[str, dict] = {}
    for result in compared:
        for model, row in result["models"].items():
            if row["called"]:
                if row["ratio"] is not None:
                    ratios.setdefault(model, []).append(row["ratio"])
            elif row["recorded_usd"]:
                seen = uncalled.setdefault(model, {"sessions": 0, "recorded_usd": 0.0})
                seen["sessions"] += 1
                seen["recorded_usd"] += row["recorded_usd"]
    low, high = BAND
    medians = {}
    for model, values in sorted(ratios.items()):
        median = round(statistics.median(values), 6)
        medians[model] = {
            "sessions": len(values),
            "median_ratio": median,
            "in_band": low <= median <= high,
        }
    for seen in uncalled.values():
        seen["recorded_usd"] = round(seen["recorded_usd"], 6)
    return {
        "sessions_read": len(mains),
        "compared": len(compared),
        "incomplete": sum(1 for r in results if r["status"] == "incomplete"),
        "absent": sum(1 for r in results if r["status"] == "absent"),
        "band": list(BAND),
        "models": medians,
        "uncalled": dict(sorted(uncalled.items())),
        "table_flagged": (
            any(not row["in_band"] for row in medians.values()) if medians else None
        ),
        "prices": {"read_on": table["read_on"], "source": table["source"]},
    }


# --- the session table -----------------------------------------------------------

# The lease table's columns, as `references/run-state.md` gives its template. A
# table under any other header is refused rather than read by position.
LEASE_COLUMNS = (
    "Task", "Attempt", "State", "Agent id", "Branch", "Start commit", "Grant", "Spend so far",
)
SESSION_COLUMNS = ("Session", "Attempts", "Priced", "Harness total", "Ratio")


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def read_leases(path: Path) -> list[dict]:
    """Every row of a lease table, by the template's column names.

    Raises ValueError when no table carries the template's header, or when a
    row has the wrong number of cells or an Attempt cell that is not all digits.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.lstrip().startswith("|") and tuple(_cells(line)) == LEASE_COLUMNS:
            break
    else:
        raise ValueError(f"no lease table with the columns {' | '.join(LEASE_COLUMNS)}")
    rows = []
    for line in lines[index + 2:]:
        if not line.lstrip().startswith("|"):
            break
        cells = _cells(line)
        if len(cells) != len(LEASE_COLUMNS):
            raise ValueError(f"a lease row with {len(cells)} cells: {line.strip()}")
        row = dict(zip(LEASE_COLUMNS, (cell.strip("`") for cell in cells)))
        if not (row["Attempt"].isascii() and row["Attempt"].isdigit()):
            raise ValueError(f"a lease row whose Attempt is not a number: {line.strip()}")
        rows.append(row)
    return rows


def find_transcript(project: Path, agent_id: str) -> Path | None:
    """A subagent's transcript in a project folder, found by its agent id."""
    if not agent_id:
        return None
    found = sorted(project.glob(f"*/subagents/agent-{agent_id}.jsonl"))
    return found[0] if found else None


def session_table(leases: list[dict], project: Path, table: dict) -> tuple[list[dict], list[str]]:
    """One reconciled row per session the leased attempts ran in, in lease order,
    and a line for each lease row whose transcript was not found."""
    sessions: dict[str, dict] = {}
    missing = []
    for lease in leases:
        transcript = find_transcript(project, lease["Agent id"])
        if transcript is None:
            missing.append(
                f"{lease['Task']} attempt {lease['Attempt']}: no transcript for agent "
                f"{lease['Agent id'] or '(none)'} under {project}"
            )
            continue
        attempt = int(lease["Attempt"])
        sid = transcript.parent.parent.name
        entry = sessions.setdefault(sid, {"transcript": transcript, "attempts": []})
        entry["attempts"].append({"task": lease["Task"], "attempt": attempt})
    rows = []
    for sid, entry in sessions.items():
        result = reconcile(entry["transcript"], table)
        absent = result["status"] == "absent"
        rows.append({
            "session": sid,
            "attempts": entry["attempts"],
            "status": result["status"],
            "priced_usd": result["priced_usd"],
            "recorded_usd": None if absent else result["recorded_usd"],
            "ratio": None if absent else result["ratio"],
            "unpriced_calls": result["status"] == "incomplete" or bool(result.get("unpriced_calls")),
        })
    return rows, missing


def session_markdown(rows: list[dict]) -> str:
    def dollars(value: float) -> str:
        return f"${value:.2f}"

    lines = [
        "| " + " | ".join(SESSION_COLUMNS) + " |",
        "|" + " --- |" * len(SESSION_COLUMNS),
    ]
    for row in rows:
        absent = row["status"] == "absent"
        priced = dollars(row["priced_usd"])
        if row["unpriced_calls"]:
            priced += " (incomplete)"
        ratio = "absent" if absent else ("n/a" if row["ratio"] is None else f"{row['ratio']:.3f}")
        cells = [
            row["session"],
            ", ".join(f"{a['task']} {a['attempt']}" for a in row["attempts"]),
            priced,
            "absent" if absent else dollars(row["recorded_usd"]),
            ratio,
        ]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


# --- the record ------------------------------------------------------------------


# --- the stuck detector ------------------------------------------------------------

EDIT_TOOLS = {"Edit", "MultiEdit", "Write", "NotebookEdit"}
# The thresholds are the OpenHands SDK's stuck-detector defaults, borrowed: the
# lab's supervised attempts held no stuck case to calibrate them on.
REPEATED_FAILURE = 3
REPEATED_RESULT = 4
ALTERNATION_STEPS = 6
TIMING = re.compile(
    r"\d+(?:\.\d+)?\s*(?:ms|s|sec|secs|seconds|m|min)\b|\b\d+:\d{2}(?::\d{2})?(?:\.\d+)?\b"
)


def collect_results(paths: list[Path]) -> dict[str, tuple[str, bool]]:
    """Each tool result's text and error flag, by the id of the call it answers."""
    results: dict[str, tuple[str, bool]] = {}
    for path in paths:
        for entry in read_entries(path):
            message = entry.get("message")
            if not isinstance(message, dict) or not isinstance(message.get("content"), list):
                continue
            for block in message["content"]:
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    content = block.get("content")
                    if isinstance(content, list):
                        content = "\n".join(
                            str(part.get("text") or "") for part in content if isinstance(part, dict)
                        )
                    results.setdefault(
                        str(block.get("tool_use_id")), (str(content or ""), bool(block.get("is_error")))
                    )
    return results


def _same_result(text: str) -> str:
    """A result with its timings stripped, so a re-run that only took longer reads the same."""
    return TIMING.sub("<t>", text).strip()


def stuck_episodes(tools: dict, results: dict, also: set[str]) -> list[dict]:
    """The episodes in which an attempt repeated a check without getting anywhere.

    A check is a verification call; "the same" is its command text and its
    result with timings stripped. Three patterns, each cleared by a changed
    result:

    - repeated-failure: the same check failing the same way 3 times, edits
      between or not;
    - repeated-result: the same check giving the same result 4 times with no
      edit between;
    - edit-check-alternation: 6 steps alternating an edit and the same check
      whose result does not change. Consecutive edits count as one step, and
      calls that neither edit nor check are passed over.
    """
    episodes: list[dict] = []
    failing: dict[str, dict] = {}
    unedited: dict[str, dict] = {}
    alternation: dict | None = None
    last_kind = None

    def note(pattern: str, run: dict, threshold: int) -> None:
        if run["count"] == threshold:
            run["episode"] = {"pattern": pattern, "command": run["command"], "result": run["shown"],
                              "count": run["count"], "first_call": run["first"], "last_call": run["last"]}
            episodes.append(run["episode"])
        elif run["count"] > threshold:
            run["episode"].update(count=run["count"], last_call=run["last"])

    for index, (tool_id, block) in enumerate(tools.items(), start=1):
        name = block.get("name")
        if name in EDIT_TOOLS:
            unedited.clear()
            if last_kind != "edit" and alternation is not None:
                alternation["steps"] += 1
            last_kind = "edit"
            continue
        command = str((block.get("input") or {}).get("command") or "")
        if name not in SHELL_TOOLS or not is_verification(command, also):
            continue
        text, failed = results.get(str(tool_id), ("", False))
        key = (command, _same_result(text))
        shown = text.strip().splitlines()[-1][:200] if text.strip() else ""

        def advance(runs: dict, eligible: bool) -> dict | None:
            run = runs.get(command)
            if not eligible:
                runs.pop(command, None)
                return None
            if run is not None and run["key"] == key:
                run["count"] += 1
                run["last"] = index
            else:
                run = runs[command] = {"key": key, "command": command, "shown": shown,
                                       "count": 1, "first": index, "last": index}
            return run

        run = advance(failing, failed)
        if run is not None:
            note("repeated-failure", run, REPEATED_FAILURE)
        note("repeated-result", advance(unedited, True), REPEATED_RESULT)

        if last_kind == "edit" and alternation is not None and alternation["key"] == key:
            alternation["steps"] += 1
            alternation["count"] += 1
            alternation["last"] = index
        else:
            steps = 2 if last_kind == "edit" else 1
            alternation = {"key": key, "command": command, "shown": shown, "steps": steps,
                           "count": 1, "first": index, "last": index}
        if alternation["steps"] >= ALTERNATION_STEPS:
            if "episode" not in alternation:
                alternation["episode"] = {
                    "pattern": "edit-check-alternation", "command": command, "result": shown,
                    "count": alternation["count"], "first_call": alternation["first"],
                    "last_call": index,
                }
                episodes.append(alternation["episode"])
            else:
                alternation["episode"].update(count=alternation["count"], last_call=index)
        last_kind = "check"
    return episodes


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
    episodes = stuck_episodes(tools, collect_results([transcript]), also)
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
        "stuck": bool(episodes),
        "stuck_episodes": episodes,
        "prices": {"read_on": table["read_on"], "source": table["source"]},
    }


def print_sessions(leases_path: Path, project: Path, as_json: bool, table: dict) -> int:
    """Print the session table; exit 1 naming each lease row with no transcript."""
    if not project.is_dir():
        print(f"error: no project folder at {project}", file=sys.stderr)
        return 2
    try:
        leases = read_leases(leases_path)
    except (OSError, ValueError) as error:
        print(f"error: cannot read the lease table at {leases_path}: {error}", file=sys.stderr)
        return 2
    rows, missing = session_table(leases, project, table)
    if as_json:
        sys.stdout.write(json.dumps(rows, indent=2, sort_keys=True) + "\n")
    else:
        sys.stdout.write(session_markdown(rows))
    for line in missing:
        print(f"error: {line}", file=sys.stderr)
    return 1 if missing else 0


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
        help="instead of one transcript: each model's median priced-over-recorded ratio "
        "over a project's finished sessions",
    )
    parser.add_argument(
        "--last", type=int, default=20,
        help="with --match-rate: how many of the most recent sessions to read (default 20)",
    )
    parser.add_argument(
        "--sessions", type=Path, default=None, metavar="LEASES_MD",
        help="instead of one transcript: the allocation log's session table, one row per "
        "session the lease table's attempts ran in (needs --project)",
    )
    parser.add_argument(
        "--project", type=Path, default=None, metavar="PROJECT_DIR",
        help="with --sessions: the project folder holding the attempts' transcripts",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="with --sessions: print the rows as JSON instead of Markdown",
    )
    args = parser.parse_args(argv)

    modes = [args.transcript, args.match_rate, args.sessions]
    if sum(mode is not None for mode in modes) != 1:
        parser.error("give one of a transcript, --match-rate PROJECT_DIR or --sessions LEASES_MD")
    if (args.sessions is None) != (args.project is None):
        parser.error("--sessions and --project go together")
    if args.json and args.sessions is None:
        parser.error("--json goes with --sessions")
    table = json.loads(PRICES.read_text(encoding="utf-8"))
    if args.sessions is not None:
        return print_sessions(args.sessions, args.project, args.json, table)
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
