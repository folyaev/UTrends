import json
import feedparser
import logging
import re
import datetime
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from collections import defaultdict

FETCH_TIMEOUT_SECONDS = 5
SEARCH_MAX_WORKERS = 24
DEFAULT_HEADERS = {'User-Agent': 'UTrendsBot/1.0 (Telegram news aggregator)'}

def normalize_text(text):
    # Remove punctuation, make lowercase, split into words
    text = re.sub(r'[^\w\s]', '', text.lower())
    words = set(text.split())
    # remove short words
    return {w for w in words if len(w) > 3}

def parse_date(date_str):
    try:
        return time.mktime(date_str)
    except:
        return time.time()

def clean_source_name(feed_title: str, domain_fallback: str) -> str:
    """Возвращает короткое название источника.
    Если feed title слишком длинный или выглядит как описание — используем домен.
    """
    if not feed_title:
        return domain_fallback
    # Если название длиннее 30 символов или содержит 'все' + 'новости'/'посты' — подозрительно
    lower = feed_title.lower()
    if len(feed_title) > 30 or ('все' in lower and ('новост' in lower or 'пост' in lower or 'подряд' in lower)):
        return domain_fallback
    return feed_title


def fetch_source(url):
    items = []
    # Базовое имя по домену
    domain = url.split('/')[2].replace('www.', '') if 'youtube' not in url else 'YouTube'
    source_name = domain
    
    if "forbes.ru" in url:
        try:
            html = requests.get(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'},
                timeout=FETCH_TIMEOUT_SECONDS,
            ).text
            soup = BeautifulSoup(html, 'html.parser')
            source_name = "Forbes"
            seen_links = set()
            seen_titles = set()
            for a in soup.find_all('a', href=True):
                text = a.text.strip()
                href = a['href']
                # Только статьи (содержат /articles/ или /profile/ и т.п.)
                if not (href.startswith('/') or 'forbes.ru' in href):
                    continue
                full_link = f"https://www.forbes.ru{href}" if href.startswith('/') else href
                # Убираем query-параметры для дедупликации
                clean_link = full_link.split('?')[0].rstrip('/')
                title_norm = text.lower()
                if len(text) < 30:
                    continue
                if clean_link in seen_links or title_norm in seen_titles:
                    continue
                seen_links.add(clean_link)
                seen_titles.add(title_norm)
                items.append({
                    'title': text,
                    'link': full_link,
                    'time': time.time(),
                    'source_name': source_name
                })
        except Exception as e:
            logging.warning(f"Forbes parsing error: {e}")
    else:
        try:
            # Reddit требует кастомный User-Agent иначе блокирует
            resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=FETCH_TIMEOUT_SECONDS)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            raw_title = feed.feed.get('title', '')
            source_name = clean_source_name(raw_title, domain)

            for entry in feed.entries[:30]:
                is_youtube = 'youtube.com' in url
                pub_time = time.time()
                if entry.get('published_parsed'):
                    pub_time = time.mktime(entry.published_parsed)

                # YouTube: извлекаем просмотры из media:statistics
                views = ''
                if is_youtube:
                    stats = entry.get('media_statistics', {})
                    if isinstance(stats, dict):
                        raw_v = stats.get('views', '')
                        if raw_v:
                            try:
                                views = f"{int(raw_v):,}".replace(',', '\u00a0')
                            except ValueError:
                                views = raw_v

                items.append({
                    'title':       entry.get('title', ''),
                    'link':        entry.get('link', ''),
                    'time':        pub_time,
                    'source_name': source_name,
                    'views':       views,
                })
        except Exception as e:
            logging.warning(f"Feed parsing error for {url}: {e}")
            
    # keep unique titles and top latest 30 max to avoid spam
    unique_items = []
    seen = set()
    for item in items:
        if item['title'] not in seen:
            seen.add(item['title'])
            unique_items.append(item)
    return unique_items[:30]

def fetch_category_digest(file_path="feeds.json", time_window_hours=12):
    with open(file_path, "r", encoding="utf-8") as f:
        categories = json.load(f)

    cutoff_time = time.time() - (time_window_hours * 3600)
    digest = {}

    for cat_name, urls in categories.items():
        all_items = []
        for url in urls:
            items = fetch_source(url)
            for item in items:
                if item['time'] > cutoff_time:
                    item['words'] = normalize_text(item['title'])
                    item['source_url'] = url
                    all_items.append(item)

        # Clustering
        clusters = []
        for item in all_items:
            matched = False
            for cluster in clusters:
                # Check overlap
                overlap = item['words'].intersection(cluster['words'])
                # If they share at least 3 significant words, they are likely the same topic
                # Or if one title is very short and shares 2 words
                if len(overlap) >= 3 or (len(item['words']) > 0 and len(overlap) / len(item['words']) > 0.5):
                    # Only add if it's from a different source
                    sources_in_cluster = {x['source_url'] for x in cluster['items']}
                    if item['source_url'] not in sources_in_cluster:
                        cluster['items'].append(item)
                        cluster['words'].update(item['words']) # expand cluster vocabulary
                    matched = True
                    break
            
            if not matched:
                clusters.append({
                    'words': set(item['words']),
                    'items': [item],
                    'main_title': item['title']
                })
        
        # Кластеры из ≥2 источников — настоящий тренд
        valid_clusters = [c for c in clusters if len(c['items']) >= 2]
        valid_clusters.sort(key=lambda x: len(x['items']), reverse=True)

        if valid_clusters:
            digest[cat_name] = valid_clusters[:5]
        elif all_items:
            # Фоллбэк: нет пересечений — показываем топ-5 свежих одиночных новостей
            all_items.sort(key=lambda x: x['time'], reverse=True)
            seen_titles = set()
            singles = []
            for item in all_items:
                if item['title'] not in seen_titles:
                    seen_titles.add(item['title'])
                    singles.append({
                        'main_title': item['title'],
                        'items': [item]
                    })
                if len(singles) >= 5:
                    break
            if singles:
                digest[cat_name] = singles

    return digest

def search_feeds(query, file_path="feeds.json", time_window_hours=48):
    with open(file_path, "r", encoding="utf-8") as f:
        categories = json.load(f)

    cutoff_time = time.time() - (time_window_hours * 3600)
    results = []
    
    query_lower = query.lower()

    feed_sources = [
        (cat_name, url)
        for cat_name, urls in categories.items()
        for url in urls
    ]

    with ThreadPoolExecutor(max_workers=SEARCH_MAX_WORKERS) as executor:
        future_to_source = {
            executor.submit(fetch_source, url): (cat_name, url)
            for cat_name, url in feed_sources
        }
        for future in as_completed(future_to_source):
            cat_name, url = future_to_source[future]
            try:
                items = future.result()
            except Exception as e:
                logging.warning(f"Feed search error for {url}: {e}")
                continue
            for item in items:
                if item['time'] > cutoff_time:
                    if query_lower in item['title'].lower():
                        item['category'] = cat_name
                        item['source'] = item['source_name']
                        results.append(item)
                
    # Sort by time newest first
    results.sort(key=lambda x: x['time'], reverse=True)
    return results

def fetch_all_items(file_path="feeds.json", time_window_hours=3):
    with open(file_path, "r", encoding="utf-8") as f:
        categories = json.load(f)

    cutoff_time = time.time() - (time_window_hours * 3600)
    all_items = []

    for cat_name, urls in categories.items():
        for url in urls:
            items = fetch_source(url)
            for item in items:
                if item['time'] > cutoff_time:
                    all_items.append(item)
    return all_items

if __name__ == "__main__":
    d = fetch_category_digest()
    for cat, topics in d.items():
        print(f"--- {cat} ---")
        for t in topics:
            print(f"🚀 {t['main_title']} (Источников: {len(t['items'])})")
            for i in t['items']:
                print(f"  - {i['link']}")
