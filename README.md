# 🛒 Marketplace Price & Stock Monitor

> An automated system to track **price changes**, **stock availability**, and **discount updates** across Tokopedia — with real-time alerts via **Telegram Bot**.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat-square&logo=telegram&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📌 Background

E-commerce businesses need real-time visibility into competitor pricing and stock levels. Manually checking products across marketplaces is time-consuming and error-prone.

This project builds a fully automated monitoring infrastructure that:
- ✅ Periodically fetches product data from Tokopedia
- ✅ Detects every price, stock, and discount change
- ✅ Sends instant alerts directly to Telegram
- ✅ Stores the complete change history in a local database

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   scheduler.py                       │
│           (Runs automatically every 6h)             │
└──────────────────────┬──────────────────────────────┘
                       │
          ┌────────────▼────────────┐
          │       scraper.py        │
          │  Fetch product data     │
          │  from Tokopedia API     │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │      database.py        │
          │  SQLite — persist data  │
          │  & detect changes       │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │      notifier.py        │
          │  Push alerts to         │
          │  Telegram Bot           │
          └─────────────────────────┘
```

---

## 📁 Project Structure

```
marketplace_monitor/
├── scraper.py        # Product data fetching
├── database.py       # SQLite storage + change detection
├── notifier.py       # Telegram Bot alerts
├── scheduler.py      # Automated scheduling
├── requirements.txt  # Dependencies
├── .env.example      # Environment variable template
├── data/
│   ├── products.csv  # Scraped data (CSV)
│   └── monitor.db    # SQLite database
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/username/marketplace-monitor.git
cd marketplace-monitor
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:
```env
TELEGRAM_BOT_TOKEN=123456789:ABC-your-token-here
TELEGRAM_CHAT_ID=987654321
```

> 💡 **Get your token:** Open [@BotFather](https://t.me/BotFather) on Telegram → `/newbot`
>
> 💡 **Get your Chat ID:** Open `https://api.telegram.org/bot<TOKEN>/getUpdates` after starting your bot

### 3. Run

```bash
# Demo mode — runs every 1 minute (for testing)
python scheduler.py

# Production mode — runs every 6 hours (08:00, 14:00, 20:00)
# Set MODE = "production" in scheduler.py first
python scheduler.py
```

---

## 📲 Sample Telegram Notification

```
📊 Monitor Report — 05 Apr 2026 08:00
🔍 Total products tracked: 15
🔔 Changes detected: 4

💰 Price changes  : 2 products
📦 Stock changes  : 1 product
🏷️  Discount changes: 1 product
─────────────────────────────────────
🔴 OUT OF STOCK
📦 Nilaya Temulawak Herbal Extract 60 Capsules
🔗 View Product
─────────────────────────────────────
📉 PRICE CHANGE
📦 Nilaya Pea Protein Isolate Natural 500g
💰 Rp185,000 → Rp172,123
📊 Down 7.0%
🔗 View Product
```

---

## 🗄️ Database Schema

### `products` table — latest snapshot per product
| Column | Type | Description |
|---|---|---|
| `id_product` | TEXT PK | Unique product ID |
| `name` | TEXT | Product name |
| `price` | INTEGER | Current price (Rp) |
| `original_price` | INTEGER | Price before discount |
| `discount_pct` | INTEGER | Discount percentage |
| `stock_status` | TEXT | `available` / `out_of_stock` |
| `last_updated` | TEXT | Timestamp of last update |

### `change_history` table — full historical log
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto increment |
| `timestamp` | TEXT | Time of change |
| `id_product` | TEXT | Product reference |
| `change_type` | TEXT | `PRICE` / `STOCK` / `DISCOUNT` |
| `old_value` | TEXT | Previous value |
| `new_value` | TEXT | Updated value |

---

## 🔧 Configuration

Tweak the `CONFIG` section in each file:

**`scraper.py`** — Products to monitor:
```python
KEYWORDS   = ["vitamin c", "herbal supplement", "vegan protein"]
MAX_ITEMS  = 10   # products per keyword
```

**`scheduler.py`** — Monitoring frequency:
```python
MODE             = "production"  # "demo" or "production"
INTERVAL_HOURS   = 6             # production interval (hours)
INTERVAL_MINUTES = 1             # demo interval (minutes)
```

---

## 🛠️ Tech Stack

| Component | Library |
|---|---|
| HTTP Requests | `requests` |
| Database | `sqlite3` (built-in) |
| Telegram Bot | `python-telegram-bot` |
| Scheduler | `schedule` |
| Environment | `python-dotenv` |

---

## 🚀 Roadmap

- [x] Product data scraping
- [x] SQLite database + change detection
- [x] Telegram bot notifications
- [x] Automated scheduler
- [ ] Web dashboard (Streamlit)
- [ ] Shopee API support
- [ ] AI-based price trend prediction
- [ ] Multi-user support
- [ ] Cloud deployment (Railway / VPS)

---

## 👤 Author

**[Your Name]** — AI & Robotics Student
📧 email@example.com
🔗 [LinkedIn](https://linkedin.com/in/username) · [GitHub](https://github.com/username)

---

## 📄 License

MIT License — free to use and modify.
