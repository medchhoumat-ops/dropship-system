# Launch pipeline: from zero to a live Shopify store (Morocco-based owner)

The full checklist, in order. Tick each box before moving to the next phase.

> **Not legal, tax or financial advice.** Rules, fees and promotions change often, and the
> facts below were checked against general knowledge as of late 2026. Confirm every legal,
> tax and exchange-control point with a Moroccan *expert-comptable*, and in the country where
> you register a company.

Store model: **one niche, 4 related single-variant products**, shipped from warehouses in or
near the target market in ≤ 10 days, landed cost $5–15, retail ×4–5. Start with **one market**
(`config/settings.toml`).

---

## Phase 0: Decide the legal and payment setup (week 0–1)

You can't use Shopify Payments, Stripe or a normal PayPal Business account as a Morocco-based
business. **The company structure decides which payment gateways you can use.** Choose this
first.

### Option A: Moroccan auto-entrepreneur (cheapest; fine for testing)
- [ ] Register on the auto-entrepreneur portal (ae.gov.ma) or at a Barid Al-Maghrib agency.
      Check that an e-commerce/online-sales activity code is in the eligible list.
- [ ] Tax is a flat rate on turnover: about 0.5% for commercial activity, with an annual cap of
      roughly 500,000 MAD for commerce. Check the current rates and caps. AMO/CNSS contributions apply.
- [ ] Moroccan business bank account (CIH, Attijariwafa, BMCE/Bank of Africa, Al Barid Bank …).
- **Payments you can realistically get:** Payoneer (receive USD/EUR/GBP, withdraw to a
  Moroccan account), some third-party card gateways that onboard Moroccan merchants
  (e.g. 2Checkout/Verifone; check current eligibility), and CMI for card payments in MAD
  (needs a custom integration). A Moroccan PayPal account has historically been very
  limited for receiving money, so check its current status before relying on it.
- **Downsides:** Shopify adds a **third-party gateway fee** (≈2% on Basic) on top of the
  gateway's own fee. Customers trust these checkouts less. Some gateways hold funds longer.
  → Set `fee_pct` in `config/settings.toml` to the real total (e.g. `0.05`).

### Option B: US LLC (most common for US/CA stores)
- [ ] Form a single-member LLC (Wyoming / Delaware / New Mexico) yourself or through a service
      (Stripe Atlas, doola, Firstbase …). You'll need a registered agent and an EIN (Form SS-4;
      a non-resident without an SSN usually gets it by fax or by phone).
- [ ] US business bank account for non-residents (e.g. Mercury, Relay; availability for
      Moroccan founders varies).
- [ ] **Unlocks:** Shopify Payments (US), Stripe, PayPal Business US, Shop Pay, Apple Pay/Google Pay.
- [ ] **Annual compliance:** a foreign-owned single-member LLC must file **Form 5472 + pro-forma
      1120** every year. The penalty for missing it is very high (USD 25,000). Pay state fees
      and the registered agent too. Handle US sales-tax nexus (Shopify Tax tracks thresholds).

### Option C: UK Ltd (for UK/EU-first stores)
- [ ] Incorporate at Companies House (online, ~£100) with a UK registered-office service.
      Note the director identity-verification rules.
- [ ] UK business account (availability for non-residents varies).
- [ ] **Unlocks:** Shopify Payments UK, Stripe UK, PayPal UK.
- [ ] **VAT:** non-UK-established sellers have **no VAT threshold**. If you sell goods ≤ £135
      imported into the UK or stocked in a UK warehouse, register for UK VAT before the first sale.

### Option D: EU company (e.g. Estonian OÜ via e-Residency) for FR/DE
- [ ] Unlocks Shopify Payments EU and Stripe EU.
- [ ] Shipping from **EU warehouses** (e.g. CJ DE) is an EU supply: register for VAT and OSS.
      Imports ≤ €150 shipped from outside the EU go through **IOSS**.

### Critical for every option: Moroccan exchange control and tax
- [ ] Moroccan residents face **Office des Changes** rules on owning foreign companies and
      foreign bank accounts and on repatriating foreign income. Owning an LLC or Ltd abroad may
      need authorisation or declarations. Get **written** advice before you form one.
- [ ] As a Moroccan tax resident, your worldwide income is taxable in Morocco, and treaties
      (e.g. Morocco–US, Morocco–UK, Morocco–France) decide where it is taxed. Keep clean books
      from day 1: Shopify payouts, supplier invoices (CJ/AliExpress) and ad invoices.

**Recommendation:** validate the products with this tool first. If you target US/CA and want
the best conversion rate, choose Option B **after** the Office des Changes advice. If you want
the lowest legal overhead to start, use Option A with Payoneer and a third-party gateway, and
accept the extra fees.

---

## Phase 1: Product research with this repo (week 1)

- [ ] Fill in `.env` (start with Semrush + SerpApi + CJ; add Apify and AliExpress later).
- [ ] `dropship niche --country US --seeds "pets,kitchen,home"` → choose **one** niche from
      the top 5. It should have rising or stable demand, competition below 0.7 and a price range
      within $20–60.
- [ ] `dropship source "<idea>" --country US` for each product idea → keep the **4 best picks**
      (grade A/B). Prefer products that complement each other (bundle/upsell potential).
- [ ] Read every pick's **Risks** section. Check trademarks (USPTO / UKIPO / EUIPO),
      patents and the "as seen on TV" brands. Avoid products that need certification you can't
      prove (electrical, kids' toys, cosmetics, anything food-contact without docs).
- [ ] Read the competitor section: write down 3 gaps you'll do better (FAQ, returns window,
      bundles, faster delivery, better images).
- [ ] **Order samples** of all 4 products to your address (or to a friend in the target market).
      Check the quality, packaging and the real delivery time. Film the UGC with these samples.
- [ ] Ask the supplier (CJ agent / AliExpress store) for: stock in the local warehouse, price at
      30/100 orders per month, processing time, whether they can remove the invoice or price from
      the parcel, and branded packaging later.

---

## Phase 2: Shopify store (week 2)

### Account
- [ ] Sign up at shopify.com. Shopify usually gives a **3-day free trial, then $1/month for
      the first 1–3 months** on Basic/Grow. The offer depends on the country and the date, so check
      shopify.com/pricing at signup. Set the **store country to your company's country**
      (it decides the available payment providers and taxes).
- [ ] Store currency = target-market currency. Domain: buy a short `.com` (or `.co.uk`/`.fr`/`.de`)
      through Shopify or Cloudflare. Set up branded email (Zoho Mail or Google Workspace),
      e.g. `support@yourbrand.com`.

### Theme development with Shopify CLI
```bash
# Node.js 20+ and Git required
npm install -g @shopify/cli@latest
shopify theme init my-store-theme            # starts from the official reference theme
#   or start from Dawn:  shopify theme init my-store-theme --clone-url https://github.com/Shopify/dawn
cd my-store-theme
shopify theme dev --store your-store.myshopify.com   # live preview at http://127.0.0.1:9292
shopify theme check                                  # lint Liquid / performance / a11y
shopify theme push --unpublished                     # upload as a new draft theme
shopify theme publish                                # when ready
```
- [ ] Keep the theme in Git (a separate repo), or use the Shopify GitHub integration
      (Online Store → Themes → Add theme → Connect from GitHub).
- [ ] Theme work: a clear hero for the niche, trust bar (delivery time, returns window,
      secure checkout), an FAQ section answering the objections the competitors leave open,
      bundle offer block, sticky add-to-cart on mobile, fast pages (compress images, few apps).

### Products (4)
- [ ] Use the title, price (`.99`) and bundle ideas from the report. Set a compare-at price
      **only if there is a real former price**. In FR/DE (EU Omnibus rules), a "reduction"
      must refer to the lowest price of the last 30 days.
- [ ] Images: your own photos and the Google Flow images (prompts are in the report: worn/in use,
      in hand, flat lay, macro). No supplier watermarks. No text claims you can't prove.
- [ ] Description: what it does, dimensions/materials, what's in the box, care, delivery time
      ("ships from our US warehouse, delivered in X–Y business days").
- [ ] **No fake reviews.** Start with no reviews, and collect real ones after delivery
      (Judge.me or a similar app with verified-buyer badges).
- [ ] Fulfilment: connect the CJ app (or DSers for AliExpress), map each product to the
      **local-warehouse variant**, and turn on auto-fulfil after a manual check of the first 10 orders.

### Shipping and taxes
- [ ] Shipping profile per market: free shipping (built into the price) or a free-shipping
      threshold that makes bundles worthwhile. Show the delivery estimate = processing (1–2 d)
      + carrier days from the report.
- [ ] Shopify Tax / VAT settings that match Phase 0 (US nexus, UK VAT, EU OSS/IOSS).

### Policies (Settings → Policies)
- [ ] **Refund policy:** at least 30 days is a selling point (competitors often have 14).
      EU/UK law requires a 14-day right of withdrawal for distance sales.
- [ ] **Shipping policy:** processing time, delivery times per country, carriers, tracking,
      lost-parcel handling and customs (who pays).
- [ ] **Privacy policy:** GDPR/UK-GDPR for FR/DE/UK and cookie consent
      (Shopify Customer Privacy banner).
- [ ] **Terms of service** and **Contact information** (legal name, address, email, phone).
- [ ] **Germany:** *Impressum*. **France:** *mentions légales*. **EU:** GPSR (General Product
      Safety Regulation) requires an **EU-based responsible person** plus manufacturer details
      for each product sold to EU consumers. Organise this before selling to FR/DE.
- [ ] About page (who you are, where you ship from) and a Contact page with a form, email and
      expected response time.
- [ ] Footer links to all policies. Test checkout with Bogus Gateway / test mode, then place a
      real order and refund it.

### Tracking
- [ ] Install **Google & YouTube** app (Google tag + conversions), Shopify analytics,
      and optionally Microsoft Clarity for heatmaps.

---

## Phase 3: Google Merchant Center and Google Ads Shopping (week 3)

### Merchant Center
- [ ] Shopify → install **Google & YouTube** → connect your Google account → create or link
      **Merchant Center**. The app verifies and claims the domain and syncs products.
- [ ] Business info: legal name, address and customer-service contact, the same details as on
      the Contact page.
- [ ] **Shipping settings** in MC must match the store: handling 1–2 days, transit per country
      from the report, and the same cost or free-shipping threshold.
- [ ] **Return policy** in MC = the store refund policy (days, who pays return shipping).
- [ ] Product data: clear titles (`Brand + product type + key attribute`), a Google product
      category, `condition=new`, correct availability and price. Dropshipped items rarely have a
      GTIN: set your own brand and `identifier_exists = no` where appropriate (never invent GTINs).
- [ ] Enable **free listings** (free traffic and a data check).
- [ ] **Avoid "Misrepresentation" suspension:** real contact details, complete policies,
      HTTPS, no fake timers/scarcity/reviews, no unrealistic claims, prices and shipping
      consistent across feed, page and checkout, and enough original content (About page,
      original images). Fix every item in *Products → Needs attention* before you advertise.

### Google Ads
- [ ] Create a Google Ads account, link it to MC (via the Google & YouTube app), complete
      **advertiser verification** and billing.
- [ ] Conversion tracking: purchases imported via the app (Google tag + enhanced conversions).
      Check that a test purchase records a conversion.
- [ ] **First campaign:** either *Standard Shopping* (more control) or *Performance Max* with a
      feed-only asset group. Budget $20–30/day per market. Bidding: *Maximize conversion value*
      without a target for the first ~30 conversions.
- [ ] Then set **target ROAS ≥ the break-even ROAS** from the report (e.g. break-even 1.4 →
      start tROAS around 180–200% to leave room for refunds and fees).
- [ ] Supplemental feed / custom labels: `custom_label_0 = grade (A/B/C)` and
      `custom_label_1 = margin bucket`, so you can bid more on winners.
- [ ] Standard Shopping: add negative keywords weekly (free, DIY, how to, brand names, wrong
      product types).
- [ ] Kill/scale rules: if spend reaches 2× the break-even CPA with no sale, pause the product.
      If ROAS stays above break-even for 3+ days, raise the budget 20% every 3 days.
- [ ] YouTube/Demand Gen later, using the 3 UGC scripts from the report (filmed with real
      samples, #ad disclosure if a creator is paid or gifted).

---

## Phase 4: Customer support and the support bot

### Phase 4a: before launch (manual, day 1)
- [ ] Shared inbox `support@`, Shopify Inbox chat on the store, and order tracking page
      (CJ tracking numbers synced to Shopify; a tracking app such as 17TRACK / AfterShip / Parcel Panel).
- [ ] Macros for the top questions: where is my order, delivery time, return request, damaged
      item, change address, cancel order.
- [ ] Target first response under 24 h. Handle chargebacks within the gateway's deadline.

### Phase 4b: the support bot (once you have ~5+ tickets/day)
**Scope (v1)**
1. Order status: the customer gives order number + email → Shopify Admin API order lookup →
   fulfilment status and tracking link.
2. Questions about shipping, returns and products, answered **only** from a knowledge base:
   store policies, FAQ and product pages (also the content that fills competitor gaps).
3. Start a return: collect the order number, reason and photos → create a ticket for a human.

**Guardrails**
- It never invents delivery dates, discounts, refunds or product claims. It never promises
  anything outside policy.
- It hands over to a human on: refund/chargeback mentions, angry sentiment, a second failed
  answer, legal/safety topics, or when the customer asks for a human.
- It only reveals order data after the order number and email match. Log as little PII as
  possible, mention the bot in the privacy policy, and follow GDPR deletion requests.
- Languages: EN, then FR/DE as you open those markets. Answer in the customer's language.

**Stack options**
- *No-code:* a helpdesk with a built-in AI agent and Shopify integration (Gorgias, Tidio,
  Zendesk …). It's the fastest to set up.
- *Custom (cheaper at volume):* a small FastAPI service on the same VPS. It receives chat/email
  webhooks, uses a custom Shopify app (read-only order scope) and an LLM API (a small, cheap
  model is enough). Retrieval runs over the policies and FAQ. Add a human-handoff queue.
  Add it as `src/dropship/support/` when needed.

**Metrics:** share resolved without a human, first-response time, CSAT, refund rate per product
(feed this back into product selection).

---

## Phase 5: Launch and the weekly loop

- [ ] Final QA on mobile: page speed, every link, checkout in each market currency, policy
      pages, contact form and emails (order confirmation, shipping confirmation).
- [ ] Launch ads in **one** market. Watch the daily numbers: CTR, CPC, add-to-cart rate,
      conversion rate, AOV and CPA vs the break-even CPA from the report.
- [ ] **Weekly (cron on the VPS):** `deploy/weekly-niche.sh` refreshes the niche scan. Re-run
      `dropship source` for live products to catch supplier price, stock and shipping changes.
- [ ] Monthly: replace the weakest of the 4 products with the next best pick in the same niche.
      Add bundles and upsells. When ROAS has been stable for ~4 weeks, open the next market
      (re-source with local stock first, and complete the market's legal checklist in Phase 2).

### Suggested timeline
| Week | Milestone |
|---|---|
| 0 | Accountant + Office des Changes advice, company/payment option chosen |
| 1 | Niche picked, 4 products sourced, samples ordered |
| 2 | Store, theme, policies, product pages, fulfilment mapped |
| 3 | Merchant Center approved, conversion tracking verified, first Shopping campaign |
| 4+ | Optimise, add support bot, scale or swap products |
