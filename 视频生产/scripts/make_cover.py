#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一键出封面（定稿风格 Swiss IKB · 套迪迪照片）。
用法：
  python3 视频生产/scripts/make_cover.py --title "能写出人味的/文案 agent" --hl "agent" --out ~/Desktop/封面.png
  ("/" = 换行；--hl 高亮末词用宝蓝；--accent 可选 ikb|lemon-yellow|lemon-green|safety-orange；--photo 换照片)
封面规格见记忆/模板：照片在上+轻量大字在下，必带真人脸。
"""
import argparse, os, re, shutil, subprocess, tempfile, sys
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TPL  = os.path.join(REPO, "视频生产/模板库/封面_SwissIKB模板.html")
PHOTO_DEFAULT = os.path.join(REPO, "视频生产/模板库/封面照_迪迪.jpg")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def build(title, hl, accent, photo, out, ep, tags):
    html = open(TPL, encoding="utf-8").read()
    if accent and accent != "ikb":
        html = re.sub(r'(<html[^>]*data-accent=")[^"]*(")', r'\1'+accent+r'\2', html, count=1)
    # 标题：/ -> 换行；hl 词 -> 宝蓝
    t = title.replace("/", "<br>")
    if hl and hl in title:
        t = t.replace(hl, f'<span style="color:var(--accent)">{hl}</span>')
    html = re.sub(r'(<h1 class="h-statement">).*?(</h1>)', lambda m: m.group(1)+t+m.group(2), html, count=1, flags=re.S)
    if ep:
        html = re.sub(r'(<span class="t-cat">)[^<]*(</span>)', lambda m: m.group(1)+ep+m.group(2), html, count=1)
    if tags:
        items = [x.strip() for x in re.split(r'[／/，,]', tags) if x.strip()]
        row = "".join('<p class="t-meta">%s%s</p>' % (("/ " if i else ""), x) for i, x in enumerate(items))
        html = re.sub(r'(<div class="row gap-8">).*?(</div>)', lambda m: m.group(1)+row+m.group(2), html, count=1, flags=re.S)
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "assets"), exist_ok=True)
        shutil.copy(photo, os.path.join(td, "assets/face.jpg"))
        open(os.path.join(td, "index.html"), "w", encoding="utf-8").write(html)
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=2", "--virtual-time-budget=5000",
            "--window-size=1080,1440", f"--screenshot={out}",
            f"file://{td}/index.html"], check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("封面已出 ->", out, "(2160x2880, 3:4)")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True, help='主标题，"/"换行')
    ap.add_argument("--hl", default="", help="高亮末词(宝蓝)")
    ap.add_argument("--accent", default="ikb")
    ap.add_argument("--photo", default=PHOTO_DEFAULT)
    ap.add_argument("--ep", default="", help="顶部期标，如 闭环 · EP03")
    ap.add_argument("--tags", default="", help="底部三标签，/ 分隔")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if not os.path.exists(TPL): sys.exit("缺模板: "+TPL)
    build(a.title, a.hl, a.accent, a.photo, a.out, a.ep, a.tags)
