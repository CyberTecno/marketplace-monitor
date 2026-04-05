import sqlite3
import os
from datetime import datetime
from scraper import generate_dummy, KEYWORDS

# ============================================================
# KONFIGURASI
# ============================================================
DB_FILE = "data/monitor.db"


# ============================================================
# SETUP DATABASE
# ============================================================

def init_db(db_path: str = DB_FILE):
    """Buat tabel jika belum ada."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Tabel produk — snapshot terbaru tiap produk
    cur.execute("""
        CREATE TABLE IF NOT EXISTS produk (
            id_produk     TEXT PRIMARY KEY,
            keyword       TEXT,
            nama_produk   TEXT,
            harga         INTEGER,
            harga_asli    INTEGER,
            diskon_persen INTEGER,
            stok_status   TEXT,
            rating        REAL,
            jumlah_review INTEGER,
            nama_toko     TEXT,
            kota_toko     TEXT,
            url_produk    TEXT,
            last_updated  TEXT
        )
    """)

    # Tabel riwayat — semua perubahan tercatat di sini
    cur.execute("""
        CREATE TABLE IF NOT EXISTS riwayat_perubahan (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp     TEXT,
            id_produk     TEXT,
            nama_produk   TEXT,
            tipe_perubahan TEXT,
            nilai_lama    TEXT,
            nilai_baru    TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Database siap.")


# ============================================================
# FUNGSI DATABASE
# ============================================================

def get_produk_lama(cur, id_produk: str) -> dict | None:
    """Ambil data produk terakhir dari DB."""
    cur.execute("SELECT * FROM produk WHERE id_produk = ?", (id_produk,))
    row = cur.fetchone()
    if not row:
        return None
    cols = ["id_produk", "keyword", "nama_produk", "harga", "harga_asli",
            "diskon_persen", "stok_status", "rating", "jumlah_review",
            "nama_toko", "kota_toko", "url_produk", "last_updated"]
    return dict(zip(cols, row))


def upsert_produk(cur, p: dict):
    """Insert produk baru atau update kalau sudah ada."""
    cur.execute("""
        INSERT INTO produk VALUES (
            :id_produk, :keyword, :nama_produk, :harga, :harga_asli,
            :diskon_persen, :stok_status, :rating, :jumlah_review,
            :nama_toko, :kota_toko, :url_produk, :last_updated
        )
        ON CONFLICT(id_produk) DO UPDATE SET
            harga         = excluded.harga,
            harga_asli    = excluded.harga_asli,
            diskon_persen = excluded.diskon_persen,
            stok_status   = excluded.stok_status,
            rating        = excluded.rating,
            jumlah_review = excluded.jumlah_review,
            last_updated  = excluded.last_updated
    """, {**p, "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})


def catat_perubahan(cur, id_produk: str, nama: str, tipe: str, lama: str, baru: str):
    """Simpan record perubahan ke tabel riwayat."""
    cur.execute("""
        INSERT INTO riwayat_perubahan (timestamp, id_produk, nama_produk, tipe_perubahan, nilai_lama, nilai_baru)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id_produk, nama, tipe, lama, baru))


# ============================================================
# DETEKSI PERUBAHAN
# ============================================================

def deteksi_perubahan(lama: dict, baru: dict) -> list[dict]:
    """
    Bandingkan data lama vs baru.
    Return list perubahan yang terdeteksi.
    """
    perubahan = []

    # Cek perubahan harga
    if lama["harga"] != baru["harga"]:
        selisih = baru["harga"] - lama["harga"]
        persen = (selisih / lama["harga"]) * 100
        arah = "naik" if selisih > 0 else "turun"
        perubahan.append({
            "tipe": "HARGA",
            "lama": f"Rp{lama['harga']:,}",
            "baru": f"Rp{baru['harga']:,}",
            "info": f"{arah} {abs(persen):.1f}%"
        })

    # Cek perubahan stok
    if lama["stok_status"] != baru["stok_status"]:
        if baru["stok_status"] == "habis":
            icon = "HABIS"
        else:
            icon = "TERSEDIA"
        perubahan.append({
            "tipe": "STOK",
            "lama": lama["stok_status"],
            "baru": baru["stok_status"],
            "info": icon
        })

    # Cek perubahan diskon
    if lama["diskon_persen"] != baru["diskon_persen"]:
        perubahan.append({
            "tipe": "DISKON",
            "lama": f"{lama['diskon_persen']}%",
            "baru": f"{baru['diskon_persen']}%",
            "info": "diskon berubah"
        })

    return perubahan


# ============================================================
# PROSES UTAMA
# ============================================================

def proses_produk(produk_baru: list[dict]) -> list[dict]:
    """
    Masukkan semua produk ke DB.
    Deteksi & catat perubahan kalau produk sudah ada sebelumnya.
    Return list alert perubahan.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    alerts = []

    for p in produk_baru:
        lama = get_produk_lama(cur, p["id_produk"])

        if lama:
            # Produk sudah ada — cek perubahan
            perubahan = deteksi_perubahan(lama, p)
            for c in perubahan:
                catat_perubahan(cur, p["id_produk"], p["nama_produk"],
                                c["tipe"], c["lama"], c["baru"])
                alerts.append({
                    "nama_produk": p["nama_produk"],
                    **c
                })
        else:
            # Produk baru — langsung insert
            pass

        upsert_produk(cur, p)

    conn.commit()
    conn.close()
    return alerts


def tampilkan_riwayat():
    """Print semua riwayat perubahan dari DB."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT timestamp, nama_produk, tipe_perubahan, nilai_lama, nilai_baru
        FROM riwayat_perubahan
        ORDER BY timestamp DESC
        LIMIT 20
    """)
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("  (belum ada riwayat perubahan)")
        return

    print(f"\n  {'WAKTU':<20} {'PRODUK':<40} {'TIPE':<8} {'LAMA':<15} {'BARU'}")
    print("  " + "-" * 100)
    for r in rows:
        ts, nama, tipe, lama, baru = r
        print(f"  {ts:<20} {nama[:38]:<40} {tipe:<8} {lama:<15} {baru}")


# ============================================================
# SIMULASI 2 SESI (supaya ada perubahan yang terdeteksi)
# ============================================================

def simulasi_perubahan(produk_list: list[dict]) -> list[dict]:
    """
    Buat versi modifikasi dari produk_list
    untuk simulasi perubahan harga & stok.
    """
    import copy, random
    modif = copy.deepcopy(produk_list)

    for p in modif:
        roll = random.random()
        if roll < 0.3:
            # Simulasi harga naik 5-15%
            p["harga"] = int(p["harga"] * random.uniform(1.05, 1.15))
        elif roll < 0.5:
            # Simulasi harga turun 5-20%
            p["harga"] = int(p["harga"] * random.uniform(0.80, 0.95))
        elif roll < 0.65:
            # Simulasi stok berubah
            p["stok_status"] = "habis" if p["stok_status"] == "tersedia" else "tersedia"

    return modif


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 55)
    print("  Marketplace Monitor — Hari 2: Database & Deteksi")
    print("=" * 55)

    # Setup DB
    init_db()

    # ── SESI 1: Insert data awal ──────────────────────────
    print("\n[SESI 1] Memasukkan data awal ke database...")
    produk_sesi1 = []
    for kw in KEYWORDS:
        produk_sesi1.extend(generate_dummy(kw))

    alerts1 = proses_produk(produk_sesi1)
    print(f"  {len(produk_sesi1)} produk berhasil disimpan (data awal, belum ada perubahan)")

    # ── SESI 2: Simulasi update dengan perubahan ──────────
    print("\n[SESI 2] Simulasi update data (harga & stok berubah)...")
    produk_sesi2 = simulasi_perubahan(produk_sesi1)
    alerts2 = proses_produk(produk_sesi2)

    # ── Tampilkan Alerts ──────────────────────────────────
    print(f"\n{'=' * 55}")
    print(f"  PERUBAHAN TERDETEKSI: {len(alerts2)} alert")
    print(f"{'=' * 55}")

    if alerts2:
        for a in alerts2:
            print(f"\n  {a['nama_produk'][:50]}")
            print(f"     [{a['tipe']}] {a['lama']} → {a['baru']}  {a['info']}")
    else:
        print("  Tidak ada perubahan terdeteksi.")

    # ── Tampilkan Riwayat DB ──────────────────────────────
    print(f"\n{'=' * 55}")
    print("  RIWAYAT PERUBAHAN (dari database)")
    print(f"{'=' * 55}")
    tampilkan_riwayat()

    print(f"\n[SELESAI] Database tersimpan di: {DB_FILE}")


if __name__ == "__main__":
    main()