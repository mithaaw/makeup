"""
Uji otomatis dengan data SINTETIS (lihat synthetic_data.py).

Jalankan:  python -m pytest -q
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from recommender import Recommender, clean_products, evaluate
from synthetic_data import make_raw_products

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def cleaned():
    df, report = clean_products(make_raw_products())
    return df, report


def test_cleaning_keeps_products(cleaned):
    df, report = cleaned
    raw = make_raw_products()
    # Hanya duplikat ID dan baris tanpa deskripsi yang dibuang.
    assert report["baris_akhir"] == raw["product_link_id"].nunique() - 1
    assert report["merek_diperbaiki_dari_deskripsi"] > 0
    assert not df["brand"].str.lower().isin(["find your shade", "ask a question"]).any()
    assert df["product_link_id"].is_unique


def test_scores_are_not_all_ties(cleaned):
    df, _ = cleaned
    model = Recommender.fit(df)
    rec = model.recommend(df["product_link_id"].iloc[0], k=10)
    # Skor harus bervariasi, tidak seri 1,0 untuk semua produk sekategori.
    assert rec["score"].nunique() > 1
    assert (np.diff(rec["score"].to_numpy()) <= 1e-12).all()  # terurut menurun


def test_filters(cleaned):
    df, _ = cleaned
    model = Recommender.fit(df)
    pid = df["product_link_id"].iloc[0]
    brand = df["brand"].iloc[0]
    rec = model.recommend(pid, k=10, exclude_same_brand=True, max_price=20, min_rating=4.0)
    assert pid not in rec["product_link_id"].tolist()
    assert (rec["brand"] != brand).all()
    assert (rec["price"] <= 20).all()
    assert (rec["average_rating"] >= 4.0).all()


def test_evaluation_beats_random(cleaned):
    df, _ = cleaned
    r = evaluate(Recommender.fit(df), k=5)
    assert r["n_queries_evaluated"] > 0
    assert r["precision_at_k"] > r["baseline_random"]
    assert 0 < r["catalog_coverage"] <= 1


def test_streamlit_app_runs_with_data(tmp_path, monkeypatch):
    # Simpan data sintetis sebagai data/products_clean.csv sementara.
    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    target = data_dir / "products_clean.csv"
    existed = target.exists()
    if not existed:
        df, _ = clean_products(make_raw_products())
        df.to_csv(target, index=False)
    try:
        at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
        at.run()
        assert not at.exception, at.exception
        assert at.title[0].value == "Sistem Rekomendasi Produk Makeup"
        assert len(at.dataframe) >= 1  # tabel rekomendasi tampil

        # Ubah pilihan produk dan filter -> aplikasi tetap jalan.
        other_id = int(pd.read_csv(target)["product_link_id"].iloc[3])
        at.selectbox[1].set_value(other_id).run()
        assert not at.exception, at.exception
        assert at.metric[0].value  # kartu produk terpilih tampil
        at.toggle[0].set_value(True).run()
        assert not at.exception, at.exception

        # Tab evaluasi.
        at.button[0].click().run()
        assert not at.exception, at.exception
        assert any("Precision" in m.label for m in at.metric)
    finally:
        if not existed:
            target.unlink()


def test_streamlit_app_without_data_shows_warning():
    target = ROOT / "data" / "products_clean.csv"
    if target.exists():
        pytest.skip("data/products_clean.csv ada; skenario tanpa data dilewati")
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    at.run()
    assert not at.exception
    assert len(at.warning) == 1
