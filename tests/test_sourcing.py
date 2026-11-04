import pytest

from dropship.config import get_market
from dropship.sourcing import detect_query, source_products
from dropship.sourcing.aliexpress import sign_params


@pytest.mark.parametrize("query,expected", [
    ("dog lick mat", ("keyword", "dog lick mat")),
    ("cj:ABC", ("cj", "ABC")),
    ("ae:1005006000000001", ("aliexpress", "1005006000000001")),
    ("1005006000000001", ("aliexpress", "1005006000000001")),
    ("1720000000000000001", ("cj", "1720000000000000001")),
    ("04A22450-67F0-4617-A132-E7AE7F8963B0", ("cj", "04A22450-67F0-4617-A132-E7AE7F8963B0")),
    ("https://www.aliexpress.com/item/1005001234567890.html", ("aliexpress", "1005001234567890")),
])
def test_detect_query(query, expected):
    assert detect_query(query) == expected


def test_ae_signature_is_deterministic():
    p = {"method": "aliexpress.ds.product.get", "app_key": "123", "timestamp": "1", "product_id": "9"}
    sig = sign_params(p, "secret")
    assert sig == sign_params(dict(reversed(list(p.items()))), "secret")
    assert sig.isupper() and len(sig) == 64
    assert sign_params({**p, "sign": "IGNORED"}, "secret") == sig


def test_cj_product_details(clients):
    us = get_market("US")
    p = clients.cj.sourced_product("1720000000000000001", us)
    assert p.platform == "cj" and len(p.variants) == 1
    assert {s.country for s in p.stock} >= {"US", "CN"}
    assert any(o.from_country == "US" and o.max_days <= 10 for o in p.shipping)
    assert p.supplier.name and p.supplier.contact_url
    multi = clients.cj.sourced_product("1720000000000000002", us)
    assert len(multi.variants) == 3 and multi.variants[0].attributes == {"Color": "Red"}


def test_ae_ships_from_is_not_a_variant(clients):
    p = clients.aliexpress.sourced_product("1005006000000001", get_market("US"))
    assert len(p.variants) == 1
    assert {s.country: s.quantity for s in p.stock} == {"US": 230, "CN": 4800, "ES": 150}
    assert p.origin_prices["US"] == 5.10 and p.origin_prices["CN"] == 4.60
    assert any(o.from_country == "US" for o in p.shipping)
    assert p.supplier.name == "Mock Home Official Store"
    assert "aliexpress.com/store/1100000001" in p.supplier.url


def test_source_keyword_both_platforms(clients):
    products = source_products("dog lick mat", get_market("US"), clients, limit=5)
    assert {p.platform for p in products} == {"cj", "aliexpress"}
    assert len(products) == 8
