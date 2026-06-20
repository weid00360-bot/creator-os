#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一手信息源（选题前置）—— 直接从源头拉，不吃二手聚合。
  · GitHub：近 N 天新建、星标最高的 AI/agent repo（什么工具/agent 正在火，最贴 build-in-public）
  · Hacker News：AI 相关高分讨论（技术圈原始热议）
免 auth。官方博客/论文原文按需用 WebFetch 单独抓（如 anthropic.com/research/...）。

用法：
  python3 firsthand.py            # GitHub + HN
  python3 firsthand.py --days 7   # GitHub 只看近7天新repo
"""
import sys, os, re, json, argparse, urllib.request, urllib.parse
from datetime import datetime, timedelta

AI_KW = re.compile("AI|agent|LLM|GPT|Claude|prompt|model|机器|智能|大模型", re.I)
_MON = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "爆款知识库", "对标监控")
YT_CONF = os.path.join(_MON, "youtube频道.txt")
BLOG_CONF = os.path.join(_MON, "博客RSS.txt")


def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "didi-firsthand/1.0"})
    return json.load(urllib.request.urlopen(req, timeout=25))


def github_trending(days, n):
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    q = urllib.parse.quote(f"(AI OR agent OR LLM OR prompt OR copilot) created:>{since}")
    url = f"https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page={n}"
    try:
        d = get(url, {"User-Agent": "didi-firsthand", "Accept": "application/vnd.github+json"})
        return [(r["full_name"], r["stargazers_count"], (r.get("description") or "").strip()[:90])
                for r in d.get("items", [])[:n]]
    except Exception as e:
        return [("(GitHub 拉取失败)", 0, str(e)[:60])]


def hn_ai(n, days=7):
    since = int((datetime.utcnow() - timedelta(days=days)).timestamp())
    params = urllib.parse.urlencode({
        "tags": "story", "query": "AI",
        "numericFilters": f"created_at_i>{since},points>40", "hitsPerPage": 50})
    url = "https://hn.algolia.com/api/v1/search_by_date?" + params  # 近N天，再按分排
    try:
        d = get(url)
        hits = sorted(d.get("hits", []), key=lambda h: -(h.get("points") or 0))
        return [(h.get("title", ""), h.get("points", 0), h.get("url") or
                 f"https://news.ycombinator.com/item?id={h.get('objectID')}")
                for h in hits[:n]]
    except Exception as e:
        return [("(HN 拉取失败)", 0, str(e)[:60])]


def _rss_get(url):
    try:
        return get(url, {"User-Agent": "didi-firsthand"})
    except Exception:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "didi-firsthand"})
            return urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
        except Exception as e:
            return ""


def huggingface(n):
    out = {"models": [], "papers": []}
    try:
        d = get(f"https://huggingface.co/api/models?sort=trendingScore&limit={n}",
                {"User-Agent": "didi-firsthand"})
        out["models"] = [(m.get("id", ""), m.get("likes", 0)) for m in d[:n]]
    except Exception:
        pass
    try:
        d = get(f"https://huggingface.co/api/daily_papers?limit={n}",
                {"User-Agent": "didi-firsthand"})
        out["papers"] = [(p.get("paper", {}).get("title", "").strip()[:60],
                          "https://huggingface.co/papers/" + p.get("paper", {}).get("id", ""))
                         for p in d[:n]]
    except Exception:
        pass
    return out


def blogs(n_per):
    if not os.path.exists(BLOG_CONF):
        return None
    urls = [u.strip() for u in open(BLOG_CONF) if u.strip() and not u.startswith("#")]
    if not urls:
        return None
    out = []
    for u in urls:
        raw = _rss_get(u)
        titles = re.findall(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", raw, re.S)
        host = u.split("/")[2] if "//" in u else u
        for t in titles[1:1 + n_per]:  # 跳过第1个(feed标题)
            out.append((host[:22], t.strip()[:60]))
    return out


def youtube(n_per):
    if not os.path.exists(YT_CONF):
        return None
    chans = [c.strip() for c in open(YT_CONF) if c.strip() and not c.startswith("#")]
    if not chans:
        return None
    out = []
    for c in chans:
        url = c if c.startswith("http") else f"https://www.youtube.com/feeds/videos.xml?channel_id={c}"
        raw = _rss_get(url)
        ch = re.search(r"<author>.*?<name>(.*?)</name>", raw, re.S)
        chname = ch.group(1) if ch else c[:16]
        ents = re.findall(r"<entry>(.*?)</entry>", raw, re.S)[:n_per]
        for e in ents:
            t = re.search(r"<title>(.*?)</title>", e, re.S)
            l = re.search(r'<link rel="alternate" href="(.*?)"', e)
            if t:
                out.append((chname, t.group(1).strip()[:60], l.group(1) if l else ""))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14, help="GitHub 看近N天新建repo")
    ap.add_argument("-n", type=int, default=12)
    args = ap.parse_args()

    print(f"# 一手信息源 · {datetime.now():%Y-%m-%d}\n")
    print(f"## GitHub 新热 repo（近{args.days}天新建·星标降序）")
    for name, stars, desc in github_trending(args.days, args.n):
        print(f"  ⭐{stars:>6} {name} — {desc}")
    print(f"\n## Hacker News · 近7天 AI 高分讨论")
    for title, pts, url in hn_ai(args.n):
        print(f"  ▲{pts:>4} {title}  {url}")
    hf = huggingface(8)
    print(f"\n## Hugging Face · 热门模型（trending）")
    for mid, likes in hf["models"]:
        print(f"  🤗 ❤{likes:>5} {mid}")
    if hf["papers"]:
        print(f"## Hugging Face · 每日精选论文")
        for title, url in hf["papers"][:5]:
            print(f"  📄 {title}  {url}")
    bl = blogs(2)
    print(f"\n## AI 官方博客（可配置 RSS）")
    if bl is None:
        print(f"  （未配置：在 {BLOG_CONF} 每行填一个可用 RSS，如 deepmind.google/blog/rss.xml）")
    else:
        for host, title in bl:
            print(f"  📰 [{host}] {title}")
    yt = youtube(3)
    print(f"\n## YouTube · 订阅的 AI 频道新视频")
    if yt is None:
        print(f"  （未配置：在 {YT_CONF} 每行填一个 AI 频道 channel_id 或 RSS 链接）")
    else:
        for ch, title, url in yt:
            print(f"  ▶ [{ch}] {title}  {url}")
    print("\n> 用法：GitHub 看'什么工具在火'→实测题；HN 看'技术圈在吵啥'→认知题；YouTube 看对标博主新作。")
    print(">       深挖某条 → WebFetch 官方博客/论文/repo README 原文（一手）。Instagram/TikTok 反爬抓不到。")


if __name__ == "__main__":
    main()
