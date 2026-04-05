"""
Marketplace Price & Stock Monitor
Hari 4: Scheduler Otomatis — jalankan monitor setiap X jam/menit
"""

import schedule
import time
import sqlite3
import copy
import random
from datetime import datetime

from scraper import generate_dummy, KEYWORDS
from database import init_db, proses_produk, DB_FILE
from notifier import kirim_notifikasi, simulasi_perubahan

# ============================================================
# KONFIGURASI SCHEDULER
# ============================================================
INTERVAL_JAM    = 6      # jalankan setiap 6 jam (production)
INTERVAL_MENIT  = 1      # jalankan setiap 1 menit (demo/testing)
MODE            = "demo" # "demo" = tiap menit | "production" = tiap 6 jam

# ============================================================
# STATE — simpan data terakhir di memory
# ============================================================
_state = {
    "produk_terakhir": [],
    "run_count": 0,
    "last_run": None,
}


# ============================================================
# FUNGSI MONITOR UTAMA
# ============================================================

def jalankan_monitor():
    """
    Satu siklus penuh: ambil data → deteksi perubahan → kirim notif.
    Di production: ganti simulasi_perubahan() dengan fetch API asli.
    """
    _state["run_count"] += 1
    run_ke = _state["run_count"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _state["last_run"] = now

    print(f"\n{'═' * 55}")
    print(f"  🔄 Run #{run_ke} — {now}")
    print(f"{'═' * 55}")

    # ── Ambil data produk ────────────────────────────────
    if _state["produk_terakhir"]:
        # Sudah ada data sebelumnya → simulasi perubahan
        print("[INFO] Mengambil data terbaru dari marketplace...")
        produk_baru = simulasi_perubahan(_state["produk_terakhir"])
    else:
        # Pertama kali → pakai dummy data fresh
        print("[INFO] Inisialisasi data pertama kali...")
        produk_baru = []
        for kw in KEYWORDS:
            produk_baru.extend(generate_dummy(kw))

    _state["produk_terakhir"] = produk_baru
    print(f"[INFO] {len(produk_baru)} produk berhasil diambil")

    # ── Deteksi perubahan ────────────────────────────────
    alerts = proses_produk(produk_baru)
    produk_map = {p["id_produk"]: p["url_produk"] for p in produk_baru}
    print(f"[INFO] {len(alerts)} perubahan terdeteksi")

    # ── Kirim notifikasi ─────────────────────────────────
    if alerts:
        kirim_notifikasi(alerts, produk_map, len(produk_baru))
    else:
        print("[INFO] Tidak ada perubahan — notifikasi tidak dikirim")

    # ── Status ringkas ───────────────────────────────────
    print(f"\n  ✅ Run #{run_ke} selesai | Next run: ", end="")
    if MODE == "demo":
        print(f"~{INTERVAL_MENIT} menit lagi")
    else:
        print(f"~{INTERVAL_JAM} jam lagi")


# ============================================================
# UTILITAS
# ============================================================

def tampilkan_status():
    """Cetak status scheduler dan ringkasan DB."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM produk")
    total_produk = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM riwayat_perubahan")
    total_perubahan = cur.fetchone()[0]

    cur.execute("""
        SELECT tipe_perubahan, COUNT(*)
        FROM riwayat_perubahan
        GROUP BY tipe_perubahan
    """)
    breakdown = cur.fetchall()
    conn.close()

    print(f"\n{'─' * 40}")
    print(f"  📊 STATUS MONITOR")
    print(f"{'─' * 40}")
    print(f"  Total produk dipantau : {total_produk}")
    print(f"  Total perubahan catat : {total_perubahan}")
    for tipe, count in breakdown:
        print(f"    └ {tipe:<10} : {count}x")
    print(f"  Run terakhir          : {_state['last_run'] or '-'}")
    print(f"  Total siklus          : {_state['run_count']}")
    print(f"{'─' * 40}\n")


# ============================================================
# MAIN — Setup & Start Scheduler
# ============================================================

def main():
    print("=" * 55)
    print("  Marketplace Monitor — Hari 4: Scheduler Otomatis")
    print("=" * 55)

    # Inisialisasi DB
    init_db()

    if MODE == "demo":
        print(f"\n[MODE] DEMO — scheduler berjalan setiap {INTERVAL_MENIT} menit")
        print("[INFO] Tekan Ctrl+C untuk berhenti\n")

        # Jalankan langsung sekali di awal
        jalankan_monitor()
        tampilkan_status()

        # Lalu jadwalkan setiap INTERVAL_MENIT menit
        schedule.every(INTERVAL_MENIT).minutes.do(jalankan_monitor)
        schedule.every(INTERVAL_MENIT).minutes.do(tampilkan_status)

    else:
        print(f"\n[MODE] PRODUCTION — scheduler berjalan setiap {INTERVAL_JAM} jam")
        print("[INFO] Jadwal: 08:00, 14:00, 20:00")
        print("[INFO] Tekan Ctrl+C untuk berhenti\n")

        # Jalankan langsung sekali saat start
        jalankan_monitor()
        tampilkan_status()

        # Jadwalkan jam-jam spesifik
        schedule.every().day.at("08:00").do(jalankan_monitor)
        schedule.every().day.at("14:00").do(jalankan_monitor)
        schedule.every().day.at("20:00").do(jalankan_monitor)

    # ── Loop utama ───────────────────────────────────────
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # cek setiap 30 detik
    except KeyboardInterrupt:
        print("\n\n[STOP] Scheduler dihentikan.")
        tampilkan_status()
        print("  Sampai jumpa! 👋")


if __name__ == "__main__":
    main()