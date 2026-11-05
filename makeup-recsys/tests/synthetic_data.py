"""
Pembuat data SINTETIS untuk pengujian otomatis.

Data ini BUKAN data asli Kaggle. Skemanya meniru `cleaned_makeup_products.csv`
(termasuk artefak scraping seperti brand "Find your shade" dan kategori kosong)
agar kode bisa diuji tanpa mengunduh dataset.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

CATEGORIES = {
    "Foundation": ["liquid foundation full coverage matte finish oil control",
                   "dewy foundation hydrating serum skin tint glow"],
    "Concealer": ["creamy concealer covers dark circles under eye brightening",
                  "full coverage waterproof concealer blemish spot cover"],
    "Blush": ["soft blush powder pigmented cheeks natural flush",
              "liquid cheek tint blush buildable rosy glow"],
    "Highlighter": ["shimmer highlighter glow cheekbones luminous",
                    "baked highlighter radiant sheen face glow"],
    "Face Primer": ["pore minimizing primer smooth base makeup grip",
                    "hydrating primer mattifying long wear base"],
}
BRANDS = ["Glowly", "PureSkin", "Velvette", "Lumora", "Bloomie", "CoverPro"]


def make_raw_products(n_per_category: int = 14, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows, pid = [], 1
    for cat, phrases in CATEGORIES.items():
        for i in range(n_per_category):
            brand = BRANDS[(pid + i) % len(BRANDS)]
            phrase = phrases[i % len(phrases)]
            name = f"{phrase.split()[0].title()} {cat} No.{pid}"
            desc = (
                "Use the following zoom and pan buttons to control the image that "
                "follows them Tab through the images or use the previous or next "
                f"buttons to navigate each product image {brand} {name} Item {1000 + pid} "
                f"Summary {brand} {name} is a {phrase}. Details Benefits {phrase} "
                "How To Use Apply evenly. Ingredients Water, Glycerin. "
                "Shipping & Coupon Restrictions none"
            )
            # Sisipkan artefak scraping seperti pada data asli.
            stored_brand = brand
            if pid % 9 == 0:
                stored_brand = "Find your shade"
            elif pid % 11 == 0:
                stored_brand = np.nan
            rcount = int(rng.integers(0, 500))
            rows.append({
                "product_link_id": pid,
                "product_link": f"https://example.com/p/{pid}",
                "category": np.nan if pid % 17 == 0 else cat,
                "product_name": name,
                "brand": stored_brand,
                "price": float(rng.choice([8.99, 15.0, 24.0, 38.0, 52.0])),
                "description": desc,
                "pros": f"Blends well {phrase.split()[1]} long lasting",
                "best_uses": "Everyday" if i % 2 else "Special occasions",
                "average_rating": 0.0 if rcount == 0 else round(float(rng.uniform(3.2, 4.9)), 2),
                "rating_count": rcount,
                "review_count": rcount,
            })
            pid += 1
    df = pd.DataFrame(rows)
    # Duplikat ID dan baris tanpa deskripsi, seperti kasus nyata.
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    extra = df.iloc[[1]].copy()
    extra["product_link_id"] = 9999
    extra["description"] = np.nan
    return pd.concat([df, extra], ignore_index=True)
