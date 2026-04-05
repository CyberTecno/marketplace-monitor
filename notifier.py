import os
import requests
from datetime import datetime
from database import init_db, proses_produk, DB_FILE
from scraper import generate_dummy, KEYWORDS, DUMMY_PRODUK
import sqlite3
import copy
import random

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_TOKEN_BELUM_DIISI")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID",   "TELEGRAM_CHAT_ID_BELUM_DIISI")

DEMO_MODE = (
    TELEGRAM_BOT_TOKEN == "TELEGRAM_BOT_TOKEN_BELUM_DIISI"
    or TELEGRAM_CHAT_ID == "TELEGRAM_CHAT_ID_BELUM_DIISI"
)


def kirim_pesan(text: str) -> bool:
    """Kirim pesan ke Telegram. Return True kalau berhasil."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"  [ERROR] Gagal kirim Telegram: {e}")
        return False


def format_alert_harga(nama: str, lama: str, baru: str, info: str, url: str = "") -> str:
    arah = "naik" if "naik" in info else "turun"
    icon = "📈" if arah == "naik" else "📉"
    persen = info.replace("naik 📈", "").replace("turun 📉", "")
    link = f'\n🔗 <a href="{url}">Lihat Produk</a>' if url else ""
    return (
        f"{icon} <b>PERUBAHAN HARGA</b>\n"
        f"📦 {nama}\n"
        f"💰 {lama} → <b>{baru}</b>\n"
        f"📊 {arah.capitalize()} {persen}{link}"
    )


def format_alert_stok(nama: str, baru: str, url: str = "") -> str:
    if baru == "habis":
        icon, label = "🔴", "STOK HABIS"
    else:
        icon, label = "🟢", "STOK TERSEDIA"
    link = f'\n🔗 <a href="{url}">Lihat Produk</a>' if url else ""
    return (
        f"{icon} <b>{label}</b>\n"
        f"📦 {nama}{link}"
    )


def format_alert_diskon(nama: str, lama: str, baru: str, url: str = "") -> str:
    link = f'\n🔗 <a href="{url}">Lihat Produk</a>' if url else ""
    return (
        f"🏷️ <b>PERUBAHAN DISKON</b>\n"
        f"📦 {nama}\n"
        f"🎯 {lama} → <b>{baru}</b>{link}"
    )


def format_summary(alerts: list[dict], total_produk: int) -> str:
    """Ringkasan semua perubahan dalam satu pesan."""
    ts = datetime.now().strftime("%d %b %Y %H:%M")
    n_harga = sum(1 for a in alerts if a["tipe"] == "HARGA")
    n_stok  = sum(1 for a in alerts if a["tipe"] == "STOK")
    n_diskon = sum(1 for a in alerts if a["tipe"] == "DISKON")

    baris = [
        f"📊 <b>Laporan Monitor — {ts}</b>",
        f"🔍 Total produk dipantau: {total_produk}",
        f"🔔 Perubahan terdeteksi: {len(alerts)}",
        "",
    ]
    if n_harga:
        baris.append(f"💰 Harga berubah  : {n_harga} produk")
    if n_stok:
        baris.append(f"📦 Stok berubah   : {n_stok} produk")
    if n_diskon:
        baris.append(f"🏷️  Diskon berubah : {n_diskon} produk")

    if not alerts:
        baris.append("✅ Tidak ada perubahan")

    return "\n".join(baris)


# ============================================================
# KIRIM NOTIFIKASI
# ============================================================

def kirim_notifikasi(alerts: list[dict], produk_map: dict, total_produk: int):
    """
    Kirim semua alert ke Telegram.
    produk_map = {id_produk: url_produk}
    """
    if DEMO_MODE:
        print("\n  [DEMO MODE] Token belum diisi — pesan ditampilkan di terminal:\n")
        _print_demo(alerts, total_produk)
        return

    # 1. Kirim summary dulu
    summary = format_summary(alerts, total_produk)
    ok = kirim_pesan(summary)
    print(f"  {'✓' if ok else '✗'} Summary terkirim")

    # 2. Kirim tiap alert satu per satu
    for a in alerts:
        url = produk_map.get(a.get("id_produk", ""), "")
        if a["tipe"] == "HARGA":
            msg = format_alert_harga(a["nama_produk"], a["lama"], a["baru"], a["info"], url)
        elif a["tipe"] == "STOK":
            msg = format_alert_stok(a["nama_produk"], a["baru"], url)
        elif a["tipe"] == "DISKON":
            msg = format_alert_diskon(a["nama_produk"], a["lama"], a["baru"], url)
        else:
            continue

        ok = kirim_pesan(msg)
        nama_short = a["nama_produk"][:40]
        print(f"  {'✓' if ok else '✗'} [{a['tipe']}] {nama_short}...")


def _print_demo(alerts: list[dict], total_produk: int):
    """Cetak preview pesan Telegram ke terminal."""
    print("  ─" * 28)
    print(format_summary(alerts, total_produk))
    print()
    for a in alerts:
        if a["tipe"] == "HARGA":
            msg = format_alert_harga(a["nama_produk"], a["lama"], a["baru"], a["info"])
        elif a["tipe"] == "STOK":
            msg = format_alert_stok(a["nama_produk"], a["baru"])
        elif a["tipe"] == "DISKON":
            msg = format_alert_diskon(a["nama_produk"], a["lama"], a["baru"])
        else:
            continue
        # Strip HTML tags buat terminal
        import re
        msg_clean = re.sub(r"<[^>]+>", "", msg)
        print(msg_clean)
        print("  ─" * 28)


# ============================================================
# SIMULASI PERUBAHAN (sama seperti hari 2)
# ============================================================

def simulasi_perubahan(produk_list: list[dict]) -> list[dict]:
    modif = copy.deepcopy(produk_list)
    random.seed(42)  # seed biar hasilnya konsisten tiap run
    for p in modif:
        roll = random.random()
        if roll < 0.25:
            p["harga"] = int(p["harga"] * random.uniform(1.05, 1.20))
        elif roll < 0.45:
            p["harga"] = int(p["harga"] * random.uniform(0.80, 0.95))
        elif roll < 0.60:
            p["stok_status"] = "habis" if p["stok_status"] == "tersedia" else "tersedia"
        elif roll < 0.70:
            p["diskon_persen"] = random.choice([0, 5, 10, 15, 20, 25])
    return modif


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 55)
    print("  Marketplace Monitor — Hari 3: Telegram Notifikasi")
    print("=" * 55)

    # Setup DB & sesi 1 (data awal)
    init_db()
    produk_sesi1 = []
    for kw in KEYWORDS:
        produk_sesi1.extend(generate_dummy(kw))
    proses_produk(produk_sesi1)  # insert awal, belum ada perubahan
    print(f"[INFO] {len(produk_sesi1)} produk awal dimuat ke database")

    # Sesi 2: simulasi update dengan perubahan
    print("[INFO] Simulasi update data...")
    produk_sesi2 = simulasi_perubahan(produk_sesi1)
    alerts = proses_produk(produk_sesi2)

    # Buat map id → url untuk link di Telegram
    produk_map = {p["id_produk"]: p["url_produk"] for p in produk_sesi2}

    # Kirim notifikasi
    print(f"\n[INFO] {len(alerts)} perubahan terdeteksi — mengirim notifikasi...\n")
    kirim_notifikasi(alerts, produk_map, len(produk_sesi2))

    mode = "DEMO (terminal)" if DEMO_MODE else "TELEGRAM"
    print(f"\n[SELESAI] Notifikasi dikirim via {mode}")

    if DEMO_MODE:
        print("\n💡 Untuk kirim ke Telegram sungguhan:")
        print("   1. Buat bot via @BotFather di Telegram")
        print("   2. Isi TELEGRAM_BOT_TOKEN dan TELEGRAM_CHAT_ID di notifier.py")
        print("   3. Jalankan ulang script ini")


if __name__ == "__main__":
    main()