# Anthrogen flipbook (temporary)

A page-turning version of the Anthrogen zine, built with
[flipbook-viewer](https://github.com/theproductiveprogrammer/flipbook-viewer) 1.6.1 (MIT).

- **Desktop / tablet / phone in landscape:** the covers sit alone in the middle;
  the book opens into two-page spreads. Turn with the arrows, a click on either half
  of the book, a swipe, or the arrow keys (Home / End jump to the covers).
  Under the book: "Biological Abundance" and the current chapter (hidden on the covers).
- **Phone in portrait:** the pages in one scrolling column.
- **Order:** spreads 12–13 and 10–11 are shown in corrected reading order.
- **Pages:** cropped to trim, on the paper tone (#f4f3ec) with a soft spine shadow,
  plus a fine grain layer on top. Two sizes: `pages/md` (300 dpi) for laptops and
  phones, `pages/lg` (450 dpi) for large or high-density screens; the page picks one.

## Publish on GitHub Pages

1. Put the contents of this folder at the root of a repo (or a `docs/` folder).
2. Repo Settings → Pages → deploy from the branch (and folder) you used.

## Re-render the pages

```
pip install pymupdf pillow numpy
python3 tools/render_pages.py "anthro binder.pdf" "biological proof.pdf"
```

The interior comes from the binder; only the cover (first page) is taken from the proof.

## Changes to the vendored library

`vendor/flipbook-viewer.js` differs from the published file in two places:
the page-turn duration reads `window.FLIP_MS` (instant turns for reduced motion and
Home / End jumps), and the screen's pixel density is re-read each time the book is
rebuilt (keeps pages sharp after browser zoom or moving to another screen).
