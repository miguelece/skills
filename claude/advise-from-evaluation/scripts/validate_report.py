"""Validate an evaluation report against `references/report.schema.yaml`.

    python scripts/validate_report.py <report.json>

Prints one problem per line, each naming the field path and the value found,
and exits 0 when the report is valid, 1 when it has problems, and 2 when the
file cannot be read or is not JSON.

The schema is YAML documentation, and this script imports only the standard
library, so it has no YAML parser. It therefore holds the schema's validating
keys -- `type`, `required`, `enum`, `values`, `fields`, `items` -- and its
`enums:` as constants below, and implements each rule of the schema's `rules:`
list in the schema's order. The skill's authoring repository pins these
constants and rule ids against the schema, so the two cannot drift apart.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable


# --------------------------------------------------------------------------
# The schema's constants: `enums:` and the `report:` tree, without the keys
# that only explain a field to a reader.
# --------------------------------------------------------------------------

ENUMS: dict[str, list[str]] = {
    "input-kind": ["diff", "repository", "design-from-code", "design-document"],
    "phase": ["static", "dynamic"],
    "severity": ["critical", "high", "medium", "low", "info"],
    "confidence": ["high", "medium", "low"],
}


def _string(required: bool, **extra: Any) -> dict:
    return {"type": "string", "required": required, **extra}


_PHASE_LIST = {"type": "list", "required": True, "items": {"type": "string", "enum": "phase"}}

_MODULE_ENTRY = {
    "type": "mapping",
    "fields": {"id": _string(True), "reason": _string(True)},
}

REPORT: dict = {
    "type": "mapping",
    "fields": {
        "schema-version": {"type": "integer", "required": True, "values": [1]},
        "input": {
            "type": "mapping",
            "required": True,
            "fields": {
                "kind": _string(True, enum="input-kind"),
                "scope": _string(True),
                "excluded": {
                    "type": "list",
                    "required": False,
                    "items": {"type": "string"},
                },
            },
        },
        "phases": {
            "type": "mapping",
            "required": True,
            "fields": {
                "requested": _PHASE_LIST,
                "run": _PHASE_LIST,
                "not-run": {
                    "type": "list",
                    "required": True,
                    "items": {
                        "type": "mapping",
                        "fields": {
                            "phase": _string(True, enum="phase"),
                            "reason": _string(True),
                        },
                    },
                },
            },
        },
        "modules": {
            "type": "mapping",
            "required": True,
            "fields": {
                "loaded": {"type": "list", "required": True, "items": _MODULE_ENTRY},
                "skipped": {"type": "list", "required": True, "items": _MODULE_ENTRY},
            },
        },
        "dynamic": {
            "type": "mapping",
            "required": True,
            "fields": {
                "started": {
                    "type": "list",
                    "required": True,
                    "items": {
                        "type": "mapping",
                        "fields": {
                            "target": _string(True),
                            "command": _string(True),
                            "ready": _string(False),
                        },
                    },
                },
            },
        },
        "findings": {
            "type": "list",
            "required": True,
            "items": {
                "type": "mapping",
                "fields": {
                    "module": _string(True),
                    "check": _string(True),
                    "phase": _string(True, enum="phase"),
                    "location": {
                        "type": "mapping",
                        "required": True,
                        "fields": {
                            "file": _string(False),
                            "symbol": _string(False),
                            "line": {"type": "integer", "required": False},
                            "section": _string(False),
                        },
                    },
                    "evidence": _string(True),
                    "severity": _string(True, enum="severity"),
                    "confidence": _string(True, enum="confidence"),
                    "dynamic": {
                        "type": "mapping",
                        "required": False,
                        "fields": {
                            "command": _string(True),
                            "observed": _string(True),
                            "expected": _string(True),
                        },
                    },
                },
            },
        },
    },
}


# --------------------------------------------------------------------------
# The structural pass, driven by the tree above
# --------------------------------------------------------------------------

TYPES: dict[str, Callable[[Any], bool]] = {
    "mapping": lambda value: isinstance(value, dict),
    "list": lambda value: isinstance(value, list),
    "string": lambda value: isinstance(value, str),
    "integer": lambda value: isinstance(value, int) and not isinstance(value, bool),
}

JSON_NAMES = {
    dict: "object",
    list: "array",
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    type(None): "null",
}


def _shown(value: Any) -> str:
    """A value as the report holds it, short enough for one line."""
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= 60 else text[:57] + "..."


def structural_problems(
    value: Any, spec: dict = REPORT, where: str = "report"
) -> list[str]:
    kind = spec["type"]
    if not TYPES[kind](value):
        found = JSON_NAMES.get(type(value), type(value).__name__)
        return [f"{where}: expected {kind}, found {found} {_shown(value)}"]
    problems: list[str] = []
    if "enum" in spec and value not in ENUMS[spec["enum"]]:
        problems.append(
            f"{where}: {value!r} is not one of {spec['enum']} {ENUMS[spec['enum']]}"
        )
    if "values" in spec and value not in spec["values"]:
        problems.append(f"{where}: {value!r} is not one of {spec['values']}")
    if kind == "mapping" and "fields" in spec:
        for name in sorted(set(value) - set(spec["fields"])):
            problems.append(
                f"{where}.{name}: the schema defines no such field, found {_shown(value[name])}"
            )
        for name, field in spec["fields"].items():
            child = f"{where}.{name}"
            if name not in value or value[name] is None:
                if field.get("required"):
                    found = "null" if name in value else "nothing"
                    problems.append(f"{child}: required, found {found}")
                continue
            problems += structural_problems(value[name], field, child)
    if kind == "list" and "items" in spec:
        for number, item in enumerate(value):
            problems += structural_problems(item, spec["items"], f"{where}[{number}]")
    return problems


# --------------------------------------------------------------------------
# The cross-field rules, one per entry of the schema's `rules:` list
# --------------------------------------------------------------------------


def _mapping(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list:
    return value if isinstance(value, list) else []


def _findings(report: dict) -> list[tuple[int, dict]]:
    return [
        (number, finding)
        for number, finding in enumerate(_list(report.get("findings")))
        if isinstance(finding, dict)
    ]


def _phases_run(report: dict) -> list:
    return _list(_mapping(report.get("phases")).get("run"))


def run_within_requested(report: dict) -> list[str]:
    phases = _mapping(report.get("phases"))
    requested = _list(phases.get("requested"))
    return [
        f"report.phases.run[{number}]: {phase!r} was run but not in phases.requested"
        for number, phase in enumerate(_list(phases.get("run")))
        if phase not in requested
    ]


def not_run_is_requested_minus_run(report: dict) -> list[str]:
    phases = _mapping(report.get("phases"))
    run = _list(phases.get("run"))
    unrun = [phase for phase in _list(phases.get("requested")) if phase not in run]
    listed = [
        entry.get("phase")
        for entry in _list(phases.get("not-run"))
        if isinstance(entry, dict) and "phase" in entry
    ]
    problems = [
        f"report.phases.not-run: {phase!r} was requested and not run, but is not "
        "in phases.not-run"
        for phase in unrun
        if phase not in listed
    ]
    seen: set = set()
    for number, phase in enumerate(listed):
        if phase not in unrun:
            problems.append(
                f"report.phases.not-run[{number}].phase: {phase!r} is not a requested "
                "phase that did not run"
            )
        elif phase in seen:
            problems.append(
                f"report.phases.not-run[{number}].phase: {phase!r} is listed more than once"
            )
        seen.add(phase)
    return problems


def module_accounted_once(report: dict) -> list[str]:
    modules = _mapping(report.get("modules"))
    seen: set = set()
    problems = []
    for group in ("loaded", "skipped"):
        for number, entry in enumerate(_list(modules.get(group))):
            if not isinstance(entry, dict):
                continue
            module = entry.get("id")
            if module in seen:
                problems.append(
                    f"report.modules.{group}[{number}].id: {module!r} is listed more than once"
                )
            seen.add(module)
    return problems


def finding_phase_was_run(report: dict) -> list[str]:
    run = _phases_run(report)
    return [
        f"report.findings[{number}].phase: {finding.get('phase')!r} is not in phases.run {run}"
        for number, finding in _findings(report)
        if finding.get("phase") not in run
    ]


def finding_module_was_loaded(report: dict) -> list[str]:
    loaded = {
        entry.get("id")
        for entry in _list(_mapping(report.get("modules")).get("loaded"))
        if isinstance(entry, dict)
    }
    return [
        f"report.findings[{number}].module: {finding.get('module')!r} is not in modules.loaded"
        for number, finding in _findings(report)
        if finding.get("module") not in loaded
    ]


def finding_check_belongs_to_its_module(report: dict) -> list[str]:
    return [
        f"report.findings[{number}].check: {finding.get('check')!r} does not start with "
        f"{str(finding.get('module')) + '/'!r}"
        for number, finding in _findings(report)
        if not str(finding.get("check", "")).startswith(f"{finding.get('module')}/")
    ]


def location_names_a_file_or_a_section(report: dict) -> list[str]:
    problems = []
    for number, finding in _findings(report):
        location = finding.get("location")
        if not isinstance(location, dict):
            continue
        has_file = bool(location.get("file"))
        has_section = bool(location.get("section"))
        if has_file == has_section:
            problems.append(
                f"report.findings[{number}].location: {_shown(location)} must name a "
                "file or a section, not both"
            )
    return problems


def dynamic_fields_empty_in_a_static_run(report: dict) -> list[str]:
    if "dynamic" in _phases_run(report):
        return []
    problems = []
    for name, value in _mapping(report.get("dynamic")).items():
        if value not in (None, [], "", {}):
            problems.append(
                f"report.dynamic.{name}: {_shown(value)} must be empty when "
                "dynamic is not in phases.run"
            )
    for number, finding in _findings(report):
        if finding.get("dynamic") not in (None, {}):
            problems.append(
                f"report.findings[{number}].dynamic: {_shown(finding['dynamic'])} must "
                "be empty when dynamic is not in phases.run"
            )
    return problems


CROSS_FIELD_RULES: dict[str, Callable[[dict], list[str]]] = {
    "run-within-requested": run_within_requested,
    "not-run-is-requested-minus-run": not_run_is_requested_minus_run,
    "module-accounted-once": module_accounted_once,
    "finding-phase-was-run": finding_phase_was_run,
    "finding-module-was-loaded": finding_module_was_loaded,
    "finding-check-belongs-to-its-module": finding_check_belongs_to_its_module,
    "location-names-a-file-or-a-section": location_names_a_file_or_a_section,
    "dynamic-fields-empty-in-a-static-run": dynamic_fields_empty_in_a_static_run,
}


def report_problems(report: Any) -> list[str]:
    """Every problem with a parsed report: the structural pass, then each rule."""
    problems = structural_problems(report)
    if isinstance(report, dict):
        for rule in CROSS_FIELD_RULES.values():
            problems += rule(report)
    return problems


# --------------------------------------------------------------------------
# The command line
# --------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python scripts/validate_report.py <report.json>", file=sys.stderr)
        return 2
    path = Path(argv[0])
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as error:
        print(f"{path}: cannot be read: {error}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as error:
        print(f"{path}: is not JSON: {error}", file=sys.stderr)
        return 2
    problems = report_problems(report)
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
