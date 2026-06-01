"""Shared data model for a scraped product."""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Product:
    site: str            # site key, e.g. "rei"
    category: str        # category key, e.g. "apparel"
    name: str
    brand: Optional[str]
    url: str
    price: Optional[float]        # current price (sale price if discounted)
    list_price: Optional[float]   # original / MSRP
    currency: str = "USD"

    @property
    def discount_pct(self) -> Optional[int]:
        if self.price is None or self.list_price is None:
            return None
        if self.list_price <= 0 or self.price >= self.list_price:
            return 0
        return round((self.list_price - self.price) / self.list_price * 100)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["discount_pct"] = self.discount_pct
        return d
