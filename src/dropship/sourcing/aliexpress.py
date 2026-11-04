"""AliExpress Open Platform – Drop Shipping API (product, freight, text search)."""

from __future__ import annotations

import copy
import hashlib
import hmac
import json
import time

from ..config import Market
from ..http import ApiError, BaseClient, load_fixture
from ..models import ShippingOption, SourcedProduct, Supplier, Variant, WarehouseStock
from ..utils import to_float
from .common import SHIP_FROM_NAMES, country_iso, mock_shipping

SECRET_PARAMS = ("app_key", "access_token", "timestamp", "sign_method", "sign")


def sign_params(params: dict, secret: str) -> str:
    """AliExpress /sync signature: HMAC-SHA256 over sorted key+value pairs, hex upper."""
    payload = "".join(f"{k}{params[k]}" for k in sorted(params) if k != "sign" and params[k] is not None)
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest().upper()


def _list(node, *path):
    for key in path:
        node = (node or {}).get(key) if isinstance(node, dict) else None
    if node is None:
        return []
    return node if isinstance(node, list) else [node]


class AliExpressClient(BaseClient):
    source = "aliexpress"
    URL = "https://api-sg.aliexpress.com/sync"
    min_interval = 0.25

    def has_credentials(self) -> bool:
        return self.settings.has_keys("AE_APP_KEY", "AE_APP_SECRET", "AE_ACCESS_TOKEN")

    def check(self, endpoint, data):
        if isinstance(data, dict) and "error_response" in data:
            e = data["error_response"]
            raise ApiError(f"aliexpress {endpoint}: {e.get('code')} {e.get('msg')}")

    def _api(self, method: str, business: dict) -> dict:
        business = {k: v for k, v in business.items() if v is not None}
        secrets = {"app_key": self.settings.key("AE_APP_KEY"),
                   "access_token": self.settings.key("AE_ACCESS_TOKEN"),
                   "timestamp": str(int(time.time() * 1000)), "sign_method": "sha256"}
        all_params = {"method": method, **business, **secrets}
        secrets["sign"] = sign_params(all_params, self.settings.key("AE_APP_SECRET"))
        return self.call(method, self.URL, {"method": method, **business}, method="POST",
                         secret_params=secrets)

    # --------------------------------------------------------------- endpoints
    def search(self, keyword: str, market: Market, size: int = 10) -> list[dict]:
        data = self._api("aliexpress.ds.text.search", {
            "keyWord": keyword, "local": "en_US", "countryCode": market.iso,
            "currency": "USD", "pageSize": size, "pageIndex": 1,
        })
        items = _list(data, "aliexpress_ds_text_search_response", "data", "products",
                      "selection_search_product")
        return [{"pid": str(i.get("itemId")), "title": i.get("title"),
                 "price": to_float(i.get("targetSalePrice")), "image": i.get("itemMainPic")}
                for i in items[:size]]

    def product(self, product_id: str, market: Market) -> dict:
        data = self._api("aliexpress.ds.product.get", {
            "product_id": product_id, "ship_to_country": market.iso,
            "target_currency": "USD", "target_language": "EN",
        })
        resp = data.get("aliexpress_ds_product_get_response") or {}
        if resp.get("rsp_code") not in (None, 200, "200"):
            raise ApiError(f"aliexpress product {product_id}: {resp.get('rsp_msg')}")
        return resp.get("result") or {}

    def freight(self, product_id: str, sku_id: str, market: Market,
                origin: str = "CN") -> list[ShippingOption]:
        req = {"quantity": 1, "shipToCountry": market.iso, "productId": product_id,
               "selectedSkuId": sku_id, "language": "en_US", "locale": "en_US",
               "currency": "USD", "source": "any"}
        data = self._api("aliexpress.ds.freight.query", {"queryDeliveryReq": json.dumps(req, sort_keys=True)})
        rows = _list(data, "aliexpress_ds_freight_query_response", "result", "delivery_options",
                     "delivery_option_d_t_o")
        out = []
        for r in rows:
            fee = 0.0 if str(r.get("free_shipping")).lower() == "true" else (
                to_float(r.get("shipping_fee_format")) or to_float(r.get("shipping_fee_cent"), 0.0))
            out.append(ShippingOption(
                method=r.get("company") or r.get("code") or "?",
                from_country=country_iso(r["ship_from_country"]) if r.get("ship_from_country") else origin,
                to_country=market.iso,
                cost=fee or 0.0, min_days=int(to_float(r.get("min_delivery_days"), 0)) or None,
                max_days=int(to_float(r.get("max_delivery_days"), 0)) or None))
        return out

    # --------------------------------------------------------------- assembly
    def sourced_product(self, product_id: str, market: Market, *, deep: bool = True) -> SourcedProduct:
        r = self.product(product_id, market)
        if not r:
            raise ApiError(f"aliexpress: product {product_id} not found")
        base = r.get("ae_item_base_info_dto") or {}
        store = r.get("ae_store_info") or {}
        skus = _list(r, "ae_item_sku_info_dtos", "ae_item_sku_info_d_t_o")

        # Collapse "Ships From" into warehouses: it is NOT a customer-facing variant.
        variants: dict[tuple, Variant] = {}
        stock: dict[str, int] = {}
        sku_by_origin: dict[str, str] = {}
        for s in skus:
            props = _list(s, "ae_sku_property_dtos", "ae_sku_property_d_t_o")
            origin = "CN"
            attrs = {}
            for prop in props:
                name = (prop.get("sku_property_name") or "").strip()
                value = prop.get("property_value_definition_name") or prop.get("sku_property_value") or ""
                if name.lower() in SHIP_FROM_NAMES:
                    origin = country_iso(value)
                else:
                    attrs[name] = value
            qty = int(to_float(s.get("sku_available_stock"), 0) or 0)
            stock[origin] = stock.get(origin, 0) + qty
            sku_by_origin.setdefault(origin, str(s.get("sku_id")))
            key = tuple(sorted(attrs.items()))
            price = to_float(s.get("offer_sale_price")) or to_float(s.get("sku_price"))
            if key not in variants:
                variants[key] = Variant(vid=str(s.get("sku_id")), sku=s.get("sku_attr") or "",
                                        name=", ".join(f"{k}: {v}" for k, v in attrs.items()) or "default",
                                        price=price, attributes=attrs)
            elif price and (variants[key].price is None or price < variants[key].price):
                variants[key].price = price
        images = (r.get("ae_multimedia_info_dto") or {}).get("image_urls", "")
        store_id = store.get("store_id")
        prices = [v.price for v in variants.values() if v.price]
        p = SourcedProduct(
            platform="aliexpress", product_id=str(base.get("product_id") or product_id),
            title=base.get("subject") or "", price=min(prices) if prices else None,
            url=f"https://www.aliexpress.com/item/{product_id}.html",
            image=images.split(";")[0] if images else None, category=str(base.get("category_id") or ""),
            variants=list(variants.values()),
            stock=[WarehouseStock(country=c, name=f"Ships from {c}", quantity=q) for c, q in stock.items()],
            supplier=Supplier(platform="aliexpress", name=store.get("store_name") or "AliExpress seller",
                              store_id=str(store_id) if store_id else None,
                              url=f"https://www.aliexpress.com/store/{store_id}" if store_id else None,
                              contact_url=f"https://www.aliexpress.com/store/{store_id} (Message seller)"
                              if store_id else None),
        )
        if not deep:
            return p
        if len(p.variants) > 1 and self.settings.single_variant_only:
            p.errors.append("multi-variant: freight lookups skipped")
            return p
        for origin, sku_id in sku_by_origin.items():
            if stock.get(origin, 0) <= 0:
                continue
            if origin != "CN" and origin not in market.warehouse_countries:
                continue
            try:
                p.shipping.extend(self.freight(p.product_id, sku_id, market, origin))
            except ApiError as exc:
                p.errors.append(str(exc))
        return p

    # --------------------------------------------------------------- mock
    def mock_response(self, endpoint, params):
        if endpoint == "aliexpress.ds.text.search":
            data = load_fixture("ae_text_search.json")
            kw = params.get("keyWord", "")
            for i in _list(data, "aliexpress_ds_text_search_response", "data", "products",
                           "selection_search_product"):
                i["title"] = i["title"].replace("{Keyword}", kw.title())
            return data
        if endpoint == "aliexpress.ds.product.get":
            d = copy.deepcopy(load_fixture("ae_product_get.json").get(str(params.get("product_id"))))
            if d is None:
                return {"error_response": {"code": "ProductNotFound", "msg": "product not found"}}
            res = d["aliexpress_ds_product_get_response"]["result"]
            res["ae_item_base_info_dto"]["subject"] = res["ae_item_base_info_dto"]["subject"].replace(
                "{Keyword}", "Mock Product")
            return d
        if endpoint == "aliexpress.ds.freight.query":
            req = json.loads(params["queryDeliveryReq"])
            sku = str(req["selectedSkuId"])
            origin = {"12000000000000001": "US", "12000000000000003": "ES"}.get(sku, "CN")
            opts = [{"code": r["method"].upper().replace(" ", "_"), "company": f"AliExpress {r['method']}",
                     "shipping_fee_cent": f"{r['cost'] - 0.8:.2f}", "shipping_fee_currency": "USD",
                     "shipping_fee_format": f"${r['cost'] - 0.8:.2f}", "free_shipping": False,
                     "min_delivery_days": r["min"], "max_delivery_days": r["max"],
                     "ship_from_country": origin}
                    for r in mock_shipping(origin, req["shipToCountry"])]
            return {"aliexpress_ds_freight_query_response": {"result": {
                "success": True, "delivery_options": {"delivery_option_d_t_o": opts}}}}
        raise KeyError(endpoint)
