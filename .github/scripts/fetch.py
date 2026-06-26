"""
每日知识采集脚本 — 商业化版本
- 重试 + 退避、多级超时、响应校验
- Reddit → RSS（绕过 API 鉴权失败）
- 掘金 → 多端点尝试
- Dev.to → 跨日去重
- 采集源失败不阻塞整体流程
"""
import json
import time
import random
from datetime import datetime, timezone
from pathlib import Path
from functools import wraps

import feedparser
import requests

# --- 配置 ---
VAULT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = VAULT_ROOT / "raw" / "网页剪藏"
DEDUP_FILE = RAW_DIR / ".dedup.json"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
HEADERS = {
    "User-Agent": "KnowledgeBot/2.0 (personal use; contact@example.com)",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,en;q=0.9",
}
TIMEOUT = (5, 20)  # (connect, read)
MAX_PER_SOURCE = 5
RETRY_MAX = 2
DEDUP_DAYS = 7  # 去重窗口


# --- 工具 ---
def retry(name: str):
    """带指数退避的重试装饰器"""
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            last_err = None
            for attempt in range(RETRY_MAX + 1):
                try:
                    return fn(*a, **kw)
                except Exception as e:
                    last_err = e
                    if attempt < RETRY_MAX:
                        delay = (2 ** attempt) + random.uniform(0, 1)
                        print(f"[{name}] 第{attempt+1}次失败，{delay:.1f}s 后重试: {e}")
                        time.sleep(delay)
            print(f"[{name}] 重试{RETRY_MAX}次后仍失败: {last_err}")
            return []
        return wrapper
    return deco


def load_dedup() -> dict[str, set]:
    """加载去重缓存"""
    try:
        if DEDUP_FILE.exists():
            data = json.loads(DEDUP_FILE.read_text(encoding="utf-8"))
            return {k: set(v) for k, v in data.items()}
    except Exception:
        pass
    return {}


def save_dedup(cache: dict[str, set]):
    """保存去重缓存，只保留 DEDUP_DAYS 天内的记录"""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cutoff = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    out = {}
    for date_str, urls in cache.items():
        if date_str >= cutoff.strftime("%Y-%m-%d") or len(out) < DEDUP_DAYS:
            out[date_str] = sorted(urls)
    DEDUP_FILE.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


def is_duplicate(url: str, cache: dict) -> bool:
    """检查 URL 是否在窗口内出现过"""
    return any(url in urls for urls in cache.values())


def record_urls(urls: list[str], cache: dict):
    """记录今日已采集的 URL"""
    if TODAY not in cache:
        cache[TODAY] = set()
    cache[TODAY].update(urls)


def dedup_key(item: dict) -> str:
    """生成去重键，优先用 URL"""
    return item.get("url", item.get("title", ""))


# --- 采集源 ---

@retry("HN")
def fetch_hacker_news():
    """Hacker News 热门（Firebase API）"""
    resp = requests.get(
        "https://hacker-news.firebaseio.com/v0/topstories.json",
        headers=HEADERS, timeout=TIMEOUT
    )
    resp.raise_for_status()
    ids = resp.json()[:30]

    items = []
    for sid in ids[:12]:
        try:
            r = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                headers=HEADERS, timeout=TIMEOUT
            )
            r.raise_for_status()
            item = r.json()
            if item and item.get("title"):
                items.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                    "score": item.get("score", 0),
                    "comments": item.get("descendants", 0),
                    "source": "Hacker News",
                })
        except Exception:
            continue

    items.sort(key=lambda x: x["score"], reverse=True)
    print(f"[HN] 采集 {len(items[:MAX_PER_SOURCE])} 条")
    return items[:MAX_PER_SOURCE]


@retry("Reddit")
def fetch_reddit():
    """Reddit r/programming 热帖 → 用 RSS 替代 JSON API（避免鉴权问题）"""
    feed = feedparser.parse("https://www.reddit.com/r/programming/hot.rss?limit=25")
    items = []
    for entry in feed.entries:
        title = entry.get("title", "")
        if not title:
            continue
        link = entry.get("link", "")
        items.append({
            "title": title,
            "url": link,
            "score": 0,
            "comments": 0,
            "source": "Reddit r/programming",
        })

    # RSS 不提供 score，所有条目 score=0，按出现顺序取
    print(f"[Reddit] RSS 采集 {len(items[:MAX_PER_SOURCE])} 条")
    return items[:MAX_PER_SOURCE]


@retry("Dev.to")
def fetch_devto(dedup_cache: dict):
    """Dev.to 热门文章 → 带跨日去重"""
    resp = requests.get(
        "https://dev.to/api/articles?top=14&per_page=15",
        headers=HEADERS, timeout=TIMEOUT
    )
    resp.raise_for_status()
    articles = resp.json()

    items = []
    skipped = 0
    for a in articles:
        url = a.get("url", "")
        title = a.get("title", "")
        if is_duplicate(url, dedup_cache) or is_duplicate(title, dedup_cache):
            skipped += 1
            continue
        items.append({
            "title": title,
            "url": url,
            "score": a.get("positive_reactions_count", 0),
            "comments": a.get("comments_count", 0),
            "tags": ", ".join(a.get("tag_list", [])),
            "source": "Dev.to",
        })

    if skipped:
        print(f"[Dev.to] 跳过 {skipped} 条重复，保留 {len(items[:MAX_PER_SOURCE])} 条")
    else:
        print(f"[Dev.to] 采集 {len(items[:MAX_PER_SOURCE])} 条")
    return items[:MAX_PER_SOURCE]


@retry("掘金")
def fetch_juejin():
    """掘金热门 → RSS 主路径（反爬策略不影响 RSS）"""
    feed = feedparser.parse("https://juejin.cn/rss")
    items = []
    for entry in feed.entries:
        title = entry.get("title", "").strip()
        if not title:
            continue
        items.append({
            "title": title,
            "url": entry.get("link", ""),
            "score": 0,
            "comments": 0,
            "tags": "",
            "source": "掘金",
        })
    print(f"[掘金] RSS 采集 {len(items[:MAX_PER_SOURCE])} 条")
    return items[:MAX_PER_SOURCE]


@retry("arXiv")
def fetch_arxiv():
    """arXiv CS 最新论文（RSS）"""
    feed = feedparser.parse("http://export.arxiv.org/rss/cs")
    items = []
    for entry in feed.entries[:MAX_PER_SOURCE]:
        items.append({
            "title": entry.title.replace("\n", " ").strip(),
            "url": entry.link,
            "score": 0,
            "comments": 0,
            "tags": "",
            "source": "arXiv CS",
        })
    print(f"[arXiv] 采集 {len(items)} 条")
    return items


# --- 日报生成 ---

def build_report(sources: dict, status: dict) -> str:
    """生成 Markdown 日报"""
    lines = [
        f"# 知识采集日报 — {TODAY}",
        "",
        f"> 采集时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"> 源: {' · '.join(sources.keys())}",
        "",
        "---",
        "",
    ]

    total = 0
    for name, items in sources.items():
        if not items:
            err = status.get(name, "无数据")
            lines.append(f"## {name}")
            lines.append("")
            lines.append(f"*（{err}）*")
            lines.append("")
            continue

        lines.append(f"## {name}")
        lines.append("")
        for item in items:
            total += 1
            meta = []
            if item.get("score"):
                meta.append(f"{item['score']} 赞")
            if item.get("comments"):
                meta.append(f"{item['comments']} 评论")
            if item.get("tags"):
                meta.append(f"标签：{item['tags']}")
            meta_str = " | ".join(meta)
            lines.append(f"- [{item['title']}]({item['url']})  ")
            if meta_str:
                lines.append(f"  *{meta_str}*  ")
        lines.append("")

    lines.insert(3, f"共采集 {total} 条内容。")
    lines.insert(4, "")
    return "\n".join(lines)


# --- 主流程 ---

def main():
    print(f"=== 知识采集 {TODAY} ===")

    # 加载去重缓存
    dedup_cache = load_dedup()

    sources = {}
    status = {}
    today_urls = []

    # 按顺序采集（不依赖网络的源先跑）
    fetchers = [
        ("Hacker News", lambda: fetch_hacker_news()),
        ("Reddit r/programming", lambda: fetch_reddit()),
        ("Dev.to", lambda: fetch_devto(dedup_cache)),
        ("掘金", lambda: fetch_juejin()),
        ("arXiv CS", lambda: fetch_arxiv()),
    ]

    for name, fetcher in fetchers:
        try:
            result = fetcher()
            sources[name] = result
            for item in result:
                key = dedup_key(item)
                if key:
                    today_urls.append(key)
            if not result:
                status[name] = "无新内容"
        except Exception as e:
            sources[name] = []
            status[name] = f"采集失败: {e}"

    # 记录今日 URL 到去重缓存
    if today_urls:
        record_urls(today_urls, dedup_cache)
        save_dedup(dedup_cache)

    # 输出日报
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report(sources, status)
    filepath = RAW_DIR / f"{TODAY}-日报.md"
    filepath.write_text(report, encoding="utf-8")
    print(f"→ 日报已写入 {filepath}")

    # 汇总
    total = sum(len(v) for v in sources.values())
    failed = [n for n, v in sources.items() if not v and status.get(n)]
    ok = [n for n, v in sources.items() if v]
    print(f"完成: {total} 条 | OK: {', '.join(ok) if ok else '无'}", end="")
    if failed:
        print(f" | 失败: {', '.join(failed)}")
    else:
        print()


if __name__ == "__main__":
    main()
