from dropship.config import get_market
from dropship.research import research_keyword
from dropship.research.amazon import parse_amazon_item
from dropship.research.semrush import parse_semrush_csv
from dropship.research.serpapi import is_marketplace, monthly_buckets, offer_domain
from dropship.research.service import trend_change


def test_parse_semrush():
    text = ("Keyword;Search Volume;CPC;Competition;Number of Results;Trends\n"
            "dog lick mat;12100;0.85;1.00;4100000;0.54,0.66,1.00\n")
    rows = parse_semrush_csv(text)
    assert rows[0].keyword == "dog lick mat"
    assert rows[0].volume == 12100 and rows[0].competition == 1.0
    assert rows[0].trend == [0.54, 0.66, 1.0]
    assert parse_semrush_csv("ERROR 50 :: NOTHING FOUND") == []


def test_trend_change():
    assert trend_change([1, 1, 1, 0, 0, 0, 0, 0, 0, 2, 2, 2]) == 1.0
    assert trend_change([1, 2]) == 0.0


def test_monthly_buckets():
    timeline = [{"values": [{"extracted_value": v}]} for v in range(52)]
    b = monthly_buckets(timeline)
    assert len(b) == 12 and b[-1] == 1.0 and b[0] < b[-1]


def test_offer_domain():
    assert offer_domain("https://www.shop.com/products/x") == "shop.com"
    assert offer_domain("https://www.google.com/url?url=https://store.co/p") == "store.co"
    assert offer_domain("https://www.google.com/shopping/product/1") is None
    assert is_marketplace("amazon.com") and not is_marketplace("pawsomesupply.com", "Pawsome")


def test_parse_amazon_item_shapes():
    a = parse_amazon_item({"title": "x", "price": {"value": 19.9}, "stars": 4.5, "reviewsCount": 10,
                           "bestsellerRanks": [{"rank": 900, "category": "Pets"}, {"rank": 12, "category": "Sub"}],
                           "seller": {"name": "S"}})
    assert (a.price, a.rating, a.reviews, a.bsr, a.seller) == (19.9, 4.5, 10, 12, "S")
    b = parse_amazon_item({"title": "y", "price": "$1,299.00", "rating": "4.1 out of 5", "bsr": "#2,345"})
    assert b.price == 1299.0 and b.rating == 4.1 and b.bsr == 2345


def test_research_keyword_mock(settings, clients):
    r = research_keyword("dog lick mat", get_market("US"), settings, clients)
    assert r.volume > 0 and len(r.trend) == 12
    assert r.amazon.count > 0 and r.amazon.price_median
    assert r.shopping.sellers > 0
    # deterministic mocks
    r2 = research_keyword("dog lick mat", get_market("US"), settings, clients)
    assert r2.volume == r.volume and r2.trend == r.trend


def test_google_trends_option(settings, clients):
    settings.use_google_trends = True
    r = research_keyword("yoga wheel", get_market("DE"), settings, clients, amazon=False, shopping=False)
    assert r.trend_source == "google_trends" and len(r.trend) == 12
