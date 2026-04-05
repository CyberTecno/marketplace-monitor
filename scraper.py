"""
Marketplace Price & Stock Monitor
Hari 1: Generate dummy data produk (simulasi scraping)
"""

import csv
import os
import random
from datetime import datetime

# ============================================================
# KONFIGURASI
# ============================================================
KEYWORDS = ["vitamin c", "herbal supplement", "vegan protein"]
OUTPUT_FILE = "data/produk.csv"

# ============================================================
# DUMMY DATA
# ============================================================

DUMMY_PRODUK = {
    "vitamin c": [
        {"id": "vc001", "nama": "Blackmores Vitamin C 1000mg 60 Tablet", "harga": 85000, "harga_asli": 95000, "diskon": 10, "toko": "HealthyStore", "kota": "Jakarta", "rating": 4.8, "review": 1240},
        {"id": "vc002", "nama": "Now Foods Vitamin C 1000mg with Rose Hips", "harga": 120000, "harga_asli": 120000, "diskon": 0, "toko": "NutritionHub", "kota": "Surabaya", "rating": 4.7, "review": 890},
        {"id": "vc003", "nama": "Vitacimin Vitamin C 500mg Orange 10 Tablet", "harga": 12000, "harga_asli": 15000, "diskon": 20, "toko": "ApotekSehat", "kota": "Bandung", "rating": 4.9, "review": 5600},
        {"id": "vc004", "nama": "Nature's Plus Vitamin C 1000mg Sustained Release", "harga": 210000, "harga_asli": 250000, "diskon": 16, "toko": "NaturalLife", "kota": "Bali", "rating": 4.6, "review": 320},
        {"id": "vc005", "nama": "Enervon C Multivitamin Tablet 30s", "harga": 45000, "harga_asli": 45000, "diskon": 0, "toko": "MediStore", "kota": "Medan", "rating": 4.5, "review": 2100},
    ],
    "herbal supplement": [
        {"id": "hs001", "nama": "Nilaya Temulawak Herbal Extract 60 Kapsul", "harga": 75000, "harga_asli": 90000, "diskon": 17, "toko": "NilayaOfficial", "kota": "Bali", "rating": 4.9, "review": 430},
        {"id": "hs002", "nama": "Sido Muncul Kunyit Asam 12 Sachet", "harga": 18000, "harga_asli": 20000, "diskon": 10, "toko": "HerbalNusantara", "kota": "Semarang", "rating": 4.7, "review": 3200},
        {"id": "hs003", "nama": "Jahe Merah Kapsul Organik 500mg 60 Kapsul", "harga": 55000, "harga_asli": 55000, "diskon": 0, "toko": "OrganicLife", "kota": "Yogyakarta", "rating": 4.6, "review": 780},
        {"id": "hs004", "nama": "Spirulina Tablet 500mg Organic 100 Tablet", "harga": 130000, "harga_asli": 160000, "diskon": 19, "toko": "GreenHealth", "kota": "Bali", "rating": 4.8, "review": 560},
        {"id": "hs005", "nama": "Habbatussauda Black Seed Oil 100 Kapsul", "harga": 95000, "harga_asli": 95000, "diskon": 0, "toko": "HerbalMart", "kota": "Jakarta", "rating": 4.5, "review": 1890},
    ],
    "vegan protein": [
        {"id": "vp001", "nama": "Orgain Organic Protein Powder Vanilla 920g", "harga": 420000, "harga_asli": 480000, "diskon": 13, "toko": "VeganStore", "kota": "Jakarta", "rating": 4.7, "review": 670},
        {"id": "vp002", "nama": "Sunwarrior Classic Protein Chocolate 750g", "harga": 580000, "harga_asli": 580000, "diskon": 0, "toko": "NutritionHub", "kota": "Surabaya", "rating": 4.8, "review": 340},
        {"id": "vp003", "nama": "Nilaya Pea Protein Isolate Natural 500g", "harga": 185000, "harga_asli": 220000, "diskon": 16, "toko": "NilayaOfficial", "kota": "Bali", "rating": 4.9, "review": 210},
        {"id": "vp004", "nama": "Garden of Life Raw Organic Protein 560g", "harga": 650000, "harga_asli": 720000, "diskon": 10, "toko": "OrganicLife", "kota": "Jakarta", "rating": 4.6, "review": 480},
        {"id": "vp005", "nama": "MyProtein Soy Protein Isolate Unflavored 1kg", "harga": 310000, "harga_asli": 310000, "diskon": 0, "toko": "FitnessMart", "kota": "Bandung", "rating": 4.4, "review": 920},
    ],
}

STOK_STATUS = ["tersedia", "tersedia", "tersedia", "tersedia", "habis"]  # 80% tersedia


# ============================================================
# FUNGSI
# ============================================================

def generate_dummy(keyword: str) -> list[dict]:
    """Simulasi hasil scraping dengan data dummy."""
    hasil = []
    produk_list = DUMMY_PRODUK.get(keyword, [])

    for p in produk_list:
        stok = random.choice(STOK_STATUS)
        hasil.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "keyword": keyword,
            "id_produk": p["id"],
            "nama_produk": p["nama"],
            "harga": p["harga"],
            "harga_asli": p["harga_asli"],
            "diskon_persen": p["diskon"],
            "stok_status": stok,
            "rating": p["rating"],
            "jumlah_review": p["review"],
            "nama_toko": p["toko"],
            "kota_toko": p["kota"],
            "url_produk": f"https://tokopedia.com/product/{p['id']}",
        })

    return hasil


def simpan_ke_csv(data: list[dict], filepath: str):
    """Simpan list produk ke CSV. Append jika file sudah ada."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file_exists = os.path.isfile(filepath)

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(data)

    print(f"  [OK] {len(data)} produk disimpan ke '{filepath}'")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 55)
    print("  Marketplace Monitor — Hari 1: Generate Dummy Data")
    print("=" * 55)

    semua_produk = []

    for keyword in KEYWORDS:
        print(f"\n[INFO] Keyword: '{keyword}'")
        produk_list = generate_dummy(keyword)

        for p in produk_list:
            icon = "✓" if p["stok_status"] == "tersedia" else "✗"
            diskon_label = f" (-{p['diskon_persen']}%)" if p["diskon_persen"] > 0 else ""
            print(f"  {icon} {p['nama_produk'][:45]:<45} | Rp{p['harga']:>9,}{diskon_label}")

        semua_produk.extend(produk_list)

    print()
    simpan_ke_csv(semua_produk, OUTPUT_FILE)

    print(f"\n{'=' * 55}")
    print(f"  SELESAI — {len(semua_produk)} produk dari {len(KEYWORDS)} keyword")
    print(f"  File: {OUTPUT_FILE}")
    print(f"{'=' * 55}")


if __name__ == "__main__":
    main()