#!/usr/bin/env python3
"""Audit a generated paper report for common depth and visual-quality failures."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


IMAGE_RE = re.compile(r"!\[[^\]]*]\((?P<path>[^)\s]+)(?:\s+\"[^\"]*\")?\)")
CODE_RE = re.compile(r"```(?P<lang>[^\n]*)\n(?P<body>.*?)```", re.DOTALL)
FORMULA_RE = re.compile(r"\$\$(?P<body>.*?)\$\$", re.DOTALL)
UNSAFE_METHODS = {
    "page_render_candidate",
    "full_page_fallback",
    "full_page_fallback_do_not_embed",
    "embedded_full_page_do_not_embed",
}
CRITICAL_MECHANISMS = {
    "routing": ("router", "routing", "路由"),
    "retrieval": ("retrieve", "retrieval", "检索"),
    "attention": ("attention", "注意力"),
    "sampling": ("sampling", "sample", "采样"),
    "reranking": ("rerank", "reranking", "重排序"),
    "memory update": ("memory update", "更新记忆", "记忆更新"),
}
CALL_RE = re.compile(r"\b(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\(")
CRITICAL_NAME_RE = re.compile(
    r"router|routing|route|retrieve|rerank|select|sample|similarity|score|"
    r"attention|memory_update|paper_loss",
    re.IGNORECASE,
)
DEF_RE = re.compile(r"\bdef\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\(")


def fail(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def load_metadata(paths: list[Path]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for path in paths:
        if not path.exists():
            fail(f"metadata file not found: {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            fail(f"could not read metadata file {path}: {exc}")
        if not isinstance(data, list):
            fail(f"metadata must be a JSON list: {path}")
        for record in data:
            if not isinstance(record, dict) or not record.get("image_path"):
                continue
            image_path = Path(str(record["image_path"]))
            records[image_path.name] = record
            records[str(image_path)] = record
    return records


def visible_text_length(text: str) -> int:
    text = re.sub(r"`[^`]*`", "", text)
    text = re.sub(r"\s+", "", text)
    return len(text)


def audit_images(
    report_path: Path,
    report_text: str,
    metadata: dict[str, dict[str, Any]],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for match in IMAGE_RE.finditer(report_text):
        raw_path = match.group("path")
        if re.match(r"^[a-z]+://", raw_path, re.IGNORECASE):
            continue
        image_path = Path(raw_path)
        resolved = image_path if image_path.is_absolute() else report_path.parent / image_path
        if not resolved.exists():
            errors.append(f"image does not exist: {raw_path}")

        record = metadata.get(str(image_path)) or metadata.get(image_path.name)
        if record is None:
            warnings.append(f"no extraction metadata found for image: {raw_path}")
            continue

        method = str(record.get("extraction_method", ""))
        if method in UNSAFE_METHODS or record.get("safe_to_embed") is False:
            errors.append(
                f"unsafe full-page/intermediate asset embedded: {raw_path} "
                f"(extraction_method={method})"
            )

    return errors, warnings


def audit_formula_depth(report_text: str) -> list[str]:
    warnings: list[str] = []
    formulas = list(FORMULA_RE.finditer(report_text))
    for index, match in enumerate(formulas, start=1):
        tail = report_text[match.end() :]
        next_heading = re.search(r"\n#{1,6}\s+", tail)
        next_formula = FORMULA_RE.search(tail)
        endpoints = [candidate.start() for candidate in (next_heading, next_formula) if candidate]
        explanation = tail[: min(endpoints)] if endpoints else tail[:1000]
        if visible_text_length(explanation) < 90:
            preview = re.sub(r"\s+", " ", match.group("body")).strip()[:70]
            warnings.append(
                f"formula {index} may lack calculation-level explanation after it: {preview}"
            )
    return warnings


def audit_mechanism_pseudocode(report_text: str) -> list[str]:
    warnings: list[str] = []
    lowered = report_text.lower()
    headings = "\n".join(re.findall(r"^#{1,6}\s+.*$", report_text, re.MULTILINE)).lower()
    formulas = "\n".join(match.group("body") for match in FORMULA_RE.finditer(report_text)).lower()
    code_blocks = [match.group("body") for match in CODE_RE.finditer(report_text)]
    code_lowered = "\n".join(code_blocks).lower()

    for label, keywords in CRITICAL_MECHANISMS.items():
        appears_repeatedly = sum(lowered.count(keyword.lower()) for keyword in keywords) >= 3
        appears_as_mechanism = any(
            keyword.lower() in headings or keyword.lower() in formulas for keyword in keywords
        )
        if appears_repeatedly and appears_as_mechanism and not any(
            keyword.lower() in code_lowered for keyword in keywords
        ):
            warnings.append(
                f"report discusses {label} but no pseudocode block visibly expands that mechanism"
            )

    definitions = {
        match.group("name").lower()
        for block in code_blocks
        for match in DEF_RE.finditer(block)
    }
    calls = {
        match.group("name").lower()
        for block in code_blocks
        for match in CALL_RE.finditer(block)
        if CRITICAL_NAME_RE.search(match.group("name"))
        and match.group("name").lower() not in definitions
    }
    for name in sorted(calls):
        warnings.append(
            f"critical-looking pseudocode call may be an unexplained black box: {name}(...)"
        )
    return warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit a paper report for shallow mechanisms/formulas and unsafe visuals.",
    )
    parser.add_argument("report", help="Path to the Markdown report")
    parser.add_argument(
        "--figures-metadata",
        action="append",
        default=[],
        help="Figure metadata JSON; may be passed multiple times",
    )
    parser.add_argument(
        "--tables-metadata",
        action="append",
        default=[],
        help="Table metadata JSON; may be passed multiple times",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report_path = Path(args.report)
    if not report_path.exists():
        fail(f"report not found: {report_path}")
    if not report_path.is_file():
        fail(f"report path is not a file: {report_path}")

    report_text = report_path.read_text(encoding="utf-8")
    metadata_paths = [Path(path) for path in args.figures_metadata + args.tables_metadata]
    metadata = load_metadata(metadata_paths)

    errors, image_warnings = audit_images(report_path, report_text, metadata)
    warnings = image_warnings + audit_formula_depth(report_text) + audit_mechanism_pseudocode(report_text)

    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARNING: {message}")

    print(f"audit complete: {len(errors)} error(s), {len(warnings)} warning(s)")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
