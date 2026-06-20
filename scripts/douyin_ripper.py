#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音爆款采集器 —— 一个链接 → 数据 + 逐字稿
用法:
    python3 douyin_ripper.py "8.48 复制打开抖音...https://v.douyin.com/xxxx/"
    python3 douyin_ripper.py "https://v.douyin.com/xxxx/" --model small
    python3 douyin_ripper.py "<链接>" --no-transcribe   # 只抓数据不转写

输出到: 爆款知识库/原始素材/<item_id>/
    meta.json       结构化数据（标题/作者/赞藏转评/时长/标签）
    transcript.txt  口播逐字稿（Whisper 转写，含同音错字，拆解时人工校正）
    video.mp4       原始视频（可选保留）
依赖: ffmpeg, openai-whisper(python)  —— 已确认本机具备
"""
import sys, os, re, json, subprocess, argparse, urllib.parse, time
from datetime import datetime

UA_DESKTOP = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
UA_MOBILE = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "爆款知识库", "原始素材")


def extract_url(text):
    """从分享口令文本里揪出链接"""
    m = re.search(r'https?://[^\s]+', text)
    if not m:
        sys.exit("❌ 没在输入里找到链接")
    return m.group(0)


def curl(url, ua, headers=None, follow=True):
    cmd = ["curl", "-s", "-A", ua]
    if follow:
        cmd.append("-L")
    if headers:
        for h in headers:
            cmd += ["-H", h]
    cmd.append(url)
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def resolve_item_id(url):
    """短链 → 真实页面 → aweme item_id（视频 /video/ 或图文 /note/）"""
    m = re.search(r'/(?:video|note)/(\d+)', url)
    if m:
        return m.group(1), url
    head = subprocess.run(["curl", "-sI", "-A", UA_DESKTOP, url],
                          capture_output=True, text=True).stdout
    loc = re.search(r'(?i)location:\s*(\S+)', head)
    if loc:
        real = loc.group(1).strip()
        m = re.search(r'/(?:video|note)/(\d+)', real)
        if m:
            return m.group(1), real
    sys.exit("❌ 无法解析出 item_id，可能链接已失效")


def grab1(pattern, html, default=None, cast=str):
    m = re.search(pattern, html)
    if not m:
        return default
    try:
        return cast(m.group(1))
    except Exception:
        return default


def parse_share_page(item_id):
    # 先按视频页抓；抓不到再按图文 note 页抓
    url = f"https://www.iesdouyin.com/share/video/{item_id}/?region=US"
    html = curl(url, UA_MOBILE)
    if len(html) < 1000 or '"desc"' not in html:
        url = f"https://www.iesdouyin.com/share/note/{item_id}/?region=US"
        html = curl(url, UA_MOBILE)
    if len(html) < 1000:
        sys.exit("❌ 分享页抓取失败（可能反爬或链接失效）")
    desc = grab1(r'"desc":"([^"]*)"', html, "")
    meta = {
        "item_id": item_id,
        "share_url": url,
        "desc": desc,
        "nickname": grab1(r'"nickname":"([^"]*)"', html, ""),
        "digg_count": grab1(r'"digg_count":(\d+)', html, 0, int),
        "comment_count": grab1(r'"comment_count":(\d+)', html, 0, int),
        "collect_count": grab1(r'"collect_count":(\d+)', html, 0, int),
        "share_count": grab1(r'"share_count":(\d+)', html, 0, int),
        "play_count": grab1(r'"play_count":(\d+)', html, 0, int),
        "duration_ms": grab1(r'"duration":(\d{4,})', html, 0, int),
        "hashtags": sorted(set(re.findall(r'"hashtag_name":"([^"]*)"', html))),
        "play_vid": grab1(r'"play_addr":\{"uri":"([^"]+)"', html, ""),
        "create_time": grab1(r'"create_time":(\d{9,})', html, 0, int),  # 发布时间(unix)
    }
    # 算几个比例方便拆解
    d = meta["digg_count"] or 1
    meta["收藏赞比"] = round(meta["collect_count"] / d, 3)
    meta["分享赞比"] = round(meta["share_count"] / d, 3)
    meta["评论赞比"] = round(meta["comment_count"] / d, 3)
    meta["时长秒"] = round(meta["duration_ms"] / 1000, 1)
    # ⏱️ 时间线：没有发布时长，绝对点赞数毫无意义（5分钟的1133赞 ≠ 3天的1133赞）
    ct = meta["create_time"]
    if ct:
        meta["发布时间"] = datetime.fromtimestamp(ct).strftime("%Y-%m-%d %H:%M")
        age_h = (time.time() - ct) / 3600
        meta["发布时长小时"] = round(age_h, 1)
        meta["赞每小时"] = round(meta["digg_count"] / age_h, 1) if age_h > 0 else None
        meta["数据成熟"] = age_h >= 48  # <48h 数据未稳，别下结论
    else:
        meta["发布时间"] = meta["发布时长小时"] = meta["赞每小时"] = None
        meta["数据成熟"] = None
    return meta


def download_video(vid, out_mp4):
    url = f"https://aweme.snssdk.com/aweme/v1/play/?video_id={vid}&ratio=720p&line=0"
    subprocess.run(["curl", "-sL", "-A", UA_DESKTOP, "-e",
                    "https://www.douyin.com/", url, "-o", out_mp4], check=True)
    if os.path.getsize(out_mp4) < 10000:
        sys.exit("❌ 视频下载失败（文件过小）")


def transcribe(mp4, out_txt, model_name):
    wav = mp4.replace(".mp4", ".wav")
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-i", mp4, "-ar", "16000",
                    "-ac", "1", "-vn", wav], capture_output=True, check=True)
    import whisper
    print(f"  加载 Whisper 模型 {model_name} ...", flush=True)
    model = whisper.load_model(model_name)
    print("  转写中（CPU，按时长几分钟）...", flush=True)
    r = model.transcribe(wav, language="zh", fp16=False)
    with open(out_txt, "w") as f:
        f.write(r["text"])
    os.remove(wav)
    return len(r["text"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("link", help="抖音分享链接或口令文本")
    ap.add_argument("--model", default="small", help="whisper 模型 tiny/base/small/medium")
    ap.add_argument("--no-transcribe", action="store_true", help="只抓数据不转写")
    ap.add_argument("--keep-video", action="store_true", help="保留 mp4")
    args = ap.parse_args()

    url = extract_url(args.link)
    print(f"🔗 链接: {url}")
    item_id, real = resolve_item_id(url)
    print(f"🆔 item_id: {item_id}")

    meta = parse_share_page(item_id)
    # 按博主归档：原始素材/<博主昵称>/<item_id>/
    safe_name = re.sub(r'[\\/:*?"<>|]', '_', meta["nickname"]).strip() or "未知博主"
    outdir = os.path.join(BASE, safe_name, item_id)
    os.makedirs(outdir, exist_ok=True)
    print(f"📌 《{meta['desc'][:40]}》 by {meta['nickname']}")
    print(f"📊 赞{meta['digg_count']} 藏{meta['collect_count']}({meta['收藏赞比']}) "
          f"转{meta['share_count']}({meta['分享赞比']}) 评{meta['comment_count']} "
          f"| {meta['时长秒']}s")
    age = meta.get('发布时长小时')
    if age is not None:
        mark = "✅数据已稳" if meta.get('数据成熟') else "🌱未稳·别下结论"
        print(f"⏱️  发布于 {meta['发布时间']}（{age}h前）｜ 赞/小时≈{meta['赞每小时']} ｜ {mark}")

    if not args.no_transcribe and meta["play_vid"]:
        mp4 = os.path.join(outdir, "video.mp4")
        print("⬇️  下载视频...")
        download_video(meta["play_vid"], mp4)
        txt = os.path.join(outdir, "transcript.txt")
        n = transcribe(mp4, txt, args.model)
        meta["transcript_chars"] = n
        print(f"✍️  逐字稿 {n} 字 → {txt}")
        if not args.keep_video:
            os.remove(mp4)
    elif not meta["play_vid"]:
        print("⚠️  没拿到视频地址，跳过转写（仅存数据）")

    with open(os.path.join(outdir, "meta.json"), "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"✅ 完成 → {outdir}")


if __name__ == "__main__":
    main()
