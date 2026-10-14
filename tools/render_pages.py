"""Render the Anthrogen zine into flipbook page images.

Usage:
    python3 tools/render_pages.py "anthro binder.pdf" "biological proof.pdf" [--dpi 300]

The interior comes from the binder (it has the 10 Sep revisions to pp. 8, 9,
27 and 47). Only the first page (the wraparound cover) is used from the
printer's proof, or from the standalone cover PDF.

Writes pages/01.webp ... pages/52.webp and pages/pages.js (the order the
viewer reads). Pages are cropped to the trim box, so no crop marks or bleed.

Book order (the viewer shows the first image alone on the right, then pairs):
    front cover | blank inside cover, p1 | p2, p3 | ... | p8, p9 |
    p12, p13 | p10, p11 | p14, p15 | ... | p48, blank inside cover | back cover
Spreads 12-13 and 10-11 are swapped back into reading order (Elena, 9 Oct 2026).
"""
import argparse
import json
from pathlib import Path

import pymupdf
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "pages"


def reading_order():
    pages = list(range(1, 10)) + [12, 13, 10, 11] + list(range(14, 49))
    assert sorted(pages) == list(range(1, 49))
    return (["front", "blank"] + pages + ["blank", "back"])


def render(page, clip, dpi):
    pix = page.get_pixmap(dpi=dpi, clip=clip, colorspace=pymupdf.csRGB, alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def trim(page):
    """The trim box in the page's own coordinates (which start at the crop box)."""
    box = page.trimbox
    if not (box.width > 0 and box != page.mediabox):
        return page.rect                      # no real trim box: use the crop box
    c = page.cropbox
    return pymupdf.Rect(box.x0 - c.x0, box.y0 - c.y0, box.x1 - c.x0, box.y1 - c.y0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("binder")
    ap.add_argument("cover")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--quality", type=int, default=84)
    a = ap.parse_args()

    binder = pymupdf.open(a.binder)
    assert binder.page_count == 48, f"expected 48 pages, got {binder.page_count}"

    interior = {}
    for i in range(48):
        pg = binder[i]
        interior[i + 1] = render(pg, trim(pg), a.dpi)
    size = interior[1].size

    cover_pg = pymupdf.open(a.cover)[0]
    t = trim(cover_pg)
    mid = (t.x0 + t.x1) / 2
    back = render(cover_pg, pymupdf.Rect(t.x0, t.y0, mid, t.y1), a.dpi)
    front = render(cover_pg, pymupdf.Rect(mid, t.y0, t.x1, t.y1), a.dpi)
    # The cover is a separate file; match it to the interior size exactly.
    back, front = (im.resize(size, Image.LANCZOS) for im in (back, front))
    blank = Image.new("RGB", size, "white")

    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.webp"):
        old.unlink()

    manifest = []
    for n, key in enumerate(reading_order(), start=1):
        im = {"front": front, "back": back, "blank": blank}.get(key) or interior[key]
        name = f"{n:02d}.webp"
        im.save(OUT / name, "WEBP", quality=a.quality, method=6)
        manifest.append({"src": f"pages/{name}", "page": key})

    (OUT / "pages.js").write_text(
        "window.ZINE_PAGES = " + json.dumps(manifest, indent=1) + ";\n")
    total = sum(f.stat().st_size for f in OUT.glob("*.webp")) / 1e6
    print(f"{len(manifest)} images, {size[0]}x{size[1]} px, {total:.1f} MB")


if __name__ == "__main__":
    main()
