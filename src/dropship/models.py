"""Plain dataclasses shared across modules (serialised with utils.to_jsonable)."""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------- research
@dataclass
class KeywordMetrics:
    keyword: str
    volume: int = 0
    cpc: float = 0.0
    competition: float = 0.0  # 0..1 (Semrush paid competition density)
    results: int = 0
    trend: list[float] = field(default_factory=list)  # 12 monthly values, oldest -> newest


@dataclass
class AmazonProduct:
    title: str
    asin: str | None = None
    price: float | None = None
    rating: float | None = None
    reviews: int | None = None
    bsr: int | None = None
    bsr_category: str | None = None
    seller: str | None = None
    offers: int | None = None
    url: str | None = None


@dataclass
class AmazonSummary:
    domain: str
    count: int = 0
    price_min: float | None = None
    price_median: float | None = None
    price_max: float | None = None
    rating_avg: float | None = None
    reviews_median: float | None = None
    reviews_total: int = 0
    best_bsr: int | None = None
    sellers: int = 0  # distinct sellers on page 1
    offers_total: int = 0
    products: list[AmazonProduct] = field(default_factory=list)


@dataclass
class ShoppingOffer:
    title: str
    source: str  # merchant / store name
    price: float | None = None
    rating: float | None = None
    reviews: int | None = None
    link: str | None = None
    domain: str | None = None


@dataclass
class ShoppingSummary:
    count: int = 0
    sellers: int = 0
    price_min: float | None = None
    price_median: float | None = None
    price_max: float | None = None
    offers: list[ShoppingOffer] = field(default_factory=list)


@dataclass
class KeywordResearch:
    keyword: str
    country: str
    volume: int = 0
    cpc: float = 0.0
    competition: float = 0.0
    trend: list[float] = field(default_factory=list)
    trend_source: str = "semrush"
    trend_change: float = 0.0  # last-3-month avg vs first-3-month avg (-1..+inf)
    amazon: AmazonSummary | None = None
    shopping: ShoppingSummary | None = None
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------- sourcing
@dataclass
class Variant:
    vid: str
    sku: str = ""
    name: str = ""
    price: float | None = None
    attributes: dict[str, str] = field(default_factory=dict)
    weight_g: float | None = None


@dataclass
class WarehouseStock:
    country: str  # ISO alpha-2
    name: str = ""
    quantity: int = 0


@dataclass
class ShippingOption:
    method: str
    from_country: str
    to_country: str
    cost: float
    min_days: int | None = None
    max_days: int | None = None


@dataclass
class Supplier:
    platform: str
    name: str
    store_id: str | None = None
    url: str | None = None
    contact_url: str | None = None


@dataclass
class SourcedProduct:
    platform: str  # "cj" | "aliexpress"
    product_id: str
    title: str
    price: float | None  # unit cost in USD (cheapest variant)
    url: str | None = None
    image: str | None = None
    category: str | None = None
    variants: list[Variant] = field(default_factory=list)
    stock: list[WarehouseStock] = field(default_factory=list)
    shipping: list[ShippingOption] = field(default_factory=list)
    supplier: Supplier | None = None
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------- competitors
@dataclass
class CompetitorStore:
    domain: str
    source_name: str = ""
    is_shopify: bool = False
    theme: str | None = None
    product_count: int = 0
    matching_products: int = 0
    price_min: float | None = None
    price_median: float | None = None
    price_max: float | None = None
    images_avg: float | None = None
    faq_found: bool = False
    faq_questions: int = 0
    shipping_policy: str | None = None  # short excerpt
    shipping_days: tuple[int | None, int | None] | None = None
    free_shipping_threshold: float | None = None
    free_shipping: bool = False
    refund_days: int | None = None
    strengths: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
