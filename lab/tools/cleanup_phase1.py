"""Validation primitives for the cleanup Phase 1 safety skeleton.

The module intentionally uses only the Python standard library.  Validators
return a list of human-readable errors; the command line exits non-zero when
that list is non-empty.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


COVERAGE_STATES = {
    "MANIFESTED",
    "POINTER_ONLY",
    "INACCESSIBLE",
    "MISSING",
    "EXCLUDED",
}
UPSTREAM_DISPOSITIONS = {"FILED", "ACCEPTED"}
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
UUID7_RE = re.compile(
    r"^db-ir-[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _load_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [], [f"{path}: cannot read: {exc}"]
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{number}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(row, dict):
            errors.append(f"{path}:{number}: row must be a JSON object")
            continue
        row["__line__"] = number
        rows.append(row)
    return rows, errors


def _missing(row: dict[str, Any], fields: Iterable[str]) -> list[str]:
    return [name for name in fields if row.get(name) in (None, "", [], {})]


def _valid_hash(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA256_RE.fullmatch(value))


def _safe_relative(value: Any) -> bool:
    """Return true for a normalized, workspace-relative POSIX-style path."""
    if not isinstance(value, str) or not value.strip():
        return False
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    return not path.is_absolute() and ".." not in path.parts and ":" not in path.parts[0]


def _anchors_valid(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for anchor in value:
        if not isinstance(anchor, dict):
            return False
        if _missing(anchor, ("source", "sha256", "locator")):
            return False
        if not _valid_hash(anchor.get("sha256")):
            return False
    return True


def validate_coverage_rows(rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    ids = {row.get("root_id") for row in rows if row.get("root_id")}
    for row in rows:
        label = f"root row {row.get('root_id') or row.get('__line__', '?')}"
        state = row.get("coverage_state")
        if state not in COVERAGE_STATES:
            errors.append(f"{label}: undeclared coverage_state {state!r}")
            continue
        if state == "MANIFESTED":
            if not _safe_relative(row.get("manifest_pointer")):
                errors.append(f"{label}: MANIFESTED requires a contained manifest_pointer")
            if not _valid_hash(row.get("manifest_sha256")):
                errors.append(f"{label}: MANIFESTED requires manifest_sha256")
        elif state == "POINTER_ONLY":
            if not _anchors_valid(row.get("evidence_anchors")):
                errors.append(f"{label}: POINTER_ONLY requires hashed evidence_anchors")
        else:
            if not row.get("limitations"):
                errors.append(f"{label}: {state} requires explicit limitations")
            if not row.get("observation_basis"):
                errors.append(f"{label}: {state} requires observation_basis")
        parent = row.get("parent_root_id")
        if parent and parent not in ids:
            errors.append(f"{label}: unknown parent_root_id {parent!r}")
    return errors


def validate_registry(path: Path) -> list[str]:
    rows, errors = _load_jsonl(path)
    required = (
        "root_id", "display_path", "host_kind", "path_kind", "primary_role",
        "authority_scope", "owner", "mutation_authority", "custody",
        "access", "observation_basis", "coverage_state", "scan_policy",
        "rights", "no_move_conditions", "limitations", "evidence_anchors",
    )
    seen: set[str] = set()
    for row in rows:
        label = f"{path}:{row.get('__line__', '?')}"
        missing = _missing(row, required)
        if missing:
            errors.append(f"{label}: missing required fields: {', '.join(missing)}")
        root_id = row.get("root_id")
        if root_id in seen:
            errors.append(f"{label}: duplicate root_id {root_id!r}")
        elif root_id:
            seen.add(root_id)
        if not _anchors_valid(row.get("evidence_anchors")):
            errors.append(f"{label}: evidence_anchors must contain source, sha256, and locator")
        canonical = row.get("canonical_entry")
        if canonical is not None and not _safe_relative(canonical):
            errors.append(f"{label}: canonical_entry escapes the workspace or is absolute")
    errors.extend(validate_coverage_rows(rows))
    if not rows:
        errors.append(f"{path}: registry contains no rows")
    return errors


def _receipt_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(p for p in path.glob("*.json") if p.is_file())


def validate_receipts(path: Path) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    files = _receipt_files(path)
    if not files:
        return [f"{path}: no JSON receipts found"]
    for receipt_path in files:
        try:
            row = json.loads(receipt_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{receipt_path}: cannot parse receipt: {exc}")
            continue
        if not isinstance(row, dict):
            errors.append(f"{receipt_path}: receipt must be a JSON object")
            continue
        receipt_id = row.get("receipt_id")
        if not UUID7_RE.fullmatch(receipt_id or ""):
            errors.append(f"{receipt_path}: receipt_id must be db-ir-<UUIDv7>")
        if receipt_id in seen:
            errors.append(f"{receipt_path}: duplicate receipt_id {receipt_id!r}")
        elif receipt_id:
            seen.add(receipt_id)
        missing = _missing(
            row,
            (
                "schema_version", "created_at", "owner", "artifact", "run",
                "use", "local_receipt", "canonicality", "owner_namespace",
            ),
        )
        if missing:
            errors.append(f"{receipt_path}: missing receipt facets: {', '.join(missing)}")
        if row.get("canonicality") != "NONCANONICAL_INTEGRATION_RECEIPT":
            errors.append(
                f"{receipt_path}: canonicality must be NONCANONICAL_INTEGRATION_RECEIPT"
            )
        if row.get("owner_namespace") != "daybreak":
            errors.append(f"{receipt_path}: owner_namespace must be 'daybreak'")
        if row.get("may_assign_upstream_status") is not False:
            errors.append(f"{receipt_path}: may_assign_upstream_status must be false")
        artifact = row.get("artifact")
        if isinstance(artifact, dict):
            if not _safe_relative(artifact.get("path")):
                errors.append(f"{receipt_path}: artifact.path must be contained and relative")
            if not _valid_hash(artifact.get("sha256")):
                errors.append(f"{receipt_path}: artifact.sha256 is missing or invalid")
        elif artifact is not None:
            errors.append(f"{receipt_path}: artifact must be an object")
        disposition = row.get("upstream_disposition")
        if disposition is not None:
            if not isinstance(disposition, dict):
                errors.append(f"{receipt_path}: upstream_disposition must be an object")
            elif disposition.get("state") in UPSTREAM_DISPOSITIONS:
                required = (
                    "upstream_entity_id", "authority_root_id", "authority_path",
                    "authority_sha256", "observed_at", "owner_assertion",
                )
                absent = _missing(disposition, required)
                if absent:
                    errors.append(
                        f"{receipt_path}: {disposition.get('state')} promotion lacks " + ", ".join(absent)
                    )
                if not _safe_relative(disposition.get("authority_path")):
                    errors.append(
                        f"{receipt_path}: disposition authority_path must be relative within authority_root_id"
                    )
                if not _valid_hash(disposition.get("authority_sha256")):
                    errors.append(f"{receipt_path}: disposition authority_sha256 is missing or invalid")
    return errors


def validate_questions(questions_path: Path, key_path: Path | None = None) -> list[str]:
    questions, errors = _load_jsonl(questions_path)
    qids: set[str] = set()
    for row in questions:
        label = f"{questions_path}:{row.get('__line__', '?')}"
        missing = _missing(row, ("question_id", "prompt", "category", "weight", "hard_case", "max_source_opens"))
        if missing:
            errors.append(f"{label}: missing question fields: {', '.join(missing)}")
        qid = row.get("question_id")
        if qid in qids:
            errors.append(f"{label}: duplicate question_id {qid!r}")
        elif qid:
            qids.add(qid)
        if not isinstance(row.get("weight"), (int, float)) or isinstance(row.get("weight"), bool) or row.get("weight", 0) <= 0:
            errors.append(f"{label}: weight must be positive")
        if not isinstance(row.get("max_source_opens"), int) or isinstance(row.get("max_source_opens"), bool) or row.get("max_source_opens", 0) < 1:
            errors.append(f"{label}: max_source_opens must be a positive integer")
        if not isinstance(row.get("hard_case"), bool):
            errors.append(f"{label}: hard_case must be boolean")
    if len(questions) != 24:
        errors.append(f"{questions_path}: expected exactly 24 questions, found {len(questions)}")
    if key_path is None:
        return errors
    keys, key_errors = _load_jsonl(key_path)
    errors.extend(key_errors)
    kids: set[str] = set()
    for row in keys:
        label = f"{key_path}:{row.get('__line__', '?')}"
        qid = row.get("question_id")
        if qid in kids:
            errors.append(f"{label}: duplicate answer question_id {qid!r}")
        elif qid:
            kids.add(qid)
        missing = _missing(row, ("question_id", "answer_elements"))
        if "accepted_variants" not in row:
            missing.append("accepted_variants")
        if missing:
            errors.append(f"{label}: missing answer-key fields: {', '.join(missing)}")
        elements = row.get("answer_elements")
        if not isinstance(elements, list) or not elements:
            errors.append(f"{label}: answer_elements must be a non-empty list")
        else:
            for index, element in enumerate(elements):
                if not isinstance(element, dict) or _missing(element, ("answer", "canonical_authority", "cutoff", "source_sha256", "locator")):
                    errors.append(f"{label}: answer_elements[{index}] lacks evidence fields")
                elif not _valid_hash(element.get("source_sha256")):
                    errors.append(f"{label}: answer_elements[{index}] source_sha256 is invalid")
    if qids != kids:
        errors.append(
            f"question/key ID mismatch: missing_in_key={sorted(qids-kids)!r}; extra_in_key={sorted(kids-qids)!r}"
        )
    return errors


def verify_freeze(manifest_path: Path, root: Path | None = None) -> list[str]:
    errors: list[str] = []
    root = (root or manifest_path.parent).resolve()
    try:
        lines = manifest_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [f"{manifest_path}: cannot read: {exc}"]
    seen: set[str] = set()
    count = 0
    for number, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([0-9a-fA-F]{64})\s+(?:\*)?(.+)", line.strip())
        if not match:
            errors.append(f"{manifest_path}:{number}: invalid freeze line")
            continue
        expected, relative = match.groups()
        relative = relative.replace("\\", "/")
        if not _safe_relative(relative):
            errors.append(f"{manifest_path}:{number}: frozen path escapes root: {relative!r}")
            continue
        if relative in seen:
            errors.append(f"{manifest_path}:{number}: duplicate frozen path {relative!r}")
            continue
        seen.add(relative)
        target = (root / relative).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            errors.append(f"{manifest_path}:{number}: resolved path escapes root: {relative!r}")
            continue
        if not target.is_file():
            errors.append(f"{manifest_path}:{number}: frozen file missing: {relative}")
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual.lower() != expected.lower():
            errors.append(f"{manifest_path}:{number}: hash mismatch for {relative}")
        count += 1
    if count == 0:
        errors.append(f"{manifest_path}: freeze contains no valid entries")
    return errors


def _print_result(errors: list[str]) -> int:
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2))
        return 1
    print(json.dumps({"ok": True, "errors": []}, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    reg = sub.add_parser("registry", help="validate a federated root registry JSONL")
    reg.add_argument("path", type=Path)
    rec = sub.add_parser("receipts", help="validate one receipt or a receipt directory")
    rec.add_argument("path", type=Path)
    cold = sub.add_parser("questions", help="validate question bank and optional answer key")
    cold.add_argument("questions", type=Path)
    cold.add_argument("--key", type=Path)
    freeze = sub.add_parser("freeze", help="verify SHA-256 freeze manifest")
    freeze.add_argument("manifest", type=Path)
    freeze.add_argument("--root", type=Path)
    coverage = sub.add_parser("coverage", help="validate registry coverage states")
    coverage.add_argument("path", type=Path)
    args = parser.parse_args(argv)

    if args.command == "registry":
        return _print_result(validate_registry(args.path))
    if args.command == "receipts":
        return _print_result(validate_receipts(args.path))
    if args.command == "questions":
        return _print_result(validate_questions(args.questions, args.key))
    if args.command == "freeze":
        return _print_result(verify_freeze(args.manifest, args.root))
    rows, errors = _load_jsonl(args.path)
    errors.extend(validate_coverage_rows(rows))
    return _print_result(errors)


if __name__ == "__main__":
    sys.exit(main())
