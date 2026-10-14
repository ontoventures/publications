"""Render the Anthrogen zine into flipbook page images.

Usage:
    python3 tools/render_pages.py "anthro binder.pdf" "biological proof.pdf"

The interior comes from the binder (it has the 10 Sep revisions to pp. 8, 9,
27 and 47). Only the first page (the wraparound cover) is used from the
printer's proof, or from the standalone cover PDF.

Writes two sets of the same pages, chosen by the viewer to suit the screen:
    pages/lg/NN.webp   450 dpi, for large and high-density screens
    pages/md/NN.webp   300 dpi, for laptops and phones
and pages/pages.js (the order the viewer reads).

Every page is cropped to trim, multiplied onto the paper tone (#f4f3ec), and
the inner pages get a soft shadow at the spine. Covers get the tone only.

Book order (the viewer shows the first image alone on the right, then pairs):
    front cover | blank inside cover, p1 | p2, p3 | ... | p8, p9 |
    p12, p13 | p10, p11 | p14, p15 | ... | p48, blank inside cover | back cover
Spreads 12-13 and 10-11 are swapped back into reading order (Elena, 9 Oct 2026).
"""
import argparse
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "pages"
PAPER = np.array([0xF4, 0xF3, 0xEC], dtype=np.float32) / 255
SETS = {"lg": 450, "md": 300}


def reading_order():
    pages = list(range(1, 10)) + [12, 13, 10, 11] + list(range(14, 49))
    assert sorted(pages) == list(range(1, 49))
    return ["front", "blank"] + pages + ["blank", "back"]


def trim(page):
    """The trim box in the page's own coordinates (which start at the crop box)."""
    box = page.trimbox
    if not (box.width > 0 and box != page.mediabox):
        return page.rect
    c = page.cropbox
    return pymupdf.Rect(box.x0 - c.x0, box.y0 - c.y0, box.x1 - c.x0, box.y1 - c.y0)


def render(page, clip, dpi):
    pix = page.get_pixmap(dpi=dpi, clip=clip, colorspace=pymupdf.csRGB, alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def spine(width, side):
    """Multiplier across the page width: a soft fold shadow at the spine side."""
    x = np.linspace(0, 1, width, dtype=np.float32)
    d = (1 - x) if side == "right" else x            # 0 at the spine
    near = np.clip(1 - d / 0.045, 0, 1) ** 2.2        # tight crease
    wide = np.clip(1 - d / 0.16, 0, 1) ** 2           # broad curve of the page
    return 1 - 0.13 * near - 0.035 * wide


def finish(im, spine_side):
    a = np.asarray(im, dtype=np.float32) / 255 * PAPER
    if spine_side:
        a *= spine(a.shape[1], spine_side)[None, :, None]
    return Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("binder")
    ap.add_argument("cover")
    a = ap.parse_args()

    binder = pymupdf.open(a.binder)
    assert binder.page_count == 48, f"expected 48 pages, got {binder.page_count}"
    cover_pg = pymupdf.open(a.cover)[0]
    t = trim(cover_pg)
    mid = (t.x0 + t.x1) / 2
    dpi = SETS["lg"]

    for name in SETS:
        d = OUT / name
        d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("*.webp"):
            old.unlink()

    order = reading_order()
    size = None
    sizes = {}
    for n, key in enumerate(order, start=1):
        if key == "front":
            im = render(cover_pg, pymupdf.Rect(mid, t.y0, t.x1, t.y1), dpi)
        elif key == "back":
            im = render(cover_pg, pymupdf.Rect(t.x0, t.y0, mid, t.y1), dpi)
        elif key == "blank":
            im = None
        else:
            pg = binder[key - 1]
            im = render(pg, trim(pg), dpi)
        if size is None and im is not None and key != "front":
            size = im.size
        sizes[n] = (key, im)

    for n, (key, im) in sizes.items():
        if im is None:
            im = Image.new("RGB", size, "white")
        if im.size != size:
            im = im.resize(size, Image.LANCZOS)
        cover = key in ("front", "back")
        side = None if cover else ("right" if n % 2 == 0 else "left")  # even = left-hand page
        im = finish(im, side)
        im.save(OUT / "lg" / f"{n:02d}.webp", "WEBP", quality=82, method=6)
        md = (round(size[0] * SETS["md"] / dpi), round(size[1] * SETS["md"] / dpi))
        im.resize(md, Image.LANCZOS).save(OUT / "md" / f"{n:02d}.webp", "WEBP", quality=86, method=6)

    pages = [k for k in order]
    js = ("window.ZINE = {\n"
          f"  sizes: {{ lg: [{size[0]}, {size[1]}], md: [{md[0]}, {md[1]}] }},\n"
          f"  pages: {pages!r}\n}};\n").replace("'", '"')
    (OUT / "pages.js").write_text(js)
    for name in SETS:
        mb = sum(f.stat().st_size for f in (OUT / name).glob("*.webp")) / 1e6
        print(f"{name}: {len(order)} images, {mb:.1f} MB")


if __name__ == "__main__":
    main()
