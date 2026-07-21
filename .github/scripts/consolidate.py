"""
日报整合脚本 — 日采 → 周报/月报
- 读取指定日期范围内的日报
- 去重、按知识体系过滤
- 输出结构化摘要
用法：
    python consolidate.py week              # 本周周报
    python consolidate.py month             # 本月月报
    python consolidate.py 2026-07-04 2026-07-10  # 自定义范围
"""
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import Counter

VAULT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = VAULT_ROOT / "raw" / "网页剪藏"

# 知识体系过滤器（来自 CLAUDE.md）
DOMAIN_KEYWORDS = {
    "AI/机器学习": ["LLM", "Agent", "Transformer", "深度学习", "神经网络", "NLP", "CV",
                 "强化学习", "模型训练", "模型推理", "模型部署", "Prompt", "大模型",
                 "GPT", "Claude", "RAG", "embedding", "fine-tune", "token"],
    "编程语言": ["Python", "Java", "C/C++", "Rust", "Go", "TypeScript", "JavaScript",
               "编译器", "解释器", "类型系统", "JVM", "Spring", "异步", "虚拟线程"],
    "数据库": ["SQL", "MySQL", "PostgreSQL", "NoSQL", "HBase", "索引优化", "查询优化",
              "SQLite", "ORM", "TLA+"],
    "大数据": ["Hadoop", "Spark", "Hive", "Flink", "Kafka", "数据仓库", "数据管道", "ETL"],
    "数据分析": ["pandas", "数据可视化", "BI", "ECharts", "matplotlib", "统计分析"],
    "操作系统/Linux": ["进程", "内存管理", "文件系统", "内核", "Shell", "系统调用", "Linux"],
    "软件工程": ["设计模式", "微服务", "MVC", "SOLID", "CI/CD", "DevOps", "测试", "Git",
               "API设计", "重构", "架构"],
    "计算机基础": ["数据结构", "算法", "HTTP", "TCP", "计算机组成", "编码", "网络协议"],
    "数学/统计": ["概率论", "线性代数", "微积分", "离散数学", "假设检验", "MLE"],
    "容器/云原生": ["Docker", "Kubernetes", "容器化", "编排", "Podman", "MicroVM"],
    "Web开发": ["HTTP", "REST", "前后端", "Servlet", "Spring", "API", "React", "Vue"],
}

# 必须过滤
FILTER_PATTERNS = [
    r"职业迷茫|我的旅程|心态分享|burnout|mental.?health",
    r"隐私政策|讣告|考古|社会科学",
    r"键盘|显示器|椅子|耳机|推荐",
    r"Top\s*\d|本周精选|本月精选",
    r"游戏(?!.*编程|.*教育)",
    r"社区公告|Updated The Rules",
]


def parse_daily_report(filepath: Path) -> list[dict]:
    """解析日报，提取文章列表"""
    text = filepath.read_text(encoding="utf-8")
    articles = []
    current_source = None

    for line in text.split("\n"):
        # 检测来源标题
        if line.startswith("## "):
            current_source = line[3:].strip()
            continue

        # 解析文章条目
        match = re.match(r"- \[(.+?)\]\((.+?)\)", line)
        if match and current_source:
            title = match.group(1)
            url = match.group(2)
            articles.append({
                "title": title,
                "url": url,
                "source": current_source,
                "date": filepath.stem.replace("-日报", ""),
            })

    return articles


def match_domain(title: str) -> list[str]:
    """返回标题命中的知识领域"""
    matched = []
    title_lower = title.lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in title_lower:
                matched.append(domain)
                break
    return matched


def should_filter(title: str) -> bool:
    """标题是否应该被过滤"""
    for pattern in FILTER_PATTERNS:
        if re.search(pattern, title, re.IGNORECASE):
            return True
    return False


def get_date_range(mode: str) -> tuple[str, str]:
    """根据模式计算日期范围"""
    today = datetime.now(timezone.utc)

    if mode == "week":
        # 本周一到今天
        monday = today - timedelta(days=today.weekday())
        return monday.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

    elif mode == "month":
        # 本月 1 号到今天
        first = today.replace(day=1)
        return first.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

    else:
        raise ValueError(f"未知模式: {mode}")


def get_week_label(start: str) -> str:
    """周报标签：2026-W29"""
    d = datetime.strptime(start, "%Y-%m-%d")
    iso = d.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def get_month_label(start: str) -> str:
    """月报标签：2026-07"""
    return start[:7]


def consolidate(start_date: str, end_date: str, label: str, label_type: str):
    """核心整合逻辑"""
    # 收集日期范围内的所有日报
    reports = sorted(RAW_DIR.glob("*-日报.md"))
    in_range = []
    for rp in reports:
        date_str = rp.stem.replace("-日报", "")
        if start_date <= date_str <= end_date:
            in_range.append(rp)

    if not in_range:
        print(f"日期范围 {start_date} ~ {end_date} 内没有日报")
        return

    print(f"找到 {len(in_range)} 篇日报: {in_range[0].stem} ~ {in_range[-1].stem}")

    # 解析所有文章
    all_articles = []
    for rp in in_range:
        all_articles.extend(parse_daily_report(rp))

    print(f"共 {len(all_articles)} 篇文章")

    # 去重（按 URL）
    seen = set()
    unique = []
    for a in all_articles:
        if a["url"] not in seen:
            seen.add(a["url"])
            unique.append(a)

    print(f"去重后 {len(unique)} 篇")

    # 分类：命中领域 vs 过滤 vs 其他
    categorized = {}
    filtered = []
    other = []

    for a in unique:
        if should_filter(a["title"]):
            filtered.append(a)
            continue

        domains = match_domain(a["title"])
        if domains:
            for d in domains:
                categorized.setdefault(d, []).append(a)
        else:
            other.append(a)

    # 生成报告
    lines = [
        f"<!-- consolidated: {label} -->",
        f"# 知识采集{label_type} — {label}",
        "",
        f"> 覆盖: {start_date} ~ {end_date}",
        f"> 来源: {len(in_range)} 篇日报 → 去重 {len(unique)} 篇 → 命中 {sum(len(v) for v in categorized.values())} 篇",
        "",
        "---",
        "",
    ]

    # 按领域输出
    for domain, articles in sorted(categorized.items(), key=lambda x: len(x[1]), reverse=True):
        lines.append(f"## {domain} ({len(articles)} 篇)")
        lines.append("")
        for a in articles:
            lines.append(f"- [{a['title']}]({a['url']})  ")
            lines.append(f"  *{a['source']} · {a['date']}*  ")
        lines.append("")

    # 未分类但可能有价值的
    if other:
        lines.append(f"## 其他 ({len(other)} 篇)")
        lines.append("")
        lines.append("> 以下未匹配到知识体系关键词，可能值得人工看一眼：")
        lines.append("")
        for a in other:
            lines.append(f"- [{a['title']}]({a['url']})  ")
            lines.append(f"  *{a['source']} · {a['date']}*  ")
        lines.append("")

    # 已过滤
    if filtered:
        lines.append(f"## 已过滤 ({len(filtered)} 篇)")
        lines.append("")
        lines.append("| 条目 | 来源 |")
        lines.append("|------|------|")
        for a in filtered:
            safe_title = a['title'].replace("|", "\\|")
            lines.append(f"| [{safe_title}]({a['url']}) | {a['source']} |")
        lines.append("")

    # 写入
    out_path = RAW_DIR / f"{label}-{label_type}.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"→ {label_type}已写入 {out_path}")


def main():
    if len(sys.argv) == 2:
        mode = sys.argv[1]
        start, end = get_date_range(mode)
        if mode == "week":
            label = get_week_label(start)
            label_type = "周报"
        elif mode == "month":
            label = get_month_label(start)
            label_type = "月报"
        else:
            print("模式: week | month | YYYY-MM-DD YYYY-MM-DD")
            return
    elif len(sys.argv) == 3:
        start, end = sys.argv[1], sys.argv[2]
        label = f"{start}_{end}"
        # 判断是周报还是月报
        d1 = datetime.strptime(start, "%Y-%m-%d")
        d2 = datetime.strptime(end, "%Y-%m-%d")
        days = (d2 - d1).days
        if days <= 10:
            label_type = "周报"
            label = f"{get_week_label(start)}"
        else:
            label_type = "月报"
            label = f"{get_month_label(start)}"
    else:
        print("用法: python consolidate.py week|month|[start end]")
        return

    consolidate(start, end, label, label_type)


if __name__ == "__main__":
    main()
