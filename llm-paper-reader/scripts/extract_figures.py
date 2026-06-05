#!/usr/bin/env python3
"""Extract candidate paper figures and metadata from a PDF."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


CAPTION_RE = re.compile(
    r"^\s*(?P<label>Fig(?:ure)?\.?)\s*(?P<number>[A-Za-z0-9][A-Za-z0-9.\-]*)\s*[:.\-]?\s*(?P<caption>.*)$",
    re.IGNORECASE,
)


def fail(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def require_fitz() -> Any:
    try:
        import fitz  # type: ignore
    except ImportError:
        fail(
            "extract_figures.py requires PyMuPDF. Install it with "
            "`python3 -m pip install pymupdf`."
        )
    return fitz


def clean_filename(value: str) -> str:
    value = value.lower().replace(".", "")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "figure"


def likely_type(caption: str) -> str:
    text = caption.lower()
    checks = [
        ("architecture", ("architecture", "framework", "overview", "module", "transformer", "attention", "network")),
        ("training", ("training", "train", "pretrain", "fine-tune", "finetune", "optimization", "loss", "rlhf", "preference")),
        ("inference", ("inference", "decoding", "generation", "serving", "sampling")),
        ("data-flow", ("data", "dataset", "pipeline", "construction", "retrieval", "corpus")),
        ("system", ("system", "deployment", "latency", "throughput", "memory", "cache")),
        ("evaluation", ("benchmark", "result", "performance", "comparison", "qualitative", "case study")),
    ]
    for label, keywords in checks:
        if any(keyword in text for keyword in keywords):
            return label
    return "figure"


def page_captions(text: str) -> list[dict[str, str]]:
    captions: list[dict[str, str]] = []
    lines = [line.rstrip() for line in text.splitlines()]
    index = 0
    while index < len(lines):
        match = CAPTION_RE.match(lines[index])
        if not match:
            index += 1
            continue

        figure_id = f"Fig. {match.group('number')}"
        caption_parts = [match.group("caption").strip()]
        lookahead = index + 1
        while lookahead < len(lines):
            candidate = lines[lookahead].strip()
            if not candidate:
                break
            if CAPTION_RE.match(candidate) or re.match(r"^(Table|Algorithm)\s+", candidate, re.IGNORECASE):
                break
            if len(" ".join(caption_parts + [candidate])) > 600:
                break
            caption_parts.append(candidate)
            lookahead += 1

        caption = " ".join(part for part in caption_parts if part).strip()
        captions.append(
            {
                "figure_id": figure_id,
                "caption": caption,
                "likely_type": likely_type(caption),
            }
        )
        index = max(lookahead, index + 1)
    return captions


def save_pixmap_as_png(fitz: Any, doc: Any, xref: int, image_path: Path) -> tuple[int, int]:
    pix = fitz.Pixmap(doc, xref)
    try:
        if pix.n - pix.alpha >= 4:
            converted = fitz.Pixmap(fitz.csRGB, pix)
            pix = converted
        image_path.parent.mkdir(parents=True, exist_ok=True)
        pix.save(str(image_path))
        return pix.width, pix.height
    finally:
        pix = None


def render_page(fitz: Any, page: Any, image_path: Path, zoom: float) -> tuple[int, int]:
    matrix = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=matrix, alpha=False)
    image_path.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(image_path))
    return pix.width, pix.height


def extract_figures(
    pdf_path: Path,
    out_dir: Path,
    metadata_path: Path,
    min_width: int,
    min_height: int,
    render_caption_pages: bool,
    render_zoom: float,
) -> list[dict[str, Any]]:
    fitz = require_fitz()
    records: list[dict[str, Any]] = []

    with fitz.open(pdf_path) as doc:
        for page_index, page in enumerate(doc, start=1):
            text = page.get_text("text", sort=True)
            captions = page_captions(text)
            caption = captions[0] if captions else {}
            page_records = 0

            for image_index, image_info in enumerate(page.get_images(full=True), start=1):
                xref = image_info[0]
                base_info = doc.extract_image(xref)
                width = int(base_info.get("width") or 0)
                height = int(base_info.get("height") or 0)
                if width < min_width or height < min_height:
                    continue

                figure_id = caption.get("figure_id") or f"image-{page_index}-{image_index}"
                filename = f"page_{page_index:03d}_{clean_filename(figure_id)}_{image_index}.png"
                image_path = out_dir / filename
                saved_width, saved_height = save_pixmap_as_png(fitz, doc, xref, image_path)
                records.append(
                    {
                        "figure_id": figure_id,
                        "page": page_index,
                        "image_path": str(image_path),
                        "caption": caption.get("caption", ""),
                        "likely_type": caption.get("likely_type") or likely_type(caption.get("caption", "")),
                        "extraction_method": "embedded_image",
                        "width": saved_width,
                        "height": saved_height,
                    }
                )
                page_records += 1

            if render_caption_pages and captions and page_records == 0:
                for caption_index, caption in enumerate(captions, start=1):
                    figure_id = caption["figure_id"]
                    filename = f"page_{page_index:03d}_{clean_filename(figure_id)}_candidate.png"
                    image_path = out_dir / filename
                    saved_width, saved_height = render_page(fitz, page, image_path, render_zoom)
                    records.append(
                        {
                            "figure_id": figure_id,
                            "page": page_index,
                            "image_path": str(image_path),
                            "caption": caption["caption"],
                            "likely_type": caption["likely_type"],
                            "extraction_method": "page_render_candidate",
                            "width": saved_width,
                            "height": saved_height,
                        }
                    )

    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract candidate paper figures and metadata from a PDF.",
    )
    parser.add_argument("paper_pdf", help="Path to the input paper PDF")
    parser.add_argument(
        "--out-dir",
        default="figures",
        help="Directory for extracted figure images (default: figures)",
    )
    parser.add_argument(
        "--metadata",
        default="figures/metadata.json",
        help="Output metadata JSON path (default: figures/metadata.json)",
    )
    parser.add_argument("--min-width", type=int, default=120, help="Minimum embedded image width")
    parser.add_argument("--min-height", type=int, default=120, help="Minimum embedded image height")
    parser.add_argument(
        "--no-render-caption-pages",
        action="store_true",
        help="Disable full-page rendering for pages with figure captions but no embedded image",
    )
    parser.add_argument("--render-zoom", type=float, default=2.0, help="Zoom for caption page renders")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pdf_path = Path(args.paper_pdf)
    if not pdf_path.exists():
        fail(f"input PDF not found: {pdf_path}")
    if not pdf_path.is_file():
        fail(f"input path is not a file: {pdf_path}")

    records = extract_figures(
        pdf_path=pdf_path,
        out_dir=Path(args.out_dir),
        metadata_path=Path(args.metadata),
        min_width=args.min_width,
        min_height=args.min_height,
        render_caption_pages=not args.no_render_caption_pages,
        render_zoom=args.render_zoom,
    )
    print(f"wrote {len(records)} figure candidates to {args.out_dir}")
    print(f"wrote metadata to {args.metadata}")


if __name__ == "__main__":
    main()
