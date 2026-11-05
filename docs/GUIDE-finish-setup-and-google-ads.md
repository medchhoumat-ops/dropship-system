# Lumaube – finish the setup and start Google Ads

Written 5 Nov 2026 for lumaube.shop. Shopify menus are in French, so French labels are in **bold**.
Do the parts in order. Each step says what to click and how to check that it worked.

---

## Where you are now

| Area | Status |
|---|---|
| Domain `lumaube.shop` + HTTPS | ✅ Done |
| Theme "Lumaube v5 (FINAL)" live | ✅ Done |
| 3 products active (réveil €49.90, masseur €34.90, masque €12.90) | ✅ Done |
| Stock tracking off (dropshipping) | ✅ Done |
| Market: France only (the "Maroc" market was deleted on 5 Nov) | ✅ Done |
| Free shipping France "7 à 12 jours ouvrés" | ✅ Done |
| PayPal Express Checkout (EUR) | ✅ Done |
| CJ app: store authorized, 3 products connected (YunExpress Sensitive) | ✅ Done |
| Policies: legal notice, returns 30 days, contact | ✅ Done |
| "Épuisé" on product pages | ⚠️ Check now (Part A, step 1) |
| Test order | ⏳ To do |
| PayPal "account optional", consumer mediator, samples, cookie banner | ⏳ To do |
| Masseur + masque new photos | ⏳ ElevenLabs free plan: 3 images per day |

---

## Part A – Finish the store (about 1 hour)

### 1. Check that products can be bought
1. Open a private window (**Cmd + Shift + N**) and go to `lumaube.shop/products/masque-de-nuit`.
2. You should see an orange **Ajouter au panier** button and an active yellow PayPal button.
3. If it still says **Épuisé**:
   - In Shopify, open the product and click **Afficher en tant que** (top right). Choose **France** and
     check the button there.
   - If it's fine there, the problem only affects visitors from Morocco, and French customers can buy.
   - If it says Épuisé there too, send a screenshot to Claude.

### 2. Test order (proves payment → order → CJ works)
1. In the private window, add the **Masque de Nuit (Noir)** to the cart and go to checkout.
2. Use a French delivery address, for example a friend's.
3. Check that **Livraison offerte avec suivi – 0,00 €** is shown, then pay with PayPal.
4. Check the order in **Shopify › Commandes**, then in CJ under **Orders**.
5. **Refund it:** in **Shopify › Commandes**, open the order, click **Rembourser**, then **Annuler la commande**.
   **Do not pay it in CJ.** PayPal keeps its small fixed fee, which is normal.

### 3. PayPal
1. Go to paypal.com › **Settings › Website payments › Website preferences**.
2. Set **PayPal account optional** to **On**, so customers can pay by card without a PayPal account.
3. Check **Resolution Center**: the old account limitation must be gone, or PayPal can hold your money.
4. Add your bank account or card for withdrawals.

### 4. Cookie banner (required in France, and for Google Ads)
1. In **Paramètres › Confidentialité des clients › Bannière de cookies**, turn the banner **on** for
   France / the European Union.
2. Language: French. Keep "Accepter / Refuser" buttons with the same prominence.

Without consent, Google Ads can't measure sales properly in France (Consent Mode). The Google & YouTube app reads
this banner automatically.

### 5. Consumer mediator (legal requirement in France)
1. Choose a mediator from the official list of approved mediators on **economie.gouv.fr** (search "médiateurs de la
   consommation référencés"). Several have low-cost plans for small online shops.
2. Send its **name and website** to Claude. Claude adds them to the CGV page and publishes it, and gives you the text for
   **Paramètres › Politiques › Conditions de service**.

### 6. Samples
1. In CJ, order 1 of each product to your address in Morocco.
2. When they arrive, test the réveil: sunrise duration, sounds or radio, sunset mode, and the colours with the clock.
   Tell Claude, who will add only what's real to the website.
3. Film the UGC videos (scripts in `store-content/products.md`) and take real photos.

### 7. Photos for the masseur and the masque
The free ElevenLabs plan allows a few images per day. Each day, ask Claude for that day's images, or upgrade
ElevenLabs to do them all at once. The réveil already has new photos (studio, bedroom, French infographic).

### 8. Reviews (free)
Install **Judge.me** (free plan) from the Shopify App Store. Add its block in the theme editor
(product template › **Applications** section). Only real reviews: Judge.me asks buyers automatically.

---

## Part B – Connect the website to Google

### B1. Create the Google accounts (30 min)
Use one Google account (Gmail) for everything.

1. **Merchant Center:** you'll create it from the Shopify app in B2. Don't create it separately.
2. **Google Ads:** go to ads.google.com and click **Start now**.
   - When Google offers a "Smart" campaign, click **Switch to Expert Mode** (small link at the bottom).
     Then click **Create an account without a campaign**.
   - Billing country: **Morocco**. Time zone: **(GMT+01:00) Casablanca**.
   - **Currency: EUR.** Choose EUR, the same as your store. **It cannot be changed later.**
   - Payment: your bank card in your own name. An individual account is allowed. Google may ask for
     **advertiser verification** (photo of your ID): do it, it's normal.

### B2. Install the Google & YouTube app in Shopify (20 min)
1. In the Shopify App Store, install **Google & YouTube** (by Google).
2. **Connect Google account** (the Gmail from B1).
3. **Merchant Center:** **Create new account**.
   - Target country: **France**. Language: **French**.
   - Business name: **Lumaube**.
   - The app checks your store's requirements: refund policy, contact info, secure checkout, no password. All
     of them are already done.
4. **Google Ads:** connect the account from B1. The app then installs **conversion tracking** automatically
   (purchase, add to cart, begin checkout) and the Google tag.
5. **Product sync:** choose **all products**.

### B3. Fix the product data for Google (15 min)
In Shopify, open each product. In the **Google & YouTube** box on the product page:

| Field | Value |
|---|---|
| Product category | Already set by Claude (Réveils / Appareils de massage électriques / Masques de sommeil) |
| Condition | New |
| Custom product | **Yes** (you have no GTIN/EAN barcode; this tells Google "identifier_exists = no") |
| Brand | Lumaube (from "Fournisseur") |

Google rules to respect:
- **The first image must have no text or logo on it.** The réveil's first image is the studio photo, which is fine.
- Prices on the site and in Google must match. The app keeps them in sync.

### B4. Merchant Center settings (15 min)
In **merchants.google.com**:
1. **Business info:** name Lumaube; your address in Morocco, exactly as on the Mentions légales page; phone
   +212 6 05 56 89 57 (Google sends an SMS code).
2. **Shipping and returns › Shipping:** country **France**, cost **€0**, handling **1–3 business days**,
   transit **7–12 business days**. If the app imported shipping from Shopify, check these values.
3. **Shipping and returns › Returns:** **30 days**, the customer pays return shipping, free for defective items.
   Return policy URL: `https://lumaube.shop/policies/refund-policy`.
4. **Growth › Manage programs:** turn on **Free listings** and **Shopping ads**.
5. Wait for **approval: 3 to 7 days**. Fix everything under **Products › Needs attention**.

**Free listings** show your products on Google Shopping for €0. You get your first free visits as soon as you're approved.

### B5. Check tracking before spending anything
1. In Google Ads, go to **Goals › Conversions › Summary**. You should see conversions created by
   "Google & YouTube" (Purchase, Add to cart…).
2. The status becomes **Recording conversions** after your test order (Part A, step 2) or the first real sale.
   Do the test order **after** connecting the app, so it gets recorded.
3. Turn on **Enhanced conversions** (Goals › Settings) and accept the terms.

---

## Part C – Start the ads (only after A2, B4 approval and B5)

### The money (updated 5 Nov with real CJ shipping)
| Product | Price | Cost (CJ product + shipping) | Fees (PayPal + Shopify ≈ 9% + €0.49) | Profit before VAT | Profit if 20% VAT is due* |
|---|---|---|---|---|---|
| Réveil | €49.90 | ≈ €23 ($14.76 + $10.44) | ≈ €5.0 | **≈ €22** | ≈ €13.6 |
| Masseur | €34.90 | ≈ €10 ($4.12 + $6.59) | ≈ €3.6 | **≈ €21** | ≈ €15.5 |
| Masque | €12.90 | ≈ €6 | ≈ €1.7 | ≈ €5 | ≈ €3 |

\*Your prices say "TVA incluse". Selling to French consumers, the 20% VAT may be due through CJ's
IOSS. Check the VAT line on your first CJ order and ask an accountant. **Until it's confirmed, use the
conservative column:** you can spend at most **€13 of ads per réveil sold** and **€15 per masseur**.
Don't advertise the masque on its own: it's an add-on.

### Campaign 1 – Standard Shopping "FR | Réveil | Shopping" (start here)
1. **+ New campaign**, then **Create a campaign without a goal's guidance**, then **Shopping**.
2. Choose your Merchant Center, country **France**, then **Standard Shopping campaign**.
3. **Bidding:** **Manual CPC**. **Budget:** **€10/day**.
4. **Networks:** untick **Search partners** and **Display**.
5. **Locations:** France. Under **Location options**, choose **Presence: people in or regularly in your targeted locations**.
6. **Product groups:** subdivide **All products** by **Item ID**:
   - réveil: max CPC **€0.25**;
   - masseur: max CPC **€0.20**;
   - masque: **Excluded**;
   - everything else: Excluded.
7. **Negative keywords:** paste this list:
   ```
   philips, lumie, gratuit, occasion, notice, mode d'emploi, réparation, bébé, veilleuse bébé, amazon, cdiscount, fnac, darty, boulanger, leclerc, ikea, pile, pièces, avis philips
   ```

### Campaign 2 – Search "FR | Réveil | Search" (add after Shopping works, or from day 1 at €5/day)
- **Budget:** €5/day. **Bidding:** manual CPC, max **€0.30**. Networks: Google Search only.
- **Keywords:** use exact `[ ]` and phrase `" "` match only:
  - `[reveil simulateur d'aube]`
  - `"réveil simulateur d'aube"`
  - `[simulateur d'aube]`
  - `[reveil simulateur d aube]`
  - `[réveil à aube]`
  - `[reveil aube]`
  - `"lampe simulateur d aube"`
- **Final URL:** `https://lumaube.shop/products/reveil-simulateur-d-aube`
- **Responsive search ad:** the 11 headlines (≤ 30 characters) and 4 descriptions (≤ 90) are in
  `store-content/google-ads-fr.md`. Copy them as they are. They only promise what's confirmed (progressive
  light, free delivery, 30 days, €49.90).

### Your daily routine (10 minutes)
| When | What to check | Rule |
|---|---|---|
| Every day | Spend, clicks, orders | If a product spends **€15 with 0 sale**, pause it and tell Claude |
| Every day | New orders in CJ | Pay them in CJ the same day (Add to cart › Pay) |
| Every 3 days | ROAS (conversion value ÷ cost) | ROAS **> 3**: raise the budget **+20%**. ROAS **< 2**: lower bids **−20%** |
| Every week | **Search terms** report | Add irrelevant searches as negative keywords |
| After 30 sales | Bidding | Switch Shopping to **Target ROAS 300%** |

### What not to do
- No **Performance Max** at the start: it spends on YouTube and Display before Shopping proves itself.
- No **"Smart" campaigns** (Google's default suggestion).
- Don't raise budgets before tracking shows real purchases.
- No health claims in ads ("soigne", "insomnie", "chute de cheveux"): Google disapproves them, and they're illegal.
- No fake discounts. Don't add a compare-at price in Shopify.

---

## Where everything is
| File | Content |
|---|---|
| `store-content/google-ads-fr.md` | Keywords, ad texts, negatives |
| `store-content/products.md` | Product texts, CJ IDs, UGC scripts |
| `store-content/legal-fr.md` | Legal texts |
| `store-content/listing-images.md` | Product photo plan |
| `docs/launch-status.md` | Launch checklist |
| `store-content/media/` | Videos for ads (vertical, square, banner) |
