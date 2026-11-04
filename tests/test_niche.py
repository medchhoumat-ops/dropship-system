from dropship.config import get_market
from dropship.niche import deep_search
from dropship.niche.expand import merge_ideas, seed_niches


def test_seed_niches():
    assert "dog enrichment" in seed_niches("pets")
    assert list(seed_niches("yoga")) == ["yoga"]
    assert seed_niches("aquarium") == {"aquarium": ["aquarium"]}


def test_merge_ideas_filters_junk():
    ideas = merge_ideas(["dog lick mat"], ["best dog lick mat", "dog lick mat amazon", "how to use lick mat",
                                           "silicone dog lick mat"], 10)
    assert ideas == ["dog lick mat", "silicone dog lick mat"]


def test_deep_search_top5(settings, clients):
    niches = deep_search(["pets", "kitchen"], get_market("US"), settings, clients)
    assert len(niches) == 5
    assert all(len(n.ideas) >= 4 for n in niches)
    scores = [n.score for n in niches]
    assert scores == sorted(scores, reverse=True)
    assert all(0 <= s <= 100 for s in scores)
    assert niches[0].price_median is not None
