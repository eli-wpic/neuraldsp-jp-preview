# Neural DSP Japan — new Shopify theme (preview)

**Live preview for feedback (Pastel):** https://eli-wpic.github.io/neuraldsp-jp-preview/

This is a static preview of the new neuraldsp.jp theme, rendered locally from the theme with the store's public product, collection and blog data. Cart, checkout, login and search only work on the real Shopify store.

## What's here

| Folder | Contents |
| --- | --- |
| `docs/` | The preview site served by GitHub Pages (generated, don't edit by hand) |
| `theme/` | The Shopify OS 2.0 theme source (zip this folder to upload it to Shopify) |
| `tools/` | `convert_live_to_theme.py` (live copy → templates), `apply_theme_extras.py`, `build_pages.py`, and `preview/` (local renderer, data fetcher, theme check) |
| `site/live-content-inventory.json` | Every piece of copy captured from the live site |
| `THEME-INSTALL-GUIDE.md` | How to upload, preview and publish the theme in Shopify |
| `plugin-addons-import.csv` | Optional add-on products for multi-plugin purchases (prices to confirm) |

## Rebuild the preview

```bash
cd tools/preview && npm install
node fetch-live.mjs                      # refresh product / collection / blog data from neuraldsp.jp
MOCK_ADDONS=1 node render.mjs ../../theme ../../.preview
cd ../.. && python3 tools/build_pages.py .preview docs neuraldsp-jp-preview
```

Nothing here publishes to Shopify. The theme is uploaded manually as an unpublished theme (see the install guide).
