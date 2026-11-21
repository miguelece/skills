#!/usr/bin/env python3
"""Name the one path a capture may be written to in a research base.

    scripts/capture_path.py --base <base> --slug <slug>
    scripts/capture_path.py --base <base> --slug <slug> --date 2026-11-21

Prints `<base>/<private layer>/<date>-<slug>.md` and writes nothing; the agent
writes the capture there. A capture may quote another repository's private
material, so it is raw input, and raw input is never committed. The path is
therefore named only inside the private layer, and only when git agrees it is
private:

- the layer is the one `base.json` declares untracked with kind `source`, read
  through `validate_base.py`'s `read_layers`; none is `private-layer-missing`,
  more than one is `private-layer-ambiguous`, never a guess between them;
- git must ignore the path (`git check-ignore`), so a layer declared untracked
  whose ignore rule is missing, or a base outside a repository, is
  `capture-not-ignored`: the declaration is a claim, the ignore rule is what
  keeps the file out of a commit;
- the slug is kebab-case and the date is `YYYY-MM-DD`, so neither can lead out
  of the layer (`slug-invalid`, `date-invalid`);
- an existing capture is never overwritten (`capture-exists`).

Every refusal exits 2 and prints `[<rule>] <reason>`; the date defaults to
today.
"""

from __future__ import annotations

import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

from validate_base import DATE, read_layers

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class Refused(Exception):
    def __init__(self, rule: str, reason: str) -> None:
        super().__init__(f"[{rule}] {reason}")


def private_layer(base: Path) -> str:
    layers, findings = read_layers(base)
    if layers is None:
        _, rule, reason = findings[0]
        raise Refused(rule, reason)
    private = sorted(
        directory for directory, layer in layers.items()
        if not layer["tracked"] and layer["kind"] == "source"
    )
    if not private:
        raise Refused("private-layer-missing",
                      "base.json declares no untracked layer of kind `source`")
    if len(private) > 1:
        raise Refused("private-layer-ambiguous",
                      f"base.json declares several private source layers: {private}")
    return private[0]


def capture_path(base: Path, slug: str, date: str) -> Path:
    if not SLUG.match(slug):
        raise Refused("slug-invalid", f"{slug!r} is not a kebab-case slug")
    if not DATE.match(date):
        raise Refused("date-invalid", f"{date!r} is not YYYY-MM-DD")
    path = base.resolve() / private_layer(base) / f"{date}-{slug}.md"
    ignored = subprocess.run(
        ["git", "-C", str(base.resolve()), "check-ignore", "-q", str(path)],
        capture_output=True, check=False,
    )
    if ignored.returncode != 0:
        raise Refused("capture-not-ignored",
                      f"git does not ignore {path.name} in the private layer")
    if path.exists():
        raise Refused("capture-exists", f"{path.name} exists; choose another slug")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", type=Path, required=True,
                        help="the research base that receives the capture")
    parser.add_argument("--slug", required=True, help="the capture's kebab-case slug")
    parser.add_argument("--date", default=datetime.date.today().isoformat(),
                        help="the capture's date, YYYY-MM-DD; today by default")
    args = parser.parse_args(argv)
    try:
        print(capture_path(args.base, args.slug, args.date).as_posix())
    except Refused as refusal:
        print(refusal)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
