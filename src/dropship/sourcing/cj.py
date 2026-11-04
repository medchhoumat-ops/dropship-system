"""CJ Dropshipping API v2 client (max 1 request/second)."""

from __future__ import annotations

import copy
import json
import re

from ..config import Market
from ..http import ApiError, BaseClient, load_fixture
from ..models import ShippingOption, SourcedProduct, Supplier, Variant, WarehouseStock
from ..utils import parse_days, seeded_rng, to_float
from .common import country_iso, mock_shipping


class CJClient(BaseClient):
    source = "cj"
    BASE = "https://developers.cjdropshipping.com/api2.0/v1"
    min_interval = 1.05  # CJ: 1 request / second

    def has_credentials(self) -> bool:
        return self.settings.has_keys("CJ_MCP_TOKEN")

    def check(self, endpoint, data):
        if isinstance(data, dict) and data.get("result") is False:
            raise ApiError(f"cj {endpoint}: {data.get('code')} {data.get('message')}")

    def _api(self, endpoint: str, params: dict | None = None, body: dict | None = None):
        data = self.call(
            endpoint, f"{self.BASE}/{endpoint}", params,
            method="POST" if body is not None else "GET", json_body=body,
            headers={"CJ-Access-Token": self.settings.key("CJ_MCP_TOKEN"),
                     "Content-Type": "application/json"},
        )
        return data.get("data") if isinstance(data, dict) else None

    # --------------------------------------------------------------- endpoints
    def search(self, keyword: str, size: int = 10) -> list[dict]:
        data = self._api("product/listV2", {"keyWord": keyword, "page": 1, "size": size}) or {}
        items: list[dict] = []
        for block in data.get("content") or []:
            items.extend(block.get("productList") or [])
        items.extend(data.get("list") or [])  # legacy product/list shape
        return [{"pid": i.get("id") or i.get("pid"),
                 "title": i.get("nameEn") or i.get("productNameEn"),
                 "price": to_float(i.get("sellPrice")), "image": i.get("bigImage") or i.get("productImage")}
                for i in items[:size] if i.get("id") or i.get("pid")]

    def product(self, pid: str) -> dict:
        return self._api("product/query", {"pid": pid}) or {}

    def stock(self, vid: str) -> list[WarehouseStock]:
        rows = self._api("product/stock/queryByVid", {"vid": vid}) or []
        out = []
        for r in rows:
            qty = r.get("totalInventoryNum", r.get("storageNum", r.get("cjInventoryNum", 0)))
            out.append(WarehouseStock(country=country_iso(r.get("countryCode") or r.get("countryNameEn")),
                                      name=r.get("areaEn") or "", quantity=int(to_float(qty, 0) or 0)))
        return out

    def freight(self, vid: str, start: str, end: str) -> list[ShippingOption]:
        body = {"startCountryCode": start, "endCountryCode": end,
                "products": [{"quantity": 1, "vid": vid}]}
        rows = self._api("logistic/freightCalculate", body=body) or []
        out = []
        for r in rows:
            lo, hi = parse_days(r.get("logisticAging"))
            out.append(ShippingOption(method=r.get("logisticName", "?"), from_country=start, to_country=end,
                                      cost=to_float(r.get("logisticPrice"), 0.0) or 0.0,
                                      min_days=lo, max_days=hi))
        return out

    # --------------------------------------------------------------- assembly
    def sourced_product(self, pid: str, market: Market, *, deep: bool = True) -> SourcedProduct:
        d = self.product(pid)
        if not d:
            raise ApiError(f"cj: product {pid} not found")
        variants = []
        for v in d.get("variants") or []:
            attrs = {}
            keys = [k for k in re.split(r"[-/]", d.get("productKeyEn") or "") if k]
            vals = [x for x in re.split(r"[-/]", v.get("variantKey") or "") if x]
            attrs = dict(zip(keys or [f"option{i + 1}" for i in range(len(vals))], vals))
            variants.append(Variant(vid=v.get("vid", ""), sku=v.get("variantSku", ""),
                                    name=v.get("variantNameEn") or "", attributes=attrs,
                                    price=to_float(v.get("variantSellPrice")),
                                    weight_g=to_float(v.get("variantWeight"))))
        images = d.get("productImage")
        if isinstance(images, str) and images.startswith("["):
            images = json.loads(images)
        image = images[0] if isinstance(images, list) and images else images
        prices = [v.price for v in variants if v.price] or [to_float(d.get("sellPrice"))]
        title = d.get("productNameEn") or ""
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        p = SourcedProduct(
            platform="cj", product_id=str(d.get("pid") or pid), title=title,
            price=min(x for x in prices if x is not None) if any(prices) else None,
            url=f"https://cjdropshipping.com/product/{slug}-p-{d.get('pid') or pid}.html",
            image=image, category=d.get("categoryName"), variants=variants,
            supplier=Supplier(platform="cj", name=d.get("supplierName") or "CJ Dropshipping",
                              store_id=d.get("supplierId"), url="https://cjdropshipping.com",
                              contact_url="https://cjdropshipping.com/ (CJ app > Messages / your CJ agent)"),
        )
        if not deep or not variants:
            return p
        if len(variants) > 1 and self.settings.single_variant_only:
            p.errors.append("multi-variant: stock/freight lookups skipped to save CJ rate limit")
            return p
        vid = variants[0].vid
        try:
            p.stock = self.stock(vid)
            origins = {s.country for s in p.stock if s.quantity > 0} or {"CN"}
            for origin in sorted(origins):
                if origin != "CN" and origin not in market.warehouse_countries:
                    continue
                p.shipping.extend(self.freight(vid, origin, market.iso))
        except ApiError as exc:
            p.errors.append(str(exc))
        return p

    # --------------------------------------------------------------- mock
    def mock_response(self, endpoint, params):
        ok = lambda data: {"code": 200, "result": True, "message": "Success", "data": data}  # noqa: E731
        if endpoint == "product/listV2":
            data = load_fixture("cj_listV2.json")
            kw = params.get("keyWord", "")
            for item in data["data"]["content"][0]["productList"]:
                item["nameEn"] = item["nameEn"].replace("{Keyword}", kw.title())
            data["data"]["content"][0]["keyWord"] = kw
            return data
        if endpoint == "product/query":
            products = load_fixture("cj_query.json")
            d = copy.deepcopy(products.get(str(params.get("pid"))))
            if d is None:
                return {"code": 1600100, "result": False, "message": "Product not found", "data": None}
            kw = "mock product"
            d["productNameEn"] = d["productNameEn"].replace("{Keyword}", kw.title())
            factor = seeded_rng("cj", d["pid"]).uniform(0.92, 1.08)
            for v in d["variants"]:
                v["variantNameEn"] = v["variantNameEn"].replace("{Keyword}", kw.title())
                v["variantSellPrice"] = round(v["variantSellPrice"] * factor, 2)
            return ok(d)
        if endpoint == "product/stock/queryByVid":
            return ok(load_fixture("cj_stock.json").get(params.get("vid"), []))
        if endpoint == "logistic/freightCalculate":
            body = params["body"]
            rows = [{"logisticName": f"CJ {r['method']}", "logisticPrice": r["cost"],
                     "logisticAging": f"{r['min']}-{r['max']}"}
                    for r in mock_shipping(body["startCountryCode"], body["endCountryCode"])]
            return ok(rows)
        raise KeyError(endpoint)
