# Lumaube – Shopify theme (Online Store 2.0, French)

A custom theme for the Lumaube store (wake-up light, scalp massager, sleep mask). It has a French
default locale with English as a second locale, and no dependencies (vanilla JS, one CSS file).
It passes Shopify **Theme Check with 0 errors and 0 warnings**.

Preview screenshots: [`docs/preview/`](../docs/preview/). Rebuild them with `tools/theme-preview`.

## What's inside
| Area | Features |
|---|---|
| Home (`index.json`) | Hero (video, image or animated sunrise) · trust bar · product grid · 3 steps · evening ritual · comparison table · FAQ (with FAQ schema) · 30-day guarantee · newsletter |
| Product (`product.json`, `product.massager.json`) | Gallery + thumbnails · price (compare-at shown **only** if it's really higher) · benefits · variant picker · add to cart without reload + PayPal express button · **delivery date estimate** in business days · trust badges · bundle / cross-sell block · specs table (from metafield) · tabs · sticky add-to-cart on mobile · steps · FAQ · app slot for reviews · guarantee · recommendations |
| Guide (`page.guide.json`) | SEO buying guide + criteria table + FAQ + products |
| Other | Collection, cart, search, contact form (`page.contact`), blog, article, 404, gift card |
| Settings | Colours, fonts (Lora / Assistant), logo, delivery days (dispatch + min/max), guarantee days, support e-mail, socials |

## Install (about 1 hour)
1. **Upload the theme.** Either:
   - zip the `shopify-theme` folder: `cd shopify-theme && zip -r ../lumaube-theme.zip .`, then in
     Shopify go to *Online Store › Themes › Add theme › Upload zip file*; or
   - use the Shopify CLI: `npm i -g @shopify/cli`, then `shopify theme push --unpublished --store your-store.myshopify.com`
     from inside `shopify-theme/`, and `shopify theme dev` for a live preview.
2. **Metafield definitions** (*Settings › Custom data › Products*):
   - `lumaube.tagline`: single line text (shown under the title);
   - `lumaube.specs`: multi-line text, one `Name: value` per line (fills the specs table).
3. **Products:** create them from [`store-content/products.md`](../store-content/products.md). Set the
   scalp massager's template to **`product.massager`**. Leave compare-at prices empty.
4. **Pages:**
   - *Guide*: template `page.guide`, handle `guide-simulateur-d-aube`, content from
     [`store-content/guide-simulateur-aube.md`](../store-content/guide-simulateur-aube.md).
   - *Contact*: template `page.contact`.
   - *Mentions légales*, *Livraison*, *Retours*: from [`store-content/legal-fr.md`](../store-content/legal-fr.md).
   - Also fill the Shopify policies (*Settings › Policies*).
5. **Menus** (*Online Store › Navigation*):
   - `main-menu`: Réveil simulateur d'aube · Masseur cuir chevelu · Guide · Contact.
   - `footer`: Livraison · Retours · Mentions légales · CGV · Confidentialité · Contact.
6. **Theme editor:**
   - Hero › Vidéo: upload `store-content/media/lumaube-hero-1920x1080.mp4` to *Content › Files* and
     select it.
   - Button links: point button 1 to the wake-up light product.
   - Product template › "Produit complémentaire": pick the sleep mask.
   - *Theme settings › Livraison & confiance*: set the delivery days to match your real carrier.
7. **Apps:**
   - **CJ Dropshipping** (or DSers): product mapping and auto-fulfilment.
   - **Judge.me**: verified reviews; add its block in the "Applications" section of the product
     template.
   - **Google & YouTube**: Merchant Center.
   - **Shopify Bundles**: for the kit.
8. **Payments:** PayPal (see `docs/pipeline.md`). Test checkout with a real order and refund it.

## ⚠️ Verify before publishing (honesty checklist)
The theme copy describes a **target** wake-up light. Order a sample and **delete anything it doesn't do**:
- [ ] Adjustable sunrise duration "10 à 60 min" (home steps, hero text, comparison table, product benefits)
- [ ] Natural sounds / FM radio (home step 3, comparison, product benefits)
- [ ] Sunset / "mode crépuscule" (home evening section, comparison, product benefits)
- [ ] Dimmable display (guide criteria)
- [ ] Delivery times in *Theme settings* match the CJ line you actually use
- [ ] Don't promise "no customs fees" unless your CJ shipping method includes EU VAT (IOSS)
- [ ] Never add health claims ("soigne", "anti-insomnie", "pousse des cheveux")
- [ ] Reviews: only real ones from the reviews app

## Files
```
layout/theme.liquid          global layout, fonts, CSS variables
sections/*.liquid            all sections (each with its schema)
sections/*-group.json        header + footer groups
snippets/                    logo, icons, price, product card, delivery estimate, meta tags
templates/*.json             page compositions (French content pre-filled)
assets/base.css, theme.js    styles and behaviour
assets/lumaube-logo*.svg     logos · assets/favicon.png
locales/fr.default.json, en.json
config/settings_schema.json, settings_data.json
```
