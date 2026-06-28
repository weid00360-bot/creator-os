#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多平台 AI 热点聚合（选题前置）—— 各源各拉各的，合并去重 + AI 关键词过滤。
第一批源：Hacker News（官方API）+ arXiv（官方API）+ GitHub Trending（稳定镜像）。
设计：模块化，加一个平台加一个 fetch_ 函数；单源失败不拖垮整体。

用法：
  python3 hot_aggregator.py              # 三源聚合，AI 过滤，markdown 输出
  python3 hot_aggregator.py --all        # 不做 AI 过滤，看全部
  python3 hot_aggregator.py --limit 10   # 每源最多 N 条
"""
import sys, json, re, argparse, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
KW = re.compile("AI|artificial intelligence|machine learning|\\bML\\b|\\bLLM\\b|GPT|Claude|Anthropic|OpenAI|Gemini|Llama|"
                "agent|model|neural|deep learning|transformer|diffusion|大模型|智能体|人工智能|提示词|prompt", re.I)


def _get(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def fetch_hackernews(limit):
    """Hacker News 官方 Firebase API：取 topstories 前若干条。"""
    ids = json.loads(_get("https://hacker-news.firebaseio.com/v0/topstories.json"))[:limit * 3]
    out = []
    def one(i):
        try:
            it = json.loads(_get(f"https://hacker-news.firebaseio.com/v0/item/{i}.json"))
            if it and it.get("title"):
                return {"source": "HackerNews", "title": it["title"],
                        "url": it.get("url") or f"https://news.ycombinator.com/item?id={i}",
                        "score": it.get("score", 0)}
        except Exception:
            return None
    with ThreadPoolExecutor(max_workers=10) as ex:
        for r in ex.map(one, ids):
            if r:
                out.append(r)
    out.sort(key=lambda x: x["score"], reverse=True)
    return out[:limit * 2]


def fetch_arxiv(limit):
    """arXiv 官方 API：cs.AI / cs.LG / cs.CL 最近提交。"""
    q = ("http://export.arxiv.org/api/query?search_query="
         "cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CL"
         f"&sortBy=submittedDate&sortOrder=descending&max_results={limit}")
    xml = _get(q)
    out = []
    for m in re.finditer(r"<entry>(.*?)</entry>", xml, re.S):
        e = m.group(1)
        t = re.search(r"<title>(.*?)</title>", e, re.S)
        link = re.search(r'<id>(.*?)</id>', e, re.S)
        if t:
            out.append({"source": "arXiv", "title": re.sub(r"\s+", " ", t.group(1)).strip(),
                        "url": link.group(1).strip() if link else "", "score": 0})
    return out


def fetch_github_trending(limit):
    """GitHub Trending：无官方 API，用稳定镜像 ossinsight / 备用 trending API。"""
    try:
        data = json.loads(_get("https://api.ossinsight.io/v1/trends/repos/?period=past_24_hours"))
        rows = data.get("data", {}).get("rows", [])[:limit * 2]
        return [{"source": "GitHubTrend", "title": f"{r.get('repo_name','')}: {r.get('description','')}".strip(": "),
                 "url": f"https://github.com/{r.get('repo_name','')}", "score": int(r.get("stars", 0) or 0)}
                for r in rows]
    except Exception:
        # 备用镜像
        data = json.loads(_get("https://gh-trending-api.de.a9sapp.eu/repositories?since=daily"))
        return [{"source": "GitHubTrend", "title": f"{r.get('repositoryName','')}: {r.get('description','')}".strip(": "),
                 "url": r.get("url", ""), "score": int(r.get("totalStars", 0) or 0)}
                for r in data[:limit * 2]]


SOURCES = [fetch_hackernews, fetch_arxiv, fetch_github_trending]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="不做 AI 过滤")
    ap.add_argument("--limit", type=int, default=15, help="每源条数基数")
    args = ap.parse_args()

    items, failed = [], []
    for f in SOURCES:
        try:
            items += f(args.limit)
        except Exception as e:
            failed.append(f"{f.__name__}: {e}")

    if not args.all:
        items = [it for it in items if KW.search(it["title"])]

    # 去重（按标题前 60 字）
    seen, uniq = set(), []
    for it in items:
        k = it["title"][:60].lower()
        if k not in seen:
            seen.add(k)
            uniq.append(it)

    by_src = {}
    for it in uniq:
        by_src.setdefault(it["source"], []).append(it)

    print(f"# 多平台 AI 热点聚合（{len(uniq)} 条 / {len(SOURCES)} 源）\n")
    for src, lst in by_src.items():
        print(f"## {src}（{len(lst)}）")
        for it in lst:
            sc = f" ★{it['score']}" if it["score"] else ""
            print(f"- [{it['title']}]({it['url']}){sc}")
        print()
    if failed:
        print("> ⚠️ 失败源：" + " ｜ ".join(failed))


if __name__ == "__main__":
    main()
