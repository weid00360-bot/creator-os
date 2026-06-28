#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
words.json（词级时间戳）→ timeline.json（一屏屏字幕，含时间/分词/关键词高亮）
机械活；B-roll 插图点和精修由 Claude 在生成后人工补。

流程：单字时间戳 → 同音校正 → jieba 分词(贴时间戳) → 按停顿切屏 → 关键词高亮。

用法:
    python3 build_timeline.py projects/练手01 [--fps 30] [--source input.mov]
"""
import os, json, re, argparse
import jieba

# ── 分屏参数 ──────────────────────────────────────────────────
GAP_BREAK = 0.30      # 相邻词停顿 > 0.30s 视作自然断句，切新屏
MAX_DUR   = 2.2       # 一屏最长秒数
MAX_WORDS = 5         # 一屏最多词
HOLD_TAIL = 6         # 末屏多停几帧

# ── ASCII 错字修正（whisper 把英文当单元，安全替换）────────────
ASCII_FIX = {"pront": "prompt", "Pront": "prompt", "clod": "Claude", "Clod": "Claude"}

# ── 中文同音错字：等长整词替换（只在该词内生效，不误伤其他字）──
CONTEXT_FIX = [
    ("挨个适了", "挨个试了"), ("万份", "万粉"), ("堵定", "笃定"),
    ("做报款", "做爆款"), ("邦尼高校", "帮你高效"), ("听天有命", "听天由命"),
    ("卡斯克", "卡兹克"), ("信息园", "信息源"), ("证文", "正文"), ("国脚部", "裹脚布"),
]

# ── 字符流级同音修正：在拼接全文上等长替换（标点无关、不依赖词边界，最稳）──
# 越长的放前面，避免短串先替换破坏长串。
CHAR_FIX = [
    ("加全剪掉", "加权减掉"), ("以中为始", "以终为始"), ("币还回来", "闭环回来"),
    ("迈克一样", "卖课一样"), ("开题钩子", "开头钩子"), ("我是弟弟", "我是迪迪"),
    ("范柳亮", "泛流量"), ("范零量", "泛流量"), ("范流量", "泛流量"),
    ("玩播", "完播"), ("加全", "加权"), ("收美", "收尾"), ("越为越", "越喂越"),
    ("副盘", "复盘"), ("练录", "链路"), ("养量", "养料"), ("铺了", "扑了"),
]

def apply_char_fix(chars):
    """字符流上做等长替换：拼全文→定位→按位置改字符。时间戳不变。"""
    full = "".join(c["c"] for c in chars)
    for wrong, right in CHAR_FIX:
        if len(wrong) != len(right):
            continue
        start = 0
        while True:
            pos = full.find(wrong, start)
            if pos < 0:
                break
            for k in range(len(wrong)):
                chars[pos + k]["c"] = right[k]
            full = full[:pos] + right + full[pos + len(right):]
            start = pos + len(right)
    return chars

# ── 关键词高亮规则（按优先级；每屏最多 2 个）(正则,颜色,emoji,punch) ──
HL_RULES = [
    (r"求求了|打假|草台班子|垃圾|淘汰|pass|马甲|免费领|听天由命", "red", "", True),
    (r"\d|万|百分之|五条|第[一二三四五]", "yellow", "", True),
    (r"token", "yellow", "💸", False),
    (r"prompt|Claude|GitHub|精选库|标准化|稳定", "green", "", False),
]

def apply_context_fix(words):
    n = len(words)
    for wrong, right in CONTEXT_FIX:
        L = len(wrong)
        for i in range(n - L + 1):
            if "".join(words[i + k]["w"] for k in range(L)) == wrong:
                for k in range(L):
                    words[i + k]["w"] = right[k]
    return words

def build_char_stream(words):
    """单元流 → 逐字符流，每字符带 start/end（ASCII 修正后按字符摊时间）。"""
    chars = []
    for u in words:
        w = ASCII_FIX.get(u["w"], u["w"])
        for ch in w:
            chars.append({"c": ch, "start": u["start"], "end": u["end"]})
    return chars

def tokenize(chars):
    """jieba 分词并贴回时间戳。返回 [{t, start, end}]。"""
    full = "".join(c["c"] for c in chars)
    toks, idx, out = jieba.lcut(full), 0, []
    for tok in toks:
        L = len(tok)
        seg = chars[idx:idx + L]
        idx += L
        if tok.strip() == "":
            continue
        out.append({"t": tok, "start": seg[0]["start"], "end": seg[-1]["end"]})
    return out

def segment(tokens):
    """按停顿/时长/词数切屏。"""
    screens, cur = [], []
    for t in tokens:
        if cur:
            gap = t["start"] - cur[-1]["end"]
            dur = t["end"] - cur[0]["start"]
            if gap > GAP_BREAK or dur > MAX_DUR or len(cur) >= MAX_WORDS:
                screens.append(cur); cur = []
        cur.append(t)
    if cur:
        screens.append(cur)
    return screens

def apply_highlights(words, budget=2):
    n = 0
    for word in words:
        if n >= budget:
            break
        for pat, color, emoji, punch in HL_RULES:
            if re.search(pat, word["t"]):
                word["highlight"] = color
                if emoji:
                    word["emoji"] = emoji
                if punch:
                    word["punch"] = True
                n += 1
                break
    return words

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projdir")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--source", default="input.mov")
    ap.add_argument("--layout", default="v", choices=["v", "h"])  # v=竖版 h=横版
    args = ap.parse_args()
    fps = args.fps

    with open(os.path.join(args.projdir, "words.json"), encoding="utf-8") as f:
        words = json.load(f)
    words = apply_context_fix(words)
    tokens = tokenize(apply_char_fix(build_char_stream(words)))
    screens = segment(tokens)

    captions = []
    for i, toks in enumerate(screens):
        s_start = toks[0]["start"]
        start_f = round(s_start * fps)
        if i + 1 < len(screens):
            end_f = round(screens[i + 1][0]["start"] * fps)
        else:
            end_f = round(toks[-1]["end"] * fps) + HOLD_TAIL
        end_f = max(end_f, start_f + 8)
        words_out = [{"t": t["t"], "at": max(0, round((t["start"] - s_start) * fps))} for t in toks]
        apply_highlights(words_out)
        captions.append({"start": start_f, "end": end_f, "words": words_out})

    # B-roll/图卡点：横版读 broll_h.json，竖版读 broll.json（语义层，重跑分词不清掉）
    broll_file = "broll_h.json" if args.layout == "h" else "broll.json"
    broll_path = os.path.join(args.projdir, broll_file)
    broll = []
    if os.path.exists(broll_path):
        with open(broll_path, encoding="utf-8") as f:
            broll = json.load(f)

    if args.layout == "h":
        # 横版：1920×1080 + 圆窗人物 + 防黑屏 fallback。person/fallback 可被 person.json 覆盖。
        person = {"cropX": 103, "cropY": 440, "cropSize": 875, "diameter": 300,
                  "marginRight": 60, "marginTop": 60, "brightness": 0.86, "saturate": 0.9, "name": "迪迪"}
        fallback = "assets/五要素闭环图_hero.png"
        pj = os.path.join(args.projdir, "person.json")
        if os.path.exists(pj):
            with open(pj, encoding="utf-8") as f:
                cfg = json.load(f)
            person.update(cfg.get("person", {}))
            fallback = cfg.get("fallbackAsset", fallback)
        timeline = {
            "fps": fps, "width": 1920, "height": 1080, "source": args.source,
            "captions": captions, "broll": broll,
            "person": person, "fallbackAsset": fallback,
            "bgAsset": "assets/bg_tv.png",
        }
    else:
        timeline = {
            "fps": fps, "width": 1080, "height": 1920, "source": args.source,
            "captions": captions, "broll": broll,
        }
    out = os.path.join(args.projdir, "timeline.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)
    print(f"✅ {len(captions)} 屏字幕 · {args.layout}版 · broll {len(broll)} 段 → {out}")

if __name__ == "__main__":
    main()
