from dropship.config import get_market
from dropship.creative import BANNED_PHRASES, creative_pack
from dropship.filters import FilterResult
from dropship.models import KeywordResearch, ShippingOption, SourcedProduct, Variant
from dropship.pricing import price_product
from dropship.scoring import WEIGHTS, score_product, write_pick


def _inputs(settings, volume=20000, change=0.3, days=5):
    research = KeywordResearch("dog lick mat", "US", volume=volume, competition=0.3, trend_change=change)
    filt = FilterResult(passed=True, shipping=ShippingOption("x", "US", "US", 3.0, 2, days), landed_cost=8.0)
    return research, price_product(8.0, settings), filt


def test_weights_sum_to_100():
    assert sum(WEIGHTS.values()) == 100


def test_score_bounds_and_ordering(settings):
    good = score_product(*_inputs(settings), competitor_stores=5)
    bad = score_product(*_inputs(settings, volume=50, change=-0.4, days=10), competitor_stores=40)
    assert 0 <= bad.total < good.total <= 100
    assert set(good.components) == set(WEIGHTS)


def test_failed_filters_are_penalised(settings):
    r, p, f = _inputs(settings)
    ok = score_product(r, p, f).total
    f.passed = False
    assert score_product(r, p, f).total == round(ok * 0.5, 1)


def test_narrative(settings):
    r, p, f = _inputs(settings)
    prod = SourcedProduct("cj", "1", "Lick Mat", 5.0, variants=[Variant("v")])
    text = write_pick(prod, r, p, score_product(r, p, f), f, get_market("US"))
    assert text["why"] and text["risks"] and len(text["scale"]) >= 4
    assert any("Bundle" in s for s in text["scale"])
    assert any("UK" in s for s in text["scale"])  # more markets


def test_creative_pack():
    pack = creative_pack("Silicone Dog Lick Mat!!", "dog lick mat", "dog enrichment", get_market("FR"))
    angles = [p["angle"] for p in pack["image_prompts"]]
    assert angles == ["worn / in use", "in hand", "flat lay", "macro"]
    assert len(pack["ugc_scripts"]) == 3
    for s in pack["ugc_scripts"]:
        assert {"hook", "problem", "demo", "cta"} <= set(s)
    blob = str(pack["image_prompts"]) + str(pack["ugc_scripts"])
    assert not [b for b in BANNED_PHRASES if b in blob.lower()]
    assert "Parisian" in pack["image_prompts"][0]["prompt"]
