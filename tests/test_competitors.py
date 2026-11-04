from dropship.competitors import analyze_competitors, competitor_domains
from dropship.competitors.analyze import parse_refund_days, parse_shipping_policy
from dropship.competitors.shopify import detect_theme
from dropship.config import get_market


def test_detect_theme():
    html = 'Shopify.theme = {"name":"My copy","schema_name":"Impulse","id":1};'
    assert detect_theme(html) == "Impulse"
    assert detect_theme("<html></html>") is None


def test_policy_parsing():
    days, threshold, free = parse_shipping_policy(
        "Processed in 1-2 business days. Delivery 5 to 9 business days. Free shipping on orders over $35.")
    assert days == (5, 9) and threshold == 35 and free
    assert parse_refund_days("You have a 30-day return window") == 30


def test_analyze_mock(clients):
    shopping = clients.serpapi.shopping("dog lick mat", get_market("US"))
    domains = [d for d, _ in competitor_domains(shopping, ["https://www.extra-store.com/"])]
    assert domains[0] == "extra-store.com"
    assert not any("amazon" in d or "walmart" in d for d in domains)
    stores = analyze_competitors(clients.shopify, shopping, "mock product", our_price=34.99)
    assert stores and all(s.is_shopify for s in stores)
    s = stores[0]
    assert s.theme == "Dawn" and s.faq_found and s.refund_days == 30
    assert s.free_shipping_threshold == 35
    assert s.strengths and s.gaps
