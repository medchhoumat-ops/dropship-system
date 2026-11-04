import math

import pytest

from dropship.config import get_market
from dropship.filters import evaluate, is_single_variant
from dropship.models import ShippingOption, SourcedProduct, Variant, WarehouseStock
from dropship.pricing import multiplier_for, price_product, round_99


def make(price=4.0, variants=1, stock=(("US", 100),), ship=(("US", 3.5, 2, 5),)):
    return SourcedProduct(
        platform="cj", product_id="p", title="Thing", price=price,
        variants=[Variant(vid=f"v{i}", name=f"v{i}", attributes={"Color": str(i)} if variants > 1 else {})
                  for i in range(variants)],
        stock=[WarehouseStock(c, quantity=q) for c, q in stock],
        shipping=[ShippingOption("m", c, "US", cost, lo, hi) for c, cost, lo, hi in ship],
    )


def test_pass(settings):
    r = evaluate(make(), get_market("US"), settings)
    assert r.passed and r.landed_cost == 7.5 and r.warehouse == "US"


def test_multi_variant_fails(settings):
    r = evaluate(make(variants=3), get_market("US"), settings)
    assert not r.passed and "variants" in r.failures[0]


def test_same_attributes_count_as_single():
    p = make(variants=1)
    p.variants = [Variant("a", name="x"), Variant("b", name="x")]
    assert is_single_variant(p)


def test_stock_only_in_china_fails(settings):
    r = evaluate(make(stock=(("CN", 999),), ship=(("CN", 2.0, 8, 15),)), get_market("US"), settings)
    assert not r.passed
    assert any("no stock" in f for f in r.failures)
    assert any("10 days" in f for f in r.failures)


def test_near_warehouse_ok_for_eu(settings):
    p = make(stock=(("DE", 50),), ship=(("DE", 5.0, 4, 9),))
    assert evaluate(p, get_market("FR"), settings).passed
    assert not evaluate(p, get_market("US"), settings).passed


def test_slow_shipping_fails(settings):
    r = evaluate(make(ship=(("US", 3.0, 7, 12),)), get_market("US"), settings)
    assert not r.passed


@pytest.mark.parametrize("price,ok", [(0.5, False), (2.0, True), (11.0, True), (12.0, False)])
def test_landed_range(settings, price, ok):
    assert evaluate(make(price=price), get_market("US"), settings).passed is ok


def test_picks_cheapest_fast_method(settings):
    p = make(ship=(("US", 6.0, 1, 3), ("US", 3.0, 4, 8), ("US", 1.0, 9, 14)))
    r = evaluate(p, get_market("US"), settings)
    assert r.shipping.cost == 3.0


def test_round_99():
    assert round_99(37.2) == 36.99
    assert round_99(37.6) == 37.99
    assert round_99(0.4) == 0.99


def test_multiplier_scales(settings):
    assert multiplier_for(5, settings) == 5.0
    assert multiplier_for(15, settings) == 4.0
    assert 4.0 < multiplier_for(10, settings) < 5.0


def test_pricing_math(settings):
    p = price_product(8.0, settings, get_market("UK"))
    assert str(p.price).endswith(".99")
    assert 4 * 8.0 - 1 <= p.price <= 5 * 8.0 + 1
    assert p.fees == round(p.price * 0.029 + 0.30, 2)
    assert p.profit == round(p.price - 8.0 - p.fees, 2)
    assert p.breakeven_cpa == p.profit
    assert math.isclose(p.breakeven_roas, round(p.price / p.profit, 2))
    assert p.local_currency == "GBP" and str(p.local_price).endswith(".99")
