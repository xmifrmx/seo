#!/usr/bin/env python3
"""
Immaculate SEO Bot - Ultra Hyper Professional Edition
Organik trafik odaklı • Sıfır hata • Production-ready
"""

import os
import sys
import re
import json
import random
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

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

USER_AGENT = "ImmaculateSEOBot/4.0-Ultra (+https://github.com/xmifrmx/seo)"
TIMEOUT = 25
MAX_RETRIES = 5

INDEXNOW_KEY = os.getenv("INDEXNOW_KEY", "")

# ====================== LOGGING ======================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ImmaculateUltra")

# ====================== DATA CLASSES ======================
@dataclass
class TopicSuggestion:
    main_title: str
    alternative_titles: List[str]
    meta_description: str
    target_keyword: str
    secondary_keywords: List[str]
    content_outline: List[str]
    estimated_search_potential: str
    internal_link_ideas: List[str]

# ====================== SESSION ======================
def create_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=MAX_RETRIES,
        backoff_factor=1.8,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": USER_AGENT})
    return session

# ====================== SITEMAP & INDEXNOW ======================
def notify_search_engines(session: requests.Session) -> Dict[str, str]:
    results = {}

    pings = {
        "Google": f"https://www.google.com/ping?sitemap={SITEMAP_URL}",
        "Bing": f"https://www.bing.com/ping?sitemap={SITEMAP_URL}",
        "Yandex": f"https://webmaster.yandex.com/ping?sitemap={SITEMAP_URL}",
    }

    for name, url in pings.items():
        try:
            r = session.get(url, timeout=TIMEOUT)
            results[name] = str(r.status_code)
            logger.info(f"{name} → {r.status_code}")
        except Exception as e:
            results[name] = f"Error: {str(e)[:60]}"
            logger.warning(f"{name} failed")

    if INDEXNOW_KEY:
        try:
            payload = {
                "host": "immaculate.tr",
                "key": INDEXNOW_KEY,
                "keyLocation": f"{SITE_BASE}/{INDEXNOW_KEY}.txt",
                "urlList": [SITEMAP_URL, SITE_BASE]
            }
            r = session.post("https://api.indexnow.org/indexnow", json=payload, timeout=TIMEOUT)
            results["IndexNow"] = str(r.status_code)
            logger.info(f"IndexNow → {r.status_code}")
        except Exception as e:
            results["IndexNow"] = f"Error: {e}"
    else:
        results["IndexNow"] = "Skipped (no key)"

    return results

# ====================== FEED ======================
def get_recent_titles(session: requests.Session) -> List[str]:
    try:
        resp = session.get(FEED_URL, timeout=TIMEOUT)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)

        titles = []
        for entry in feed.entries[:30]:
            title = entry.get("title", "").strip()
            if title and len(title) > 15:
                titles.append(title)

        if not titles:
            # Fallback
            titles = re.findall(r"<title[^>]*>([^<]{15,})<", resp.text, re.I)
            titles = [t.strip() for t in titles][:20]

        logger.info(f"Feed'den {len(titles)} başlık alındı")
        return titles
    except Exception as e:
        logger.error(f"Feed hatası: {e}")
        return []

# ====================== ULTRA TOPIC ENGINE ======================
def generate_ultra_suggestion(existing_titles: List[str]) -> TopicSuggestion:
    # Mobil / Teknik Servis odaklı yüksek potansiyelli kalıplar
    high_potential_patterns = [
        "{device} inceleme 2026",
        "{device} alınır mı",
        "{device} sorunları ve çözümleri",
        "{device} batarya ömrü gerçek test",
        "{device} vs rakip karşılaştırma",
        "{device} firmware güncelleme rehberi",
        "{device} teknik servis ücretleri",
        "{device} ekran değişimi maliyeti",
        "En iyi {category} telefonlar 2026",
        "{device} kutu açılımı ve ilk izlenimler"
    ]

    # Feed'den cihaz isimlerini çıkarmaya çalış
    devices = []
    for t in existing_titles:
        # Basit cihaz yakalama
        found = re.findall(r"(iPhone \d+|Galaxy S\d+|Galaxy A\d+|Poco [A-Z0-9]+|Xiaomi \d+|Redmi [A-Z0-9]+|Vivo [A-Z0-9]+|Oppo [A-Z0-9]+|Huawei [A-Z0-9 ]+)", t, re.I)
        devices.extend(found)

    devices = list(set(devices))[:8] or ["Samsung Galaxy S26 FE", "Poco F9 Pro", "Xiaomi 15T", "iPhone 17"]

    selected_device = random.choice(devices)
    pattern = random.choice(high_potential_patterns)
    main_title = pattern.format(device=selected_device, category="orta segment")

    # Alternatif başlıklar
    alt_titles = [
        f"{selected_device} 2026 Detaylı İnceleme – Alınır mı?",
        f"{selected_device} Gerçek Kullanıcı Deneyimi ve Sorunları",
        f"{selected_device} Batarya, Performans ve Kamera Testi",
        f"{selected_device} Teknik Servis Rehberi ve Fiyatlar",
        f"2026'da {selected_device} Hâlâ Mantıklı mı?"
    ]

    secondary = [
        f"{selected_device} fiyat",
        f"{selected_device} özellikler",
        f"{selected_device} yorumlar",
        f"{selected_device} sorunları",
        "telefon teknik servis",
        "ekran değişimi"
    ]

    outline = [
        f"1. {selected_device} Genel Bakış ve Teknik Özellikler",
        "2. Tasarım ve Malzeme Kalitesi",
        "3. Ekran Deneyimi",
        "4. Performans ve Günlük Kullanım",
        "5. Batarya Ömrü Gerçek Test Sonuçları",
        "6. Kamera Performansı (Gündüz + Gece)",
        "7. Bilinen Sorunlar ve Çözümleri",
        "8. Teknik Servis ve Yedek Parça Durumu",
        "9. Rakip Modellerle Karşılaştırma",
        "10. Kimler Almalı? Sonuç ve Tavsiye"
    ]

    internal_links = [
        "Benzer incelemelere iç link verin",
        "Teknik servis hizmet sayfanıza link verin",
        "İlgili firmware / rom yazılarına link verin",
        "Kategori sayfasına (Telefon İncelemeleri) link verin"
    ]

    return TopicSuggestion(
        main_title=main_title,
        alternative_titles=alt_titles,
        meta_description=f"{selected_device} 2026 incelemesi: Batarya, kamera, performans ve bilinen sorunlar. Alınır mı? Gerçek kullanıcı deneyimi ve teknik servis bilgileri.",
        target_keyword=selected_device.lower() + " inceleme",
        secondary_keywords=secondary,
        content_outline=outline,
        estimated_search_potential="Orta-Yüksek (Cihaz popülerliğine göre)",
        internal_link_ideas=internal_links
    )

# ====================== REPORT ======================
def write_professional_report(ping_results: Dict[str, str], suggestion: TopicSuggestion) -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    content = f"""# Immaculate SEO Bot – Ultra Professional Raporu

**Tarih:** {now}  
**Versiyon:** 4.0 Ultra Hyper Professional

---

## 1. Arama Motoru Bildirim Sonuçları

| Motor       | Sonuç     | Durum |
|-------------|-----------|-------|
"""
    for motor, result in ping_results.items():
        status = "✅" if result.startswith("200") or result == "202" else "⚠️"
        content += f"| {motor:<11} | {result:<9} | {status} |\n"

    content += f"""
---

## 2. Bugünün Organik Trafik Odaklı Konu Önerisi

### Ana Başlık (Önerilen)
# {suggestion.main_title}

### Alternatif Başlıklar
"""
    for i, title in enumerate(suggestion.alternative_titles, 1):
        content += f"{i}. {title}\n"

    content += f"""
### Meta Description (150-160 karakter)
`{suggestion.meta_description}`

### Hedef Anahtar Kelime
**{suggestion.target_keyword}**

### İkincil Kelimeler
"""
    content += ", ".join(f"`{kw}`" for kw in suggestion.secondary_keywords)

    content += f"""

### Önerilen İçerik İskeleti (H2 Yapısı)
"""
    for item in suggestion.content_outline:
        content += f"- {item}\n"

    content += f"""
### İç Linkleme Önerileri
"""
    for idea in suggestion.internal_link_ideas:
        content += f"- {idea}\n"

    content += f"""
### Tahmini Arama Potansiyeli
{suggestion.estimated_search_potential}

---

## 3. Uygulama Tavsiyesi (Organik Trafik İçin)

1. Yukarıdaki ana başlığı veya alternatiflerden birini seç
2. En az 1500-2000 kelimelik kaliteli içerik yaz
3. Gerçek test sonuçları + ekran görüntüleri ekle
4. Teknik servis sayfana ve benzer incelemelere iç link ver
5. Yazıyı yayınladıktan sonra Google Search Console’dan “Dizin oluşturmayı iste”

---

*Bu rapor otomatik olarak üretilmiştir. Düzenli uygulama ile organik trafik artışı sağlanır.*
"""

    REPORT_FILE.write_text(content, encoding="utf-8")
    logger.info("Profesyonel rapor yazıldı")

    # index.md güncelle
    INDEX_FILE.write_text(f"""# Immaculate SEO Bot

**Ultra Hyper Professional Edition**

Son güncelleme: {now}

→ [Bugünün Detaylı Konu Önerisini Gör](latest-suggestion.md)
""", encoding="utf-8")

# ====================== MAIN ======================
def main() -> int:
    logger.info("=" * 70)
    logger.info("Immaculate SEO Bot 4.0 – Ultra Hyper Professional başlatıldı")
    logger.info("=" * 70)

    session = create_session()

    # 1. Arama motorlarına bildir
    ping_results = notify_search_engines(session)

    # 2. Feed al
    existing = get_recent_titles(session)

    # 3. Ultra öneri üret
    suggestion = generate_ultra_suggestion(existing)

    # 4. Rapor yaz
    write_professional_report(ping_results, suggestion)

    logger.info("Tüm işlemler başarıyla tamamlandı ✔")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.critical(f"Kritik hata: {e}", exp_info=True)
        sys.exit(1)
