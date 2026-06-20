#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对标账号半自动监控 —— 你定期把对标的新视频链接丢进来，自动去重 + 抓数据 + 筛爆款 + 排"待拆解"清单。
（抖音反爬挡死了"列博主视频列表"，所以列表这步靠你贴链接；其余全自动。）

用法：
  python3 monitor.py --links-file /tmp/new.txt           # 一批链接（每行一个/含分享口令都行）
  python3 monitor.py "<链接1>" "<链接2>" ...              # 直接传
  python3 monitor.py --links-file x.txt --min-likes 8000 # 自定义爆款阈值
  python3 monitor.py --links-file x.txt --transcribe      # 爆款顺便转写（可能撞whisper numpy报错）
输出：
  原始素材/<博主>/<item>/meta.json  （数据）
  对标监控/待拆解-<日期>.md          （新爆款清单，喂给后续拆解）
  对标监控/ledger.json               （已处理台账，自动去重）
"""
import sys, json, argparse, subprocess, re
from pathlib import Path
from datetime import datetime

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
MON = ROOT / "爆款知识库" / "对标监控"
SRC = ROOT / "爆款知识库" / "原始素材"
LEDGER = MON / "ledger.json"
RIPPER = SCRIPTS / "douyin_ripper.py"

sys.path.insert(0, str(SCRIPTS))
import douyin_ripper as dr   # 复用 extract_url / resolve_item_id


def load_ledger():
    try: return set(json.loads(LEDGER.read_text()))
    except: return set()


def find_meta(item_id):
    hits = list(SRC.glob(f"*/{item_id}/meta.json"))
    return json.loads(hits[0].read_text()) if hits else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("links", nargs="*", help="链接（可多个）")
    ap.add_argument("--links-file", help="每行一个链接的文件")
    ap.add_argument("--min-likes", type=int, default=10000, help="爆款点赞阈值（默认1万）")
    ap.add_argument("--transcribe", action="store_true", help="爆款顺便转写")
    args = ap.parse_args()

    raw = list(args.links)
    if args.links_file:
        raw += [l for l in Path(args.links_file).read_text().splitlines() if l.strip()]
    if not raw:
        sys.exit("❌ 没给链接（--links-file 或直接传）")

    ledger = load_ledger()
    new_burst, new_normal, new_fresh, skipped = [], [], [], 0

    for line in raw:
        try:
            url = dr.extract_url(line)
            item_id, _ = dr.resolve_item_id(url)
        except SystemExit:
            print(f"  ✗ 跳过无效链接：{line[:40]}", file=sys.stderr); continue
        if item_id in ledger:
            skipped += 1; continue

        # 抓数据（复用 ripper，先不转写=快）
        subprocess.run(["python3", str(RIPPER), url, "--no-transcribe"],
                       capture_output=True)
        meta = find_meta(item_id)
        if not meta:
            print(f"  ✗ 抓取失败：{item_id}", file=sys.stderr); continue

        nick, desc, digg = meta["nickname"], meta["desc"][:30], meta["digg_count"]
        age = meta.get("发布时长小时")
        # ⏱️ 时间线感知：发布<48h 数据未稳，不判爆/扑，进"待复看"，且不入台账(下次自动复看)
        if meta.get("数据成熟") is False:
            print(f"  🌱待复看 赞{digg}（{age}h·{meta.get('赞每小时')}/h，数据未稳） | {nick}《{desc}》",
                  file=sys.stderr)
            new_fresh.append(meta)
            continue
        is_burst = digg >= args.min_likes
        tag = "🔥爆款" if is_burst else "  普通"
        print(f"  {tag} 赞{digg:>7} 藏{meta['收藏赞比']}（{age}h） | {nick} 《{desc}》", file=sys.stderr)
        (new_burst if is_burst else new_normal).append(meta)
        ledger.add(item_id)

        if is_burst and args.transcribe:
            subprocess.run(["python3", str(RIPPER), url, "--model", "small"],
                           capture_output=True)

    LEDGER.write_text(json.dumps(sorted(ledger), indent=0, ensure_ascii=False))

    # 待拆解清单
    if new_burst:
        date = datetime.now().strftime("%Y%m%d")
        lines = [f"# 待拆解 · {date}（对标监控新增爆款 {len(new_burst)} 条）\n"]
        for m in sorted(new_burst, key=lambda x: -x["digg_count"]):
            lines.append(
                f"- [ ] **{m['nickname']}**《{m['desc'][:40]}》"
                f"赞{m['digg_count']} 藏{m['收藏赞比']} 转{m['分享赞比']} | "
                f"`{m['item_id']}` {m['share_url']}")
        lines.append("\n> 拆解：对每条跑转写→按6维度做拆解卡入库；高收藏(藏/赞>0.7)优先。")
        out = MON / f"待拆解-{date}.md"
        out.write_text("\n".join(lines))
        print(f"\n✅ 待拆解清单 → {out}", file=sys.stderr)

    # 待复看清单（发布<48h，数据未稳，未入台账，24-72h后再跑一次自动复看）
    if new_fresh:
        date = datetime.now().strftime("%Y%m%d")
        fl = [f"# 待复看 · {date}（新发<48h，数据未稳，{len(new_fresh)}条）\n",
              "> 这些没入台账，24-72h 后重跑 monitor 会自动再评一次。别现在就判爆/扑。\n"]
        for m in sorted(new_fresh, key=lambda x: -(x.get("赞每小时") or 0)):
            fl.append(f"- {m['nickname']}《{m['desc'][:40]}》赞{m['digg_count']}（{m.get('发布时长小时')}h·{m.get('赞每小时')}/h）| `{m['item_id']}`")
        (MON / f"待复看-{date}.md").write_text("\n".join(fl))
        print(f"🌱 待复看清单 → {MON}/待复看-{date}.md", file=sys.stderr)

    print(f"\n本次：爆款 {len(new_burst)} | 普通 {len(new_normal)} | 🌱待复看 {len(new_fresh)} | 已抓跳过 {skipped}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
