# Neural DSP Japan — new theme: install guide

**File to upload:** `neuraldsp-jp-theme.zip` (source in `neuraldsp-jp-theme/`)
**Replaces:** the current live theme "M New LIVE - Reformation"
**Built:** 2026-10-23

## 1. Upload and preview (nothing changes for customers yet)

1. In Shopify admin, go to **Online Store → Themes → Add theme → Upload zip file** and choose `neuraldsp-jp-theme.zip`.
2. The theme arrives **unpublished**, and the live site stays exactly as it is.
3. Click **Preview**, or **Customize** to edit text and images.
4. Re-enable the apps that live inside the old theme (Customize → **App embeds**):
   - **Reviews (Judge.me or similar):** turn the embed on, then on the product templates add the review block to the **Apps** section that sits under the FAQ.
   - Any other embeds the old theme had on (chat, analytics, and so on).
5. When everything looks right, click **Publish**. You can switch back to the old theme at any time from the Themes list.

> I have not uploaded or published anything. The steps above are yours to run.

## 2. What carries over automatically

All of this stays in Shopify, so the new theme reads it directly:
- products, prices, variants, stock, checkout and payment methods
- the blog and its articles (Latest News), customer accounts
- the `/a/support/...` help centre (app proxy)

Every product and page template name from the live theme exists in the new theme, so the products and pages already assigned to them keep their layout. No re-assigning is needed.

## 3. What was rebuilt (the old theme stored this content in its own sections)

The live site kept most of its copy in theme sections, which a theme switch would have lost. It has all been carried over **word for word** by `tools/convert_live_to_theme.py`:

| Area | Templates |
| --- | --- |
| Hardware pages (hero, awards, features, I/O, specs, **FAQs**) | `product.quad-cortex`, `product.quad-cortex-mini`, `product.nano-cortex` |
| Plugin bundle pages (12 × QC, 12 × mini) | `product.quadcortex-*`, `product.quad-cortex-mini-*`, `product.archetype-john-mayer-x` |
| Accessories | `product.gig-case`, `product.psu`, `page.accessory` |
| Legal | privacy, terms, refund, warranty, Cortex Cloud terms, 特定商取引法 |
| Guides | shopping guide (FAQ hub), plugin beginner's guide, contact |

The full extracted content is in `site/live-content-inventory.json`.

## 4. New in this theme

- **Fonts:** IBM Plex Sans JP for all text (it includes its own English letters). The big English product names (QUAD CORTEX) use Archivo, extra-wide and black.
- **Homepage hero (3D + campaigns):**
  - A dock at the bottom of the hero switches between the campaign, Quad Cortex, Quad Cortex mini and Nano Cortex. Each product is a real-time 3D model that stays pinned while you scroll through 5 views, and you can drag to spin it.
  - A 「購入する」 pill for the product on screen stays visible for the rest of the homepage.
  - The old campaign banner image and the separate line-up strip are gone; the campaign now lives in the hero (see section 10).
- **One type system:** seven text sizes used everywhere, and the view buttons and chooser use the same pill as the buttons.
- **Product pages open on the buy section:**
  - The same real-time 3D model sits beside the buy panel (Quad Cortex, mini and Nano; the bundle pages show the Quad Cortex or mini).
  - The view buttons glide the camera exactly like the homepage, and each view's caption is the product's live wording.
  - Photos are one tap away under 「写真」 and use the same glide transition.
- **Buying never waits for the animation:**
  - 「購入する」 is the main button on the first screen; it adds the product to the cart and goes to checkout, like the live site's buy button.
  - A visible 「スキップ」 pill jumps past the homepage 3D story.
- **Gig Case and PSU:** a product hero built from the new cut-out photos, with the live wording.
- **Buy box:**
  - Choose **several plugins** (see section 9) and accessories (never pre-ticked), with a live total and breakdown.
  - The live labels カートに追加する / 購入する.
  - Trust badges: 送料無料 / 14日以内返品可 / 3年保証.
- **"Find your sound" plugin discovery:**
  - A sound slider (すべて / クリーン / クランチ / ハイゲイン / アンビエント) that hides the plugins that don't match, launch videos, 14日間無料体験 (→ neuraldsp.com downloads), and buy-as-a-set buttons.
  - Shown on the homepage and on both "+ Plugin" pages.
- **Newsletter:**
  - The same fields and customer tags as live (`birthday_…`, `gender_…`).
  - On product pages it opens from a floating button, which hides while the 3D story is on screen.

## 5. Simplified structure (blog and FAQs kept)

| Before | Now |
| --- | --- |
| 7 menu items, 26 dropdown links | 6 items: **ハードウェア ▾ / アクセサリー ▾ / Plugin / Cortex Cloud / Latest News / サポート** |
| "Quad Cortex + Plugin" and "mini + Plugin" list pages | One plugin discovery layout for each hardware; plugin choice also lives on the product page |
| Cortex Control and Cortex Cloud as separate pages | One page; both URLs show it |
| Shopping guide | **FAQ hub**: shopping-guide FAQs, links to each product's FAQ (`#faq`), and support links |

All old URLs still work. The simplified menu is built into the header. To go back to your Shopify navigation, open **Customize → Header → Navigation source → Shopify menu**.

## 6. Fixes compared with the live site

- **The 14-day trial pop-up named the wrong plugin.** On every bundle page it said "Archetype: Cory Wong X". It now names each page's own plugin.
- **The trial form went nowhere.** It pointed at a placeholder URL (`example.com/trial`). It now opens the official download page (`https://neuraldsp.com/downloads`).

## 7. Left out on purpose

- The collection template's leftover demo text ("USE IT TO ADD SEO TEXT…").
- The Reformation theme's "shop でフォロー" button. Add it back with the Shop app block if you want it.

## 8. Checks run

- **Shopify Theme Check:** 0 errors. The 5 warnings are about Google Fonts and YouTube thumbnails, which are loaded from outside Shopify on purpose.
- **Local render with real neuraldsp.jp product data:** homepage, 3 hardware pages, bundle pages, legal pages, Cortex page, FAQ hub, plugin page and contact page all render without Liquid errors.
- **Screenshots** at desktop and phone sizes are in `theme-previews/`.
- **Not tested yet:**
  - on the real store: app embeds, checkout from the new buttons, customer login
  - on a physical phone's GPU (the 3D views)

  Please check these in Shopify's theme preview before publishing.

## 9. Turning on multiple plugins (one import, no theme changes)

neuraldsp.jp currently sells plugins only as "hardware + one plugin" bundles, so there is no product a second plugin could be sold as. To let customers pick several:

1. **Import the add-on products.** In Shopify admin, go to **Products → Import** and upload `plugin-addons-import.csv`.
   - It creates 12 plugin-only products, handles `plugin-addon-…`, tagged `plugin-addon`.
   - Each price is the plugin's current bundle difference, e.g. Gojira X ¥23,000.
   - Please confirm these prices with Neural DSP before importing.
2. **Nothing else to change.** The Quad Cortex and Quad Cortex mini templates already point at these handles.
   - As soon as the products exist, the picker switches from "one plugin" to "select several".
   - The cart then gets the hardware plus one add-on per chosen plugin.
3. **Until then,** the picker uses the existing bundles, one plugin per order, and says so to the customer.

> **Note:** add-on products can technically be bought on their own if someone finds their URL. They aren't in any collection or menu. If that matters, add a cart rule (a Shopify Function or app) that requires a Quad Cortex / mini in the same cart.

## 10. Running a campaign in the homepage hero

Open **Customize → Home page → ND · Hero 3D + campaign**. The hero holds a list of items; each one gets a button in the dock.

- **Campaign item** (one is already set up: 「Quad Cortex mini にもPLUGINセットが登場」):
  - **Visual:** one of the 3D models, or **Photo or video** to use a campaign key visual (upload an image or paste an mp4 URL).
  - Title, lead, up to two buttons, small print, and the dock label.
  - **Start / end date** (YYYY-MM-DD): the campaign shows only between these dates, so it can be scheduled ahead and disappears on its own. Untick **Show this campaign** to hide it now.
- **Product items:** Quad Cortex, Quad Cortex mini, Nano Cortex, with the 5 chapters of live wording. Price and buy button come from the product.
- **Order = dock order.** The first live item is what visitors see first. Drag the campaign above the products while it runs, or below them to make it a secondary tab.
- Up to 6 items. With only one live item, the dock hides itself.

> **Note:** the dates are checked when Shopify renders the page, in the store's time zone. Shopify caches pages, so a campaign can take a few minutes to appear or disappear around midnight.

## 11. Product media, plugin pages and the mini PSU

- **フル動画を見る plays in place.** On product pages and plugin-page heroes the YouTube film replaces the 3D model or hero picture (like a canvas turning into the full video). Any view button, 写真 or 閉じる switches back.
- **写真 uses the transparent photos** shipped with the theme (`assets/qc-photo-*.webp`, `mini-photo-*`, `nano-photo-*`, `psu-photo-*`, `minipsu-photo-*`), not Shopify's white-background product photos. To change them, edit **Photos from theme assets** on the product section, or clear it to use the Shopify images.
- **Plugin pages: 本体を選ぶ.** Every plugin page lists the same plugin with Quad Cortex and Quad Cortex mini; picking one opens that set's page.
- **Sound discovery:** all 12 plugins have a video row. Their button is 詳しく見る and opens the plugin page (plugins are sold only with a Quad Cortex or Quad Cortex mini).
- **Quad Cortex mini PSU (new): needs a product in Shopify.**
  1. Create the product with handle `quad-cortex-mini-psu`, its price and stock.
  2. Upload the photos from `mini-PSU/transparent/` (backgrounds already removed).
  3. Assign the template `product.mini-psu`.
  The hero text on that template is a draft based on the existing PSU wording; please confirm it.
  Once the product exists it automatically appears as an accessory on the Quad Cortex, Quad Cortex mini and Nano Cortex pages (both PSUs are offered on every hardware page).
- **Animations:** every section fades up once as it scrolls in, and every FAQ / spec / menu accordion opens with the same glide.

## 12. Layout clean-up (latest round)

- **No boxed / see-through cards:** comparison, support, collection and product cards are plain columns separated by thin lines.
- **Sound discovery:** the STEP 1–3 strip is gone; the slider is a plain line with stops; every plugin row has the same size and alternates left/right (also after filtering).
- **Menu:** アクセサリー is its own dropdown (Gig Case, 電源アダプター). Add the mini PSU there once its product exists (Customize → Header → アクセサリー → Links).
- **Plugin pages:** the hero is the plugin's video only. Switching Quad Cortex ↔ mini under 本体を選ぶ keeps the visitor at the same spot on the page.
- **Product pages:** プラグインを追加 shows 3 plugins until 「すべてのプラグインを表示」 is tapped.
- **Cortex Control / Cortex Cloud:** the hero has the Cortex Control film looping behind it, and ▶ フル動画を見る plays it in place.
- **Awards:** every badge sits in the same-size box above its text.
- **Found on the live store, not the theme:** the article 「quad-cortex-pluginfree-campaign」 shows five plugin images that no longer exist on Shopify's CDN (404 on the live site too). Re-upload them in the blog post.

## 13. Trial downloads, comparison, FAQs (latest round)

- **14日間無料体験 opens a download card** for that plugin: Windows / macOS installers, マニュアル, 変更履歴, 過去のリリース. Until the packages arrive every button shows 準備中. Add the links per plugin in **Customize → plugin section → each plugin → "14-day trial downloads"**, and on each plugin page in **ND · 14-day trial dialog**.
- **Pricing:** the bundle prices in `202610_Plugin_Bundle_Pricing.xlsx` (list price) already match the live store, so no price changes were needed.
- **Homepage:** the Nano Cortex / Quad Cortex / Gig Case video tiles are removed. The Quad Cortex story shows its 4 award badges on its last screen (add awards for other products in the hero's product item → Awards).
- **Comparison:** Quad Cortex, mini and Nano drawn to real scale, with size, weight bars, footswitch dots and ✓ for touchscreen / Neural Capture / plugins. The mini page shows the same chart; the full feature table is behind 「詳しい比較表を見る」.
- **FAQs** show 5 questions, then 「すべての質問を見る」. **Spec / manual** links are now plain buttons (the empty boxes are gone).
