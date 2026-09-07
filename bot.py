#!/usr/bin/env python3
"""
Immaculate SEO Bot - Ultra Premium Edition
GitHub Actions + GitHub Pages uyumlu, sıfır hata odaklı
"""

import os
import sys
import time
import random
import logging
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict

import requests
import feedparser
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ====================== CONFIG ======================
SITE_BASE = "https://immaculate.tr"
SITEMAP_URL = f"{SITE_BASE}/sitemap.xml"
FEED_URL = f"{SITE_BASE}/feed"
DOCS_DIR = Path("docs")
REPORT_FILE = DOCS_DIR / "latest-suggestion.md"
INDEX_FILE = DOCS_DIR / "index.md"

USER_AGENT = "ImmaculateSEOBot/3.0 (+https://github.com/yourusername/immaculate-seo-bot)"
TIMEOUT = 20
MAX_RETRIES = 4

# IndexNow (Bing + Yandex + diğerleri)
INDEXNOW_KEY = os.getenv("INDEXNOW_KEY", "")  # GitHub Secrets'a ekleyebilirsin
INDEXNOW_KEY_LOCATION = f"{SITE_BASE}/{INDEXNOW_KEY}.txt" if INDEXNOW_KEY else ""

# ====================== LOGGING ======================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ImmaculateBot")

# ====================== SESSION ======================
def create_session() -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST", "HEAD"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "application/rss+xml, application/xml, text/xml, */*"
    })
    return session

# ====================== SITEMAP & INDEXNOW ======================
def ping_search_engines(session: requests.Session) -> Dict[str, str]:
    results = {}

    # Klasik pingler (hala bazı motorlar dinliyor)
    pings = {
        "Google": f"https://www.google.com/ping?sitemap={SITEMAP_URL}",
        "Bing": f"https://www.bing.com/ping?sitemap={SITEMAP_URL}",
        "Yandex": f"https://webmaster.yandex.com/ping?sitemap={SITEMAP_URL}",
    }

    for name, url in pings.items():
        try:
            r = session.get(url, timeout=TIMEOUT)
            results[name] = f"{r.status_code}"
            logger.info(f"{name} ping → {r.status_code}")
        except Exception as e:
            results[name] = f"Error: {str(e)[:80]}"
            logger.warning(f"{name} ping failed: {e}")

    # IndexNow (modern ve önerilen yöntem)
    if INDEXNOW_KEY:
        try:
            payload = {
                "host": "immaculate.tr",
                "key": INDEXNOW_KEY,
                "keyLocation": INDEXNOW_KEY_LOCATION,
                "urlList": [SITEMAP_URL, f"{SITE_BASE}/"]
            }
            r = session.post("https://api.indexnow.org/indexnow", json=payload, timeout=TIMEOUT)
            results["IndexNow"] = f"{r.status_code}"
            logger.info(f"IndexNow → {r.status_code}")
        except Exception as e:
            results["IndexNow"] = f"Error: {e}"
            logger.warning(f"IndexNow failed: {e}")
    else:
        results["IndexNow"] = "Skipped (no key)"

    return results

# ====================== FEED & TOPIC ======================
def get_feed_titles(session: requests.Session) -> List[str]:
    try:
        logger.info(f"Feed okunuyor: {FEED_URL}")
        resp = session.get(FEED_URL, timeout=TIMEOUT)
        resp.raise_for_status()

        feed = feedparser.parse(resp.content)
        titles = []

        for entry in feed.entries[:25]:
            title = entry.get("title", "").strip()
            if title and len(title) > 12:
                titles.append(title)

        if not titles:
            # Fallback regex
            import re
            found = re.findall(r"<title[^>]*>([^<]+)</title>", resp.text, re.I)
            titles = [t.strip() for t in found if len(t.strip()) > 15][:20]

        logger.info(f"{len(titles)} başlık alındı")
        return titles

    except Exception as e:
        logger.error(f"Feed hatası: {e}")
        return []

def generate_premium_suggestion(titles: List[str]) -> Dict[str, str]:
    if not titles:
        titles = [
            "Samsung Galaxy S26 FE detaylı inceleme",
            "Poco F9 Pro vs Ultra karşılaştırması",
            "Xiaomi 18 Fold teknik analiz",
            "iPhone 18 Pro Max renk ve kamera sızıntıları"
        ]

    selected = random.choice(titles)

    templates = [
        f"{selected} – 2026 Detaylı İnceleme ve Gerçek Kullanıcı Deneyimi",
        f"{selected} Alınır mı? Tüm Artıları, Eksileri ve Alternatifler",
        f"2026 Rehberi: {selected} Firmware, ROM ve Unlock İşlemleri",
        f"{selected} Teknik Servis Notları ve Sık Karşılaşılan Sorunlar",
        f"Yeni Nesil {selected} – Performans, Batarya ve Kamera Analizi",
        f"{selected} için En İyi Aksesuar ve Optimizasyon Önerileri"
    ]

    return {
        "selected_from_feed": selected,
        "suggested_title": random.choice(templates),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }

# ====================== REPORT ======================
def write_report(ping_results: Dict[str, str], suggestion: Dict[str, str]) -> None:
    DOCS_DIR.mkdir(exist_ok=True)

    content = f"""# Immaculate SEO Bot – Günlük Rapor

**Çalışma Zamanı:** {suggestion['generated_at']}

---

## Sitemap Bildirim Sonuçları

| Motor       | Sonuç          |
|-------------|----------------|
"""
    for motor, result in ping_results.items():
        content += f"| {motor:<11} | {result} |\n"

    content += f"""
---

## Bugünkü Konu Önerisi

**Feed’den seçilen mevcut konu:**  
`{suggestion['selected_from_feed']}`

**Önerilen yeni blog başlığı:**  
### {suggestion['suggested_title']}

---

*Bu rapor GitHub Actions tarafından otomatik üretilmiştir.*  
*Bot Version: Ultra Premium 3.0*
"""

    REPORT_FILE.write_text(content, encoding="utf-8")
    logger.info(f"Rapor yazıldı → {REPORT_FILE}")

    # Ana sayfa da güncelle
    index_content = f"""# Immaculate SEO Bot

Günlük otomatik SEO & içerik öneri sistemi.

**Son çalışma:** {suggestion['generated_at']}

[Güncel Öneri Raporunu Görüntüle](latest-suggestion.md)
"""
    INDEX_FILE.write_text(index_content, encoding="utf-8")

# ====================== MAIN ======================
def main() -> int:
    logger.info("=" * 60)
    logger.info("Immaculate SEO Bot – Ultra Premium başlatıldı")
    logger.info("=" * 60)

    session = create_session()

    # 1. Sitemap bildir
    ping_results = ping_search_engines(session)

    # 2. Feed’den konu seç
    titles = get_feed_titles(session)
    suggestion = generate_premium_suggestion(titles)

    # 3. Rapor yaz
    write_report(ping_results, suggestion)

    logger.info("Tüm işlemler başarıyla tamamlandı")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.critical(f"Kritik hata: {e}", exc_info=True)
        sys.exit(1)
