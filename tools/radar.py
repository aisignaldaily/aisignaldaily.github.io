#!/usr/bin/env python3
"""AI Signal Daily trend radar. Run it in the Higgsfield sandbox (it has open internet):
    python3 repo/tools/radar.py [hours=6]  -> prints a ranked list of what is rising right now
Sources: official AI blogs, AI tech news, Hacker News front page, Hugging Face
and GitHub trending, Product Hunt, Google Trends (US). Stdlib only. A failing source is reported, never faked.
Use it to FIND topics; always verify facts at the primary source before posting."""
import json, re, sys, time, html, urllib.request
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

HOURS = float(sys.argv[1]) if len(sys.argv) > 1 else 6
NOW = time.time(); UA = {"User-Agent": "Mozilla/5.0 (AISignalDaily trend radar; contact aisignaldaily.news@gmail.com)"}
AI = re.compile(r"\b(AI|A\.I\.|GPT|ChatGPT|OpenAI|Claude|Anthropic|Gemini|DeepMind|LLM|Llama|Meta AI|Copilot|Grok|xAI|Mistral|"
                r"Nvidia|agent|agents|model|robot|robotics|humanoid|Sora|Veo|Midjourney|deepfake|Perplexity|Qwen|DeepSeek|Kimi)\b", re.I)
items, errors = [], []

def get(url, timeout=15):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()

def add(src, title, url, ts=None, score=0, ai_only=True):
    title = html.unescape(re.sub(r"\s+", " ", title or "")).strip()
    if not title or (ai_only and not AI.search(title)): return
    if ts and NOW - ts > HOURS * 3600: return
    items.append({"src": src, "title": title, "url": url, "age_h": round((NOW - ts) / 3600, 1) if ts else None, "score": score})

def feed(src, url, ai_only=True):
    try:
        root = ET.fromstring(get(url))
        for it in root.iter():
            tag = it.tag.split("}")[-1]
            if tag not in ("item", "entry"): continue
            t = l = d = None
            for c in it:
                ct = c.tag.split("}")[-1]
                if ct == "title": t = c.text
                elif ct == "link": l = c.get("href") or c.text
                elif ct in ("pubDate", "published", "updated") and not d: d = c.text
            ts = None
            if d:
                try: ts = parsedate_to_datetime(d).timestamp()
                except Exception:
                    try: ts = datetime.fromisoformat(d.replace("Z", "+00:00")).timestamp()
                    except Exception: pass
            add(src, t, l, ts, 0, ai_only)
    except Exception as e: errors.append(f"{src}: {e}")

FEEDS = [("OpenAI", "https://openai.com/news/rss.xml", False), ("Google AI blog", "https://blog.google/technology/ai/rss/", False),
         ("Google DeepMind", "https://deepmind.google/blog/rss.xml", False), ("Nvidia blog", "https://blogs.nvidia.com/feed/", True),
         ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/", False),
         ("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", False),
         ("Product Hunt", "https://www.producthunt.com/feed", True), ("Google Trends US", "https://trends.google.com/trending/rss?geo=US", True)]
for s, u, a in FEEDS: feed(s, u, a)

# Reddit blocks automated reads (HTTP 403); we respect that. Find Reddit buzz via normal web search instead.

try:
    d = json.loads(get("https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=60"))
    for h in d["hits"]: add("Hacker News", h["title"], h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}", h["created_at_i"], h.get("points", 0))
except Exception as e: errors.append(f"Hacker News: {e}")

try:
    d = json.loads(get("https://huggingface.co/api/trending?limit=10&type=model"))
    for r in d.get("recentlyTrending", []):
        rd = r.get("repoData", {}); add("Hugging Face trending", rd.get("id", ""), "https://huggingface.co/" + rd.get("id", ""), None, rd.get("likes", 0), False)
except Exception as e: errors.append(f"Hugging Face: {e}")

try:
    page = get("https://github.com/trending?since=daily").decode("utf-8", "ignore")
    for m in re.finditer(r'<h2 class="h3 lh-condensed">\s*<a[^>]*href="/([^"]+)"', page):
        repo = m.group(1); dm = re.search(re.escape(repo) + r'.{0,1500}?<p class="col-9[^"]*">\s*(.*?)\s*</p>', page, re.S)
        add("GitHub trending", repo + (" - " + re.sub("<[^>]+>", "", dm.group(1)) if dm else ""), "https://github.com/" + repo)
except Exception as e: errors.append(f"GitHub trending: {e}")

# Rank: things that appear in several sources first, then Reddit/HN score, then newest.
def key(t): return re.sub(r"[^a-z0-9 ]", "", t.lower())
words = {}
for it in items:
    for w in set(w for w in key(it["title"]).split() if len(w) > 4): words.setdefault(w, set()).add(it["src"].split(" (")[0])
for it in items:
    it["cross"] = max([len(words.get(w, ())) for w in set(key(it["title"]).split()) if len(w) > 4] or [1])
items.sort(key=lambda i: (-i["cross"], -(i["score"] or 0), i["age_h"] if i["age_h"] is not None else 99))
print(f"# AI trend radar, last {HOURS:g} h, {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC, {len(items)} items\n")
for i, it in enumerate(items[:60], 1):
    age = f"{it['age_h']}h ago" if it["age_h"] is not None else "now"
    print(f"{i}. [{it['src']}] {it['title']} ({age}, score {it['score']}, in {it['cross']} sources)\n   {it['url']}")
if errors: print("\nSources that failed (not faked, just missing):\n- " + "\n- ".join(errors))
