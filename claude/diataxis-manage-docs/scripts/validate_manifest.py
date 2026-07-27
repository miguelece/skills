#!/usr/bin/env python3
"""Validate a lifecycle manifest with the bundled YAML schema subset."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

import yaml


TYPE_CHECKS = {
    "array": lambda value: isinstance(value, list),
    "boolean": lambda value: isinstance(value, bool),
    "integer": lambda value: isinstance(value, int) and not isinstance(value, bool),
    "null": lambda value: value is None,
    "number": lambda value: (
        isinstance(value, (int, float)) and not isinstance(value, bool)
    ),
    "object": lambda value: isinstance(value, dict),
    "string": lambda value: isinstance(value, str),
}
FINGERPRINT_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
PORTABLE_INVALID_CHARS = re.compile(r'[<>:"|?*\x00-\x1f]')
OPEN_FINDING_STATUSES = {"blocked", "blocking", "open", "unresolved"}
WINDOWS_RESERVED_NAMES = {
    "AUX",
    "CON",
    "NUL",
    "PRN",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def construct_unique_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate mapping key: {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_unique_mapping,
)


def load_yaml(path: Path) -> Any:
    try:
        return yaml.load(
            path.read_text(encoding="utf-8", errors="strict"),
            Loader=UniqueKeyLoader,
        )
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        raise ValueError(f"{path}: cannot read YAML: {error}") from error


def display_path(parts: tuple[object, ...]) -> str:
    if not parts:
        return "$"
    rendered = "$"
    for part in parts:
        rendered += f"[{part}]" if isinstance(part, int) else f".{part}"
    return rendered


def validate(
    value: Any,
    schema: dict[str, Any],
    parts: tuple[object, ...] = (),
) -> list[str]:
    errors: list[str] = []
    expected = schema.get("type")
    expected_types = [expected] if isinstance(expected, str) else expected

    if expected_types:
        known = [item for item in expected_types if item in TYPE_CHECKS]
        if len(known) != len(expected_types):
            unknown = sorted(set(expected_types) - set(known))
            return [f"{display_path(parts)}: unsupported schema types {unknown}"]
        if not any(TYPE_CHECKS[item](value) for item in expected_types):
            actual = type(value).__name__
            return [
                f"{display_path(parts)}: expected {' or '.join(expected_types)}, "
                f"got {actual}"
            ]

    if value is None:
        return errors

    if "enum" in schema and value not in schema["enum"]:
        errors.append(
            f"{display_path(parts)}: {value!r} is not one of {schema['enum']!r}"
        )

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{display_path(parts)}: string is too short")
        pattern = schema.get("pattern")
        if pattern and re.search(pattern, value) is None:
            errors.append(
                f"{display_path(parts)}: {value!r} does not match {pattern!r}"
            )

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(
                f"{display_path(parts)}: {value} is below {schema['minimum']}"
            )

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{display_path(parts)}: array has too few items")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                errors.extend(validate(item, item_schema, (*parts, index)))

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for name in required:
            if name not in value:
                errors.append(f"{display_path((*parts, name))}: required field missing")
        if schema.get("additionalProperties") is False:
            for name in sorted(set(value) - set(properties)):
                errors.append(
                    f"{display_path((*parts, name))}: additional property not allowed"
                )
        for name in sorted(set(value) & set(properties)):
            errors.extend(validate(value[name], properties[name], (*parts, name)))

    return errors


def portable_path_error(value: Any, label: str) -> str | None:
    if not isinstance(value, str) or not value or value != value.strip():
        return f"{label}: path must be a nonempty trimmed string"
    if "\\" in value:
        normalized = value.replace("\\", "/")
    else:
        normalized = value
    posix = PurePosixPath(normalized)
    windows = PureWindowsPath(value)
    if (
        posix.is_absolute()
        or windows.is_absolute()
        or windows.drive
        or normalized.startswith("/")
    ):
        return f"{label}: path must be repository-relative"
    if "//" in normalized or any(part in {"", ".", ".."} for part in posix.parts):
        return f"{label}: path must not contain empty, dot, or traversal segments"
    for part in posix.parts:
        if PORTABLE_INVALID_CHARS.search(part):
            return f"{label}: path contains nonportable characters"
        if part.endswith((" ", ".")):
            return f"{label}: path segment cannot end with a space or dot"
        if part.split(".", 1)[0].upper() in WINDOWS_RESERVED_NAMES:
            return f"{label}: path uses a reserved Windows name"
    return None


def require_portable_paths(
    values: Any,
    label: str,
    errors: list[str],
) -> None:
    if not isinstance(values, list):
        return
    for index, value in enumerate(values):
        problem = portable_path_error(value, f"{label}[{index}]")
        if problem:
            errors.append(problem)


def semantic_validate(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    run = manifest["run"]
    repository = manifest["repository"]
    scope = manifest["scope"]
    policies = manifest["approved_policies"]
    ledger = manifest["section_ledger"]
    archive = manifest["archive"]

    problem = portable_path_error(scope["docs_domain"], "$.scope.docs_domain")
    if problem:
        errors.append(problem)
    require_portable_paths(
        scope.get("excluded_paths", []),
        "$.scope.excluded_paths",
        errors,
    )
    require_portable_paths(
        repository.get("dirty_paths", []),
        "$.repository.dirty_paths",
        errors,
    )

    for index, entry in enumerate(ledger):
        label = f"$.section_ledger[{index}]"
        problem = portable_path_error(entry["source_path"], f"{label}.source_path")
        if problem:
            errors.append(problem)
        fingerprint = entry["source_fingerprint"]
        if not isinstance(fingerprint, str) or not FINGERPRINT_PATTERN.fullmatch(
            fingerprint
        ):
            errors.append(f"{label}.source_fingerprint: invalid SHA-256 fingerprint")
        disposition = entry["disposition"]
        destination = entry.get("destination_path")
        if destination is not None:
            problem = portable_path_error(destination, f"{label}.destination_path")
            if problem:
                errors.append(problem)
        if disposition == "migrated" and not (
            isinstance(destination, str) and destination.strip()
        ):
            errors.append(
                f"{label}: migrated disposition requires destination_path"
            )
        reason = entry.get("notes") or entry.get("reason")
        if disposition in {"retired", "blocked"} and not (
            isinstance(reason, str) and reason.strip()
        ):
            errors.append(
                f"{label}: {disposition} disposition requires nonempty notes or reason"
            )

    archive_path = archive["path"]
    if archive_path is not None:
        problem = portable_path_error(archive_path, "$.archive.path")
        if problem:
            errors.append(problem)
    archive_status = archive["status"]
    if archive_status in {"created", "retained"} and not (
        isinstance(archive_path, str) and archive_path.strip()
    ):
        errors.append(f"$.archive: {archive_status} status requires archive.path")
    if archive_status == "not_created" and archive_path is not None:
        errors.append("$.archive: not_created status requires a null archive.path")
    if archive_status == "deleted":
        if archive_path is not None:
            errors.append("$.archive: deleted status requires a null archive.path")
        if policies.get("archive_deletion_approved") is not True:
            errors.append(
                "$.approved_policies.archive_deletion_approved: "
                "archive deletion requires explicit deletion approval"
            )

    if run["status"] == "complete":
        required_strings = (
            ("$.run.id", run.get("id")),
            ("$.run.started_at", run.get("started_at")),
            ("$.run.completed_at", run.get("completed_at")),
            ("$.repository.baseline_revision", repository.get("baseline_revision")),
            ("$.repository.current_revision", repository.get("current_revision")),
        )
        for label, value in required_strings:
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}: complete status requires a nonempty value")
        if policies.get("write_approved") is not True:
            errors.append(
                "$.approved_policies.write_approved: complete status requires true"
            )
        if not isinstance(policies.get("approved_plan"), str) or not policies[
            "approved_plan"
        ].strip():
            errors.append(
                "$.approved_policies.approved_plan: complete status requires "
                "a nonempty approved plan path"
            )
        if not manifest["evidence"]:
            errors.append("$.evidence: complete status requires nonempty evidence")
        if not manifest["verification"]:
            errors.append(
                "$.verification: complete status requires nonempty verification"
            )
        for index, verification in enumerate(manifest["verification"]):
            status = (
                str(verification.get("status", "")).strip().lower()
                if isinstance(verification, dict)
                else ""
            )
            if status not in {"pass", "passed", "success", "successful"}:
                errors.append(
                    f"$.verification[{index}]: complete status requires a "
                    f"successful verification result, got {status or 'missing'}"
                )
        if run.get("mode") == "migrate":
            if not ledger:
                errors.append(
                    "$.section_ledger: complete migration requires section records"
                )
            if archive_status not in {"created", "retained"}:
                errors.append(
                    "$.archive: complete migration requires a created or retained archive"
                )
        for index, finding in enumerate(manifest["findings"]):
            status = str(finding.get("status", "")).strip().lower()
            if (
                finding.get("blocking") is True
                or finding.get("resolved") is False
                or status in OPEN_FINDING_STATUSES
            ):
                errors.append(
                    f"$.findings[{index}]: complete status cannot contain "
                    "open or blocking findings"
                )

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a .docs-migration lifecycle manifest."
    )
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        schema = load_yaml(args.schema)
        manifest = load_yaml(args.manifest)
        if not isinstance(schema, dict):
            raise ValueError(f"{args.schema}: schema root must be an object")
        errors = validate(manifest, schema)
        if not errors and isinstance(manifest, dict):
            errors.extend(semantic_validate(manifest))
    except ValueError as error:
        errors = [str(error)]

    payload = {
        "valid": not errors,
        "manifest": str(args.manifest),
        "errors": errors,
    }
    if args.as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif errors:
        print(f"Manifest is invalid: {args.manifest}")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"Manifest is valid: {args.manifest}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
