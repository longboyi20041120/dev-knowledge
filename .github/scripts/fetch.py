"""
每日知识采集脚本
从多个源抓取热门内容，写入 raw/网页剪藏/
无 API Key 依赖，全部使用免费公开接口
"""
import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import feedparser
import requests

# --- 配置 ---
VAULT_ROOT = Path(__file__).resolve().parents[2]  # 编程知识库 根目录
RAW_DIR = VAULT_ROOT / "raw" / "网页剪藏"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
HEADERS = {"User-Agent": "KnowledgeBot/1.0 (personal use)"}
TIMEOUT = 15
MAX_PER_SOURCE = 5  # 每个源最多取几篇


def fetch_hacker_news():
    """Hacker News 首页热门（免费 Firebase API）"""
    try:
        # 先拿 top story IDs
        resp = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            headers=HEADERS, timeout=TIMEOUT
        )
        resp.raise_for_status()
        ids = resp.json()[:30]

        items = []
        for sid in ids[:12]:  # 只取前 12 篇详情
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
        return items[:MAX_PER_SOURCE]
    except Exception as e:
        print(f"[HN] 采集失败: {e}")
        return []


def fetch_reddit():
    """Reddit r/programming 热帖（.json 接口免费）"""
    try:
        resp = requests.get(
            "https://www.reddit.com/r/programming/hot.json?limit=15",
            headers=HEADERS, timeout=TIMEOUT
        )
        resp.raise_for_status()
        posts = resp.json()["data"]["children"]

        items = []
        for p in posts:
            d = p["data"]
            if d.get("stickied"):
                continue
            items.append({
                "title": d.get("title", ""),
                "url": f"https://reddit.com{d.get('permalink', '')}",
                "score": d.get("score", 0),
                "comments": d.get("num_comments", 0),
                "source": "Reddit r/programming",
            })

        items.sort(key=lambda x: x["score"], reverse=True)
        return items[:MAX_PER_SOURCE]
    except Exception as e:
        print(f"[Reddit] 采集失败: {e}")
        return []


def fetch_devto():
    """Dev.to 热门文章（免费 API）"""
    try:
        resp = requests.get(
            "https://dev.to/api/articles?top=7&per_page=10",
            headers=HEADERS, timeout=TIMEOUT
        )
        resp.raise_for_status()
        articles = resp.json()

        items = []
        for a in articles:
            items.append({
                "title": a.get("title", ""),
                "url": a.get("url", ""),
                "score": a.get("positive_reactions_count", 0),
                "comments": a.get("comments_count", 0),
                "tags": ", ".join(a.get("tag_list", [])),
                "source": "Dev.to",
            })

        items.sort(key=lambda x: x["score"], reverse=True)
        return items[:MAX_PER_SOURCE]
    except Exception as e:
        print(f"[Dev.to] 采集失败: {e}")
        return []


def fetch_juejin():
    """掘金热门（爬取接口）"""
    try:
        resp = requests.post(
            "https://api.juejin.cn/recommend_api/v1/article/recommend_all_feed",
            json={"id_type": 2, "sort_type": 200, "cursor": "0", "limit": 10},
            headers={**HEADERS, "Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()

        items = []
        for entry in data.get("data", []):
            info = entry.get("article_info", {})
            if not info:
                continue
            items.append({
                "title": info.get("title", ""),
                "url": f"https://juejin.cn/post/{info.get('article_id', '')}",
                "score": info.get("digg_count", 0),
                "comments": info.get("comment_count", 0),
                "tags": ", ".join(t.get("tag_name", "") for t in info.get("tags", [])),
                "source": "掘金",
            })

        items.sort(key=lambda x: x["score"], reverse=True)
        return items[:MAX_PER_SOURCE]
    except Exception as e:
        print(f"[掘金] 采集失败: {e}")
        return []


def fetch_arxiv():
    """arXiv CS 最新论文（RSS feed）"""
    try:
        feed = feedparser.parse(
            "http://export.arxiv.org/rss/cs"
        )
        items = []
        for entry in feed.entries[:MAX_PER_SOURCE]:
            arxiv_id = entry.id.split("/")[-1]
            items.append({
                "title": entry.title.replace("\n", " ").strip(),
                "url": entry.link,
                "score": 0,
                "comments": 0,
                "tags": entry.get("tags", ""),
                "source": "arXiv CS",
            })
        return items
    except Exception as e:
        print(f"[arXiv] 采集失败: {e}")
        return []


def build_report(sources: dict) -> str:
    """生成 Markdown 日报"""
    lines = [
        f"# 知识采集日报 — {TODAY}",
        "",
        f"> 自动采集时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"> 采集源: Hacker News, Reddit, Dev.to, 掘金, arXiv",
        "",
        "---",
        "",
    ]

    total_items = 0
    for source_name, items in sources.items():
        if not items:
            lines.append(f"## {source_name}")
            lines.append("")
            lines.append("*（采集失败或无新内容）*")
            lines.append("")
            continue

        lines.append(f"## {source_name}")
        lines.append("")
        for item in items:
            total_items += 1
            title = item["title"]
            url = item.get("url", "")
            score = item.get("score", 0)
            tags = item.get("tags", "")
            meta_parts = []
            if score:
                meta_parts.append(f"{score} 赞")
            if item.get("comments"):
                meta_parts.append(f"{item['comments']} 评论")
            if tags:
                meta_parts.append(f"标签：{tags}")
            meta = " | ".join(meta_parts)

            lines.append(f"- [{title}]({url})  ")
            if meta:
                lines.append(f"  *{meta}*  ")

        lines.append("")

    lines.insert(3, f"共采集 {total_items} 条内容。")
    lines.insert(4, "")

    return "\n".join(lines)


def main():
    print(f"=== 知识采集 {TODAY} ===")

    sources = {
        "Hacker News": fetch_hacker_news(),
        "Reddit r/programming": fetch_reddit(),
        "Dev.to": fetch_devto(),
        "掘金": fetch_juejin(),
        "arXiv CS": fetch_arxiv(),
    }

    total = sum(len(v) for v in sources.values())
    print(f"采集完成，共 {total} 条")

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    report = build_report(sources)
    filepath = RAW_DIR / f"{TODAY}-日报.md"
    filepath.write_text(report, encoding="utf-8")
    print(f"已写入 {filepath}")


if __name__ == "__main__":
    main()
