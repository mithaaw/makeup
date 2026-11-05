# Sistem Rekomendasi Produk Makeup — Aplikasi Web Streamlit

Aplikasi web interaktif untuk sistem rekomendasi produk makeup berbasis
**content-based filtering** (TF-IDF + cosine similarity), dikembangkan dari notebook
*Makeup Recommendation System*. Data: Kaggle `zarasarkar/makeup-insights-customer-reviews`
(file `cleaned_makeup_products.csv`).

## Mulai di sini

Jika baru membuka folder ini, baca **`notebook/Makeup_Recommendation_System_Revisi.ipynb`** lebih dulu.
Alurnya: Data Understanding → EDA → Preprocessing → Preparation → Model → Evaluasi,
dengan penjelasan di setiap langkah.

```
notebook revisi  ──►  data/products_clean.csv  ──►  streamlit run app.py
```

### Peta file: apa fungsi tiap file?

| File | Fungsi | Perlu diubah? |
|---|---|---|
| `notebook/Makeup_Recommendation_System_Revisi.ipynb` | Alur lengkap dengan penjelasan; menghasilkan `data/products_clean.csv` | Untuk belajar dan laporan |
| `recommender.py` | Logika yang sama dengan notebook revisi, dikemas sebagai fungsi untuk aplikasi | Hanya jika logika diubah |
| `app.py` | Tampilan aplikasi web Streamlit | Jika ingin mengubah tampilan |
| `prepare_data.py` | Alternatif notebook: membersihkan CSV lewat satu perintah terminal | Tidak |
| `evaluate.py` | Alternatif notebook: mencetak hasil evaluasi lewat terminal | Tidak |
| `requirements.txt` | Daftar library yang diinstal Streamlit Cloud | Tidak |
| `.streamlit/config.toml` | Warna tema dan pengaturan Streamlit | Opsional |
| `tests/` | Uji otomatis dengan data sintetis | Tidak |

Notebook revisi dan `recommender.py` dijamin memberi hasil yang sama: bagian 9 notebook
memeriksanya secara otomatis.

## Fitur aplikasi

- **Rekomendasi**: pilih produk (bisa dicari dengan mengetik), tampilkan top-*k* produk mirip
  beserta skor, kemiripan teks, harga, rating, dan tautan produk.
- **Pengaturan bobot**: kemiripan teks, kesamaan kategori, dan kesamaan merek.
- **Filter**: hanya merek lain (mencari alternatif), hanya kategori yang sama,
  harga maksimum, dan rating minimum.
- **Tab Data**: laporan pembersihan data, distribusi kategori dan merek.
- **Tab Evaluasi**: Precision@k terhadap baseline acak, lift, dan cakupan katalog.
- **Unggah CSV** dari sidebar bila file data belum disertakan.

## Struktur

```
makeup-recsys/
├── notebook/
│   └── Makeup_Recommendation_System_Revisi.ipynb   # MULAI DI SINI
├── app.py                 # Aplikasi Streamlit
├── recommender.py         # Pembersihan data, model, evaluasi
├── prepare_data.py        # CSV mentah Kaggle -> data/products_clean.csv
├── evaluate.py            # Evaluasi offline untuk laporan
├── requirements.txt
├── .streamlit/config.toml
├── data/                  # Tempat products_clean.csv
└── tests/                 # Uji otomatis (memakai data SINTETIS, bukan data asli)
```

## Menjalankan secara lokal

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 1. Unduh dataset dari halaman Kaggle (klik Download, lalu ekstrak zip-nya),
#    letakkan cleaned_makeup_products.csv di folder ini, lalu bersihkan dengan SALAH SATU cara:
#    a) jalankan notebook/Makeup_Recommendation_System_Revisi.ipynb (Colab/Jupyter), atau
#    b) satu perintah terminal:
python prepare_data.py --input cleaned_makeup_products.csv --output data/products_clean.csv

# 2. (Opsional) Evaluasi offline:
python evaluate.py --data data/products_clean.csv --k 5 10

# 3. Jalankan aplikasi:
streamlit run app.py
```

Uji otomatis: `pip install pytest` lalu `python -m pytest -q`.

## Deploy ke Streamlit Community Cloud

1. Buat repositori GitHub dan unggah seluruh isi folder ini, **termasuk**
   `data/products_clean.csv`, asalkan lisensi dataset di halaman Kaggle mengizinkan redistribusi.
2. Masuk ke Streamlit Community Cloud dengan akun GitHub, pilih *Create app*,
   pilih repositori dan branch, isi *Main file path* dengan `app.py`, lalu *Deploy*.
3. Setiap `git push` ke branch tersebut akan memperbarui aplikasi.

Jika data tidak boleh diunggah ke repositori publik, aplikasi tetap bisa dipakai:
pengguna mengunggah CSV melalui sidebar.

## Cara kerja singkat

1. **Preprocessing**: buang baris tanpa nama/deskripsi, duplikat ID, dan varian nama+merek yang sama; perbaiki merek yang berupa artefak scraping ("Find your shade", "Ask A Question") dari teks deskripsi; kategori kosong menjadi `Unknown`; kolom teks kosong diisi teks kosong.
2. **Fitur**: TF-IDF (unigram+bigram, stop words Inggris) atas nama produk, ringkasan deskripsi, best uses, dan pros.
3. **Skor**: rata-rata berbobot kemiripan teks (cosine similarity), kesamaan kategori, dan kesamaan merek; skor seri dipecah dengan rating.
4. **Evaluasi**: Precision@k dengan proxy relevansi kategori sama (tanpa kategori sebagai fitur), dibandingkan baseline acak, ditambah lift dan cakupan katalog.

## Catatan metodologis untuk laporan

- Precision@k berbasis kategori adalah **proxy** relevansi, bukan relevansi menurut pengguna.
  Karena itu evaluasi sengaja tidak memakai kategori sebagai fitur (kalau dipakai, nilainya
  trivial mendekati 1).
- Bandingkan Precision@k dengan baseline acak (nilai harapan jika rekomendasi diambil acak);
  lift > 1 menunjukkan model lebih baik dari acak.
- Validasi yang lebih kuat membutuhkan data interaksi per pengguna (file
  `cleaned_makeup_reviews.csv` bisa dijajaki untuk collaborative filtering/hybrid)
  atau uji pengguna.
- Angka hasil di `tests/` berasal dari data sintetis dan **tidak boleh** dilaporkan.
