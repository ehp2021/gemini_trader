#!/usr/bin/env python3
"""
Chinese Biotech News Scraper & Summarizer
Fetches top articles from Chinese biotech sources, translates and summarizes using Gemini
"""

import os
import json
import time
import smtplib
import requests
from datetime import datetime, date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import google.generativeai as genai

# ── Config ────────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
EMAIL_SENDER   = os.environ["EMAIL_SENDER"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]   # Gmail App Password
EMAIL_TO       = os.environ["EMAIL_TO"]
SMTP_HOST      = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT      = int(os.environ.get("SMTP_PORT", "587"))

TARGET_ARTICLES = 20
SUMMARY_WORDS   = 200

# ── News Sources ──────────────────────────────────────────────────────────────
SOURCES = [
    {
        "name": "36Kr Bio",
        "url": "https://36kr.com/newsflashes",
        "tag": "FierceBiotech-style",
        "selector": "article.newsflash-item, .news-item, .article-item",
        "rss": None,
    },
    {
        "name": "Bioon",
        "url": "https://www.bioon.com/",
        "tag": "STAT-style",
        "selector": ".article-list li, .news-list li, article",
        "rss": None,
    },
    {
        "name": "Yicai Global Biotech",
        "url": "https://www.yicai.com/news/",
        "tag": "BioPharma-style",
        "selector": ".news-list li, .article-item",
        "rss": None,
    },
    {
        "name": "Drugdu",
        "url": "https://www.drugdu.com/",
        "tag": "Regulatory/Pipeline",
        "selector": ".news-list li, .item",
        "rss": None,
    },
    {
        "name": "PharmCube",
        "url": "https://www.pharmcube.com/information/news",
        "tag": "Deals/Policy",
        "selector": ".news-item, article, .list-item",
        "rss": None,
    },
    {
        "name": "BioValley",
        "url": "https://www.bioon.com/topic/",
        "tag": "General Biotech",
        "selector": "tr, .news-item, li",
        "rss": None,
    },
    {
        "name": "CN Pharma News",
        "url": "https://www.cn-healthcare.com/articlewm/",
        "tag": "Healthcare/Pharma",
        "selector": ".article-list li, .news-item",
        "rss": None,
    },
    {
        "name": "MedCity (CN)",
        "url": "https://vcbeat.top/",
        "tag": "VC/Startup",
        "selector": ".post-list li, article, .news-item",
        "rss": None,
    },
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


# ── Scraping ──────────────────────────────────────────────────────────────────
def fetch_page(url: str, timeout: int = 15) -> BeautifulSoup | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  ⚠ Could not fetch {url}: {e}")
        return None


def extract_links_generic(soup: BeautifulSoup, base_url: str) -> list[dict]:
    """Generic link extraction – grab <a> tags with meaningful text."""
    articles = []
    seen = set()
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        href = a["href"]
        if len(text) < 10:
            continue
        # Skip nav / pagination links
        skip_kw = ["登录", "注册", "首页", "更多", "返回", "关于", "联系", "广告"]
        if any(k in text for k in skip_kw):
            continue
        # Resolve relative URLs
        if href.startswith("/"):
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            href = f"{parsed.scheme}://{parsed.netloc}{href}"
        elif not href.startswith("http"):
            continue
        if href in seen:
            continue
        seen.add(href)
        articles.append({"title": text, "url": href, "snippet": ""})
    return articles


def scrape_source(source: dict) -> list[dict]:
    print(f"  Scraping {source['name']} …")
    soup = fetch_page(source["url"])
    if not soup:
        return []
    articles = extract_links_generic(soup, source["url"])
    # Tag each article with its source
    for a in articles:
        a["source"] = source["name"]
        a["source_tag"] = source["tag"]
    return articles[:15]  # max 15 per source before dedup


def get_article_body(url: str) -> str:
    """Try to pull the main article text."""
    soup = fetch_page(url, timeout=20)
    if not soup:
        return ""
    # Remove scripts/styles
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    # Prefer <article> or main content divs
    for sel in ["article", "main", ".article-content", ".content", ".post-content", "#content"]:
        block = soup.select_one(sel)
        if block:
            return block.get_text(separator="\n", strip=True)[:3000]
    return soup.get_text(separator="\n", strip=True)[:3000]


# ── Gemini ────────────────────────────────────────────────────────────────────
def setup_gemini():
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-1.5-flash")


def score_and_select(model, raw_articles: list[dict]) -> list[dict]:
    """Ask Gemini to pick the top 20 most newsworthy biotech articles."""
    titles_json = json.dumps(
        [{"i": i, "title": a["title"], "source": a["source"]} for i, a in enumerate(raw_articles)],
        ensure_ascii=False,
    )
    prompt = f"""You are a biotech editor. From the list below, pick the {TARGET_ARTICLES} most 
newsworthy Chinese biotech articles published today. Prioritize: clinical trials, drug approvals, 
funding rounds, licensing deals, regulatory changes, and scientific breakthroughs.

Return ONLY a JSON array of the selected indices (e.g. [0, 3, 7, ...]).

Articles:
{titles_json}
"""
    try:
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        # Extract JSON array
        start, end = text.find("["), text.rfind("]")
        indices = json.loads(text[start : end + 1])
        return [raw_articles[i] for i in indices if i < len(raw_articles)]
    except Exception as e:
        print(f"  ⚠ Gemini selection failed: {e} — using first {TARGET_ARTICLES}")
        return raw_articles[:TARGET_ARTICLES]


def translate_and_summarize(model, article: dict, body: str) -> str:
    """Translate title + body into a ~200-word English summary."""
    content_for_prompt = body if body else article["title"]
    prompt = f"""You are a bilingual (Chinese→English) biotech journalist.

Translate and summarize the following Chinese biotech article in exactly ~{SUMMARY_WORDS} English words.
Structure: 1-sentence headline summary, then the key facts (who, what, drug/target, stage, deal terms if any, significance).
Be precise and factual. Do NOT pad with generic statements.

Source: {article['source']} ({article['source_tag']})
Title: {article['title']}
URL: {article['url']}

Article content:
{content_for_prompt}
"""
    try:
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        return f"[Summary unavailable: {e}]"


# ── Email ─────────────────────────────────────────────────────────────────────
def build_html_email(articles_with_summaries: list[dict]) -> str:
    today = date.today().strftime("%B %d, %Y")
    rows = ""
    for i, art in enumerate(articles_with_summaries, 1):
        rows += f"""
        <tr>
          <td style="padding:20px 0; border-bottom:1px solid #e8e8e8;">
            <p style="margin:0 0 4px 0; font-size:12px; color:#888; text-transform:uppercase; letter-spacing:1px;">
              {i:02d} &nbsp;·&nbsp; {art['source']} &nbsp;·&nbsp; {art['source_tag']}
            </p>
            <h2 style="margin:0 0 10px 0; font-size:17px; color:#1a1a2e; line-height:1.4;">
              <a href="{art['url']}" style="color:#1a1a2e; text-decoration:none;">{art['title']}</a>
            </h2>
            <p style="margin:0 0 10px 0; font-size:14px; color:#333; line-height:1.7;">
              {art['summary']}
            </p>
            <a href="{art['url']}" style="font-size:13px; color:#2563eb;">Read original →</a>
          </td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f4f6f9;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f9;padding:30px 0;">
    <tr><td align="center">
      <table width="680" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);">

        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);padding:32px 40px;">
            <p style="margin:0 0 6px 0;font-size:11px;color:#7ec8e3;letter-spacing:2px;text-transform:uppercase;">Daily Intelligence Report</p>
            <h1 style="margin:0;font-size:26px;color:#fff;font-weight:700;">🧬 China Biotech News</h1>
            <p style="margin:8px 0 0 0;font-size:14px;color:#a0b4c8;">{today} &nbsp;·&nbsp; Top {TARGET_ARTICLES} Stories</p>
          </td>
        </tr>

        <!-- Content -->
        <tr>
          <td style="padding:10px 40px 30px 40px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              {rows}
            </table>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#f8fafc;padding:20px 40px;border-top:1px solid #e8e8e8;">
            <p style="margin:0;font-size:12px;color:#999;text-align:center;">
              Translated &amp; summarized by Gemini AI &nbsp;·&nbsp; Sources: 36Kr Bio, Bioon, Yicai, Drugdu, PharmCube &amp; more<br>
              Delivered daily at 7:00 AM PST via GitHub Actions
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_email(html_body: str, article_count: int):
    today = date.today().strftime("%b %d, %Y")
    subject = f"🧬 China Biotech Daily — {article_count} Stories | {today}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_TO
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_TO.split(","), msg.as_string())
    print(f"✅ Email sent to {EMAIL_TO}")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"\n{'='*60}")
    print(f"China Biotech News — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")

    # 1. Scrape all sources
    print("\n[1/4] Scraping sources …")
    raw_articles = []
    for source in SOURCES:
        articles = scrape_source(source)
        print(f"      {source['name']}: {len(articles)} articles found")
        raw_articles.extend(articles)
        time.sleep(1.5)  # polite crawl delay

    print(f"  Total raw articles: {len(raw_articles)}")
    if not raw_articles:
        print("⚠ No articles found. Exiting.")
        return

    # 2. Deduplicate by URL
    seen_urls = set()
    deduped = []
    for a in raw_articles:
        if a["url"] not in seen_urls:
            seen_urls.add(a["url"])
            deduped.append(a)
    print(f"  After dedup: {len(deduped)} articles")

    # 3. Let Gemini select the top 20
    print("\n[2/4] Selecting top articles with Gemini …")
    model = setup_gemini()
    top_articles = score_and_select(model, deduped)
    print(f"  Selected: {len(top_articles)} articles")

    # 4. Fetch bodies + summarize
    print("\n[3/4] Fetching bodies & generating summaries …")
    results = []
    for i, art in enumerate(top_articles, 1):
        print(f"  [{i}/{len(top_articles)}] {art['title'][:60]} …")
        body = get_article_body(art["url"])
        summary = translate_and_summarize(model, art, body)
        art["summary"] = summary
        results.append(art)
        time.sleep(1)  # rate limit buffer

    # 5. Send email
    print("\n[4/4] Sending email …")
    html = build_html_email(results)
    send_email(html, len(results))
    print("\nDone! 🎉")


if __name__ == "__main__":
    main()
