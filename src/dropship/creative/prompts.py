"""Creative briefs per product.

* 4 Google Flow image prompts: worn/in use, in hand, flat lay, macro.
* 3 UGC video scripts (hook, problem, demo, CTA).

Rules baked in: no fake reviews or testimonials, no invented statistics, no
medical/health or "guaranteed" claims, no fake scarcity, no before/after
promises the product can't prove. Scripts are for real creators filming the
real product after receiving a sample.
"""

from __future__ import annotations

import re

from ..config import Market

BANNED_PHRASES = (
    "guaranteed", "cure", "clinically proven", "doctor recommended", "#1", "best seller",
    "5-star", "five star", "thousands of happy", "customers love", "100% safe", "miracle",
    "only today", "last chance", "fda approved",
)

SETTINGS_BY_MARKET = {
    "US": "a bright American suburban home",
    "UK": "a cosy British terraced-house interior",
    "CA": "a bright Canadian home with natural wood",
    "FR": "an airy Parisian apartment with natural light",
    "DE": "a clean, minimal German apartment",
}

STYLE = ("photorealistic, natural daylight, shot on a 35mm lens, shallow depth of field, "
         "true-to-life colours, no text, no logos, no watermarks")


def _clean_name(title: str) -> str:
    name = re.sub(r"\s+", " ", re.sub(r"[^\w\s&'-]", " ", title)).strip()
    words = name.split()
    return " ".join(words[:7]) if words else "the product"


def image_prompts(name: str, keyword: str, niche: str, market: Market) -> list[dict[str, str]]:
    place = SETTINGS_BY_MARKET.get(market.code, "a bright modern home")
    return [
        {"angle": "worn / in use",
         "prompt": f"A person using the {name} naturally in {place}, mid-action, candid lifestyle "
                   f"moment that shows what a {keyword} is for, product clearly visible and in focus, "
                   f"{STYLE}."},
        {"angle": "in hand",
         "prompt": f"Close-up of a hand holding the {name} at chest height, neutral background slightly "
                   f"blurred, true scale visible, clean nails, soft window light, {STYLE}."},
        {"angle": "flat lay",
         "prompt": f"Top-down flat lay of the {name} on a light linen surface with 3–4 everyday "
                   f"{niche} items arranged around it, generous negative space for ad copy, {STYLE}."},
        {"angle": "macro",
         "prompt": f"Macro detail shot of the {name} showing material texture, finish and build quality, "
                   f"edge-lit, crisp focus on the key functional part, {STYLE}."},
    ]


def ugc_scripts(name: str, keyword: str, market: Market) -> list[dict[str, str]]:
    return [
        {"title": "Problem → solution demo (20–30 s)",
         "hook": f"\"If you deal with this every day, watch how I handle it now.\" (show the mess/problem "
                 f"in the first second)",
         "problem": f"Show the real, everyday frustration that a {keyword} solves – filmed honestly, "
                    "no exaggeration.",
         "demo": f"Unbox and use the {name} in one continuous take; show set-up, use and clean-up. "
                 "Say only what you actually observed.",
         "cta": "\"Link's on the page if you want one – check the details there.\""},
        {"title": "3 things I noticed (25–35 s)",
         "hook": f"\"I tried the {name} for a week – here are three things I noticed.\"",
         "problem": "Briefly explain why you were looking for something like this.",
         "demo": "Point 1: how it's used. Point 2: a detail you liked (close-up). Point 3: something "
                 "to know before buying (honest limitation, e.g. size or care instructions).",
         "cta": "\"If that fits how you'd use it, it's linked here.\""},
        {"title": "Gift / routine angle (15–20 s)",
         "hook": f"\"Small upgrade to my routine that I didn't know I needed.\" (product in hand)",
         "problem": "Show the old way of doing the task in 2–3 quick cuts.",
         "demo": f"Show the {name} in your routine in {market.name} – real home, real lighting, "
                 "natural voice. Mention it could be a gift idea only if relevant.",
         "cta": "\"Have a look at the page – shipping times and returns are listed there.\""},
    ]


def creative_pack(title: str, keyword: str, niche: str, market: Market) -> dict:
    name = _clean_name(title)
    pack = {
        "image_prompts": image_prompts(name, keyword, niche or keyword, market),
        "ugc_scripts": ugc_scripts(name, keyword, market),
        "rules": [
            "Film the real product from a sample order; never use supplier photos as 'UGC'.",
            "No fake reviews, testimonials, ratings or follower counts.",
            "No health, medical, safety or performance claims you can't document.",
            "No fake urgency (countdown timers, 'only 3 left') unless true.",
            "Disclose paid partnerships (#ad) when a creator is paid or gifted.",
        ],
    }
    return pack
