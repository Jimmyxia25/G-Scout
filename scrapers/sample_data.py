"""Sample fallback data, used when live scraping is blocked/unavailable.

Keeps the end-to-end pipeline demoable even if anti-bot defenses block us.
These are representative placeholder products, not live prices.
"""
from models import Product

SAMPLE_PRODUCTS = [
    # --- REI ---
    Product("rei", "apparel", "Rab Microlight Alpine Down Jacket", "Rab",
            "https://www.rei.com/product/sample-rab-microlight", 199.93, 285.00),
    Product("rei", "footwear", "Salomon X Ultra 4 GTX Hiking Shoes", "Salomon",
            "https://www.rei.com/product/sample-salomon-xultra4", 119.83, 165.00),
    # --- Backcountry ---
    Product("backcountry", "apparel", "Patagonia Nano Puff Jacket", "Patagonia",
            "https://www.backcountry.com/sample-nano-puff", 174.30, 249.00),
    Product("backcountry", "footwear", "La Sportiva TX4 Approach Shoe", "La Sportiva",
            "https://www.backcountry.com/sample-tx4", 99.00, 159.00),
    # --- Steep & Cheap ---
    Product("steepandcheap", "apparel", "Arc'teryx Atom LT Hoody", "Arc'teryx",
            "https://www.steepandcheap.com/sample-atom-lt", 179.99, 300.00),
    Product("steepandcheap", "footwear", "Scarpa Zodiac Plus GTX Boot", "Scarpa",
            "https://www.steepandcheap.com/sample-zodiac-plus", 188.97, 329.00),
    # --- Public Lands ---
    Product("publiclands", "apparel", "The North Face Thermoball Eco Jacket", "The North Face",
            "https://www.publiclands.com/sample-thermoball", 159.97, 230.00),
    Product("publiclands", "footwear", "Merrell Moab 3 Mid WP Hiking Boot", "Merrell",
            "https://www.publiclands.com/sample-moab3", 104.97, 150.00),
]
