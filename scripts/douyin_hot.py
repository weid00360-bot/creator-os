#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音热榜拉取（选题前置·平台流量风向）—— 免签名直连官方 billboard 接口。
对迪迪的 AI 赛道：热榜大多是泛娱乐，所以默认 AI 过滤，只留对她有用的信号。

用法：
  python3 douyin_hot.py            # AI 相关热词（默认，给选题用）
  python3 douyin_hot.py --all      # 全部 50 条（看有没有可借的热梗句式）

两种用途：
  1) AI 话题杀进热榜 = 破圈强信号，优先做
  2) 借热榜句式当钩子（如"XX大测评"→"AI工具大测评"）
"""
import sys, json, re, argparse, subprocess

URL = "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
KW = re.compile("AI|人工智能|大模型|智能体|ChatGPT|GPT|Claude|Kimi|豆包|DeepSeek|Codex|agent|机器人|无人|自动驾驶|算法|编程|数字人|AIGC|提示词|copilot", re.I)


def fetch():
    out = subprocess.run(["curl", "-s", "-A", UA, "-e", "https://www.douyin.com/", URL],
                         capture_output=True, text=True).stdout
    try:
        return json.loads(out).get("word_list", [])
    except Exception:
        sys.exit("❌ 热榜拉取失败（接口可能变动）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="输出全部50条")
    args = ap.parse_args()
    wl = fetch()
    if not wl:
        sys.exit("❌ 热榜为空")

    if args.all:
        print(f"# 抖音热榜 · 全部 {len(wl)} 条\n")
        for i, w in enumerate(wl, 1):
            print(f"{i:>2}. {w.get('hot_value',0):>9} | {w.get('word','')}")
        return

    hits = [w for w in wl if KW.search(w.get("word", ""))]
    print(f"# 抖音热榜 AI 相关（{len(hits)}/{len(wl)} 条）")
    if not hits:
        print("\n今日热榜无 AI 相关词——纯泛娱乐，选题跳过热榜这一路（用 aihot + 对标即可）。")
        print("如需借热梗句式，跑 --all 看全部。")
        return
    print()
    for w in hits:
        print(f"  🤖 {w.get('hot_value',0):>9} | {w.get('word','')}  ← AI破圈，强信号，优先做")


if __name__ == "__main__":
    main()
