# Anthrogen flipbook (temporary)

A page-turning version of the Anthrogen zine, built with
[flipbook-viewer](https://github.com/theproductiveprogrammer/flipbook-viewer) 1.6.1 (MIT).

- **Desktop / tablet / phone in landscape:** two-page spreads. Turn with the arrows,
  a click on either half of the book, a swipe, or the arrow keys (Home / End jump
  to the covers).
- **Phone in portrait:** the pages in one scrolling column.
- **Order:** spreads 12–13 and 10–11 are shown in corrected reading order.

## Publish on GitHub Pages

1. Put the contents of this folder at the root of a repo (or a `docs/` folder).
2. Repo Settings → Pages → deploy from the branch (and folder) you used.

## Re-render the pages

```
pip install pymupdf pillow
python3 tools/render_pages.py "anthro binder.pdf" "biological_proof.pdf"
```

This crops every page to its trim size, sets the page order and writes
`pages/*.webp` plus `pages/pages.js`. Rendered at 300 dpi by default in this folder (`--dpi 300`).

## Note

`vendor/flipbook-viewer.js` has one change from the published file: the page-turn
duration reads `window.FLIP_MS`, so turns are instant for reduced motion and for
Home / End jumps.
