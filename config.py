"""Central config: sites to scrape and product categories."""

# Categories we care about right now.
CATEGORIES = {
    "apparel": "服装 (冲锋衣/羽绒服/保暖层)",
    "footwear": "鞋类 (徒步鞋/登山靴/越野跑鞋)",
}

# Site registry. `kind` distinguishes price sources from review/导购 sources.
#   price  -> e-commerce, has its own prices & discounts
#   review -> editorial/导购 site, links out to retailers
SITES = {
    "rei": {
        "name": "REI",
        "kind": "price",
        "base_url": "https://www.rei.com",
    },
    "backcountry": {
        "name": "Backcountry",
        "kind": "price",
        "base_url": "https://www.backcountry.com",
    },
    "steepandcheap": {
        "name": "Steep & Cheap",
        "kind": "price",
        "base_url": "https://www.steepandcheap.com",
    },
    "publiclands": {
        "name": "Public Lands",
        "kind": "price",
        "base_url": "https://www.publiclands.com",
    },
    "switchback": {
        "name": "Switchback Travel",
        "kind": "review",
        "base_url": "https://www.switchbacktravel.com",
    },
}
