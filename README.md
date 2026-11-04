# dropship-system

Product-research engine for a **one-niche Shopify dropshipping store** (one niche, 4 related
products). It finds niches, measures demand, sources suppliers with local stock, filters,
prices, scores and writes the ad creative brief for each product. Everything ends up in one
HTML report and one JSON file per run.

Target markets: **US, UK, CA, FR, DE** (pick them in `config/settings.toml`, start with one).

> The full business launch checklist (company and payments for a Morocco resident, Shopify,
> policies, Google Merchant Center and Shopping ads, support bot) is in
> [`docs/pipeline.md`](docs/pipeline.md).

---

## What it does

| Module | Path | What it does |
|---|---|---|
| research | `src/dropship/research/` | Semrush volume, CPC, competition and 12-month trend (optional: SerpApi Google Trends). Amazon page 1 through an Apify actor: price, rating, reviews, BSR, sellers. Google Shopping sellers and prices through SerpApi. |
| niche | `src/dropship/niche/` | Deep search: seed categories → sub-niches → keyword expansion. Ranks niches by demand, trend, competition and price range. Returns the top 5 niches, each with 4+ product ideas. |
| sourcing | `src/dropship/sourcing/` | CJ Dropshipping API v2 (`product/listV2`, `product/query`, `product/stock/queryByVid`, `logistic/freightCalculate`, max 1 req/s) and the AliExpress Drop Shipping API (`ds.text.search`, `ds.product.get`, `ds.freight.query`). Collects variants, stock per warehouse country, shipping methods with cost and days, and the supplier/store with a contact link. |
| filters | `src/dropship/filters.py` | Keeps only products that are single-variant, have stock in or near the market, deliver in ≤ 10 days and have a landed cost of $5–15. |
| pricing | `src/dropship/pricing.py` | Price = landed × 4–5 (cheaper items get ×5), rounded to .99. Also margin, break-even CPA and break-even ROAS after Shopify fees (2.9% + $0.30). |
| scoring | `src/dropship/scoring/` | Winner score from 0 to 100 (demand 25, margin 20, trend 15, competition 15, shipping 15, competitor stores 10). For each pick it writes why to pick it, the risks and how to scale. |
| competitors | `src/dropship/competitors/` | For Shopify stores found on Google Shopping: `/products.json`, prices, image count, FAQ, shipping/refund policies and theme. Lists what they do well and where the gaps are. |
| report | `src/dropship/report/` | `data/reports/<run>.html` (tables and reasons) plus `data/runs/<run>.json`. |
| creative | `src/dropship/creative/` | For each product: 4 Google Flow image prompts (worn/in use, in hand, flat lay, macro) and 3 UGC scripts (hook, problem, demo, CTA). It never writes fake reviews or claims. |

Hard rules (`config/settings.toml`): `landed_min_usd`, `landed_max_usd`,
`max_delivery_days`, `single_variant_only`, `multiplier_min/max`, `fee_pct`, `fee_fixed`.
"Near" warehouses per market: US ← US, CA · CA ← CA, US · UK ← GB + EU · FR/DE ← EU
(FR, DE, ES, IT, NL, BE, PL, CZ).

---

## Quick start (local)

```bash
git clone https://github.com/medchhoumat-ops/dropship-system.git
cd dropship-system
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env        # fill in the keys you have; empty = mock mode for that API
pytest                      # runs fully offline with sample fixtures
```

### Commands

```bash
# 1. Deep search: top 5 niches with 4+ product ideas each
dropship niche --country US --seeds "pets,kitchen"
dropship niche --country US --seeds "pets,kitchen" --source   # also source the #1 niche's ideas

# 2. One keyword: volume, trend, Amazon, Google Shopping, competitor stores
dropship research "dog lick mat" --country US
dropship research "dog lick mat" --country UK --no-amazon --competitor somestore.com

# 3. Suppliers → filters → pricing → score → narrative → creative
dropship source "dog lick mat" --country US
dropship source "cj:1424608189734113280" --country US --keyword "dog lick mat"
dropship source "ae:1005006123456789" --country FR
dropship source "https://www.aliexpress.com/item/1005006123456789.html" --country DE

# 4. Rebuild the HTML report for the latest run (or a specific one)
dropship report
dropship report --run data/runs/20261104-120000-source.json --open
```

Global flags: `--mock` (use fixtures for every API), `--config path/to/settings.toml`, `-v`.

`source` accepts a keyword, a CJ pid (a UUID or an 18+ digit number, or `cj:<pid>`), an
AliExpress id (`ae:<id>` or 10–17 digits) or a product URL.

### Outputs

```
data/cache/<api>/*.json     every API response (TTL in settings, default 7 days)
data/runs/<id>.json         full machine-readable run
data/reports/<id>.html      the report (open it in a browser)
```

---

## API keys

Keys are read **only from environment variables**. A local `.env` file is also loaded, but it
never overrides real env vars. `.env` is git-ignored. Do not put keys in `settings.toml`.

| Variable | Used for | Where to get it |
|---|---|---|
| `CJ_MCP_TOKEN` | CJ `CJ-Access-Token` header | CJ dashboard → API / developer section: generate an API key, then exchange it for an access token (`authentication/getAccessToken`). Tokens expire, so refresh them. |
| `AE_APP_KEY`, `AE_APP_SECRET`, `AE_ACCESS_TOKEN` | AliExpress DS API (`api-sg.aliexpress.com/sync`, HMAC-SHA256 signed) | openservice.aliexpress.com → create a *Drop Shipping* app → authorise your AliExpress account to get the access token |
| `APIFY_TOKEN` (+ optional `APIFY_AMAZON_ACTOR`) | Amazon search results | console.apify.com → Settings → Integrations. Default actor: `junglee~amazon-crawler` |
| `SEMRUSH_API_KEY` | `phrase_this` and `phrase_related` | Semrush Business plan + API units |
| `SERPAPI_KEY` | `google_shopping` (+ `google_trends` if `use_google_trends = true`) | serpapi.com/manage-api-key |

**Mock mode.** If a client has no key, it uses the sample fixtures in
`src/dropship/fixtures/` and the report shows a yellow "mock data" banner.
`DROPSHIP_MOCK=1` or `--mock` forces mock mode for every client. The mock data is
deterministic (the same keyword always gives the same numbers), so tests are stable.

**Cost control.** Semrush and SerpApi charge per call, and the Apify Amazon actor is the most
expensive. `niche` uses only Semrush, then calls Google Shopping for the top
`enrich_top` niches. `niche --source` skips Amazon. Use `--no-amazon` when you don't need it.
Cached responses are reused for `cache.ttl_hours`.

---

## Deploy on a VPS (Ubuntu 22.04 / 24.04)

A 1 vCPU / 1 GB VPS is enough (Hetzner, OVH, DigitalOcean, Contabo …).

```bash
# 1. As root: a non-root user + Docker
adduser dropship && usermod -aG sudo dropship
apt update && apt -y upgrade
apt -y install ca-certificates curl git ufw python3
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  > /etc/apt/sources.list.d/docker.list
apt update && apt -y install docker-ce docker-ce-cli containerd.io
usermod -aG docker dropship
ufw allow OpenSSH && ufw --force enable
```

```bash
# 2. As dropship: code, secrets, image
su - dropship
git clone https://github.com/medchhoumat-ops/dropship-system.git && cd dropship-system
cp .env.example .env && nano .env && chmod 600 .env
mkdir -p data logs
docker build -t dropship-system:latest .

# 3. Smoke test (mock), then a real run
docker run --rm -e DROPSHIP_MOCK=1 dropship-system:latest research "dog lick mat"
docker run --rm --env-file .env -v "$PWD/data:/app/data" -v "$PWD/config:/app/config:ro" \
  dropship-system:latest niche --country US --seeds "pets,kitchen"
```

```bash
# 4. Weekly niche scan with cron (every market listed in config/settings.toml)
crontab -e
# paste the line from deploy/crontab.example, e.g.
# 17 5 * * 1  cd $HOME/dropship-system && ./deploy/weekly-niche.sh "pets,kitchen,home,fitness" >> logs/cron.log 2>&1
```

The script runs `dropship niche` for each configured market. It also deletes cache, runs and
reports older than 90 days.

**Reading the reports.** Copy them to your laptop:

```bash
scp -r dropship@YOUR_VPS:dropship-system/data/reports ./reports
```

You can also serve them privately, e.g. through an SSH tunnel
(`ssh -L 8080:localhost:8080 dropship@YOUR_VPS`, then
`python3 -m http.server 8080 -d data/reports` on the server). Don't expose the reports
publicly: they contain your supplier and pricing research.

**Updating.**

```bash
git pull && docker build -t dropship-system:latest .
```

**Without Docker.** `python3.11 -m venv .venv && .venv/bin/pip install .`, then point cron at
`.venv/bin/dropship` and set `DROPSHIP_DATA_DIR` and `DROPSHIP_CONFIG`.

---

## Development

```bash
pytest            # offline, mock fixtures
ruff check src tests
```

Layout:

```
src/dropship/
  cli.py  config.py  cache.py  http.py  models.py  pipeline.py  filters.py  pricing.py  utils.py
  research/ niche/ sourcing/ scoring/ competitors/ report/ creative/ fixtures/
config/settings.toml   deploy/   docs/pipeline.md   tests/
```

To add an API client, subclass `http.BaseClient`, implement `has_credentials()` and
`mock_response()`, pass secrets via `secret_params=`/`headers=` (never `params=`, which
becomes the cache key), and add a fixture plus a test.

**Before advertising any product, order a sample.** The scores are a shortlist, not a guarantee.
