#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
闭环复盘取数 —— 拉迪迪自己某条视频的完整后台数据，按北极星判定 + 留存归因，生成复盘卡。
复用 ~/变美agent/douyin-analytics/scripts/fetch_douyin.py 的取数函数（不重复造轮子）。

用法：
  python3 loop_review.py --latest                      # 复盘最新一条公开视频
  python3 loop_review.py --item-id <item_id_plain>     # 复盘指定视频
  python3 loop_review.py --latest --cookie-file ~/.douyin_cookie
输出：
  复盘/<发布日期>-<标题>.md   （按模板填好）
  复盘/<发布日期>-<标题>.json （原始数据）
"""
import argparse, json, sys, time, re
from pathlib import Path
from datetime import datetime

# 复用 douyin-analytics 的取数函数
DA = Path.home() / "变美agent" / "douyin-analytics" / "scripts"
sys.path.insert(0, str(DA))
try:
    from fetch_douyin import (make_session, get_user_info, get_creator_item_ids,
                              get_metrics_batch, get_item_compare,
                              get_retention_curves, get_play_source)
except Exception as e:
    sys.exit(f"❌ 无法导入 fetch_douyin（检查路径 {DA}）：{e}")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "复盘"


def ff(x):
    try: return float(x) if x not in (None, "") else 0.0
    except: return 0.0


def src(ps, key):
    return next((p.get("value") for p in ps if p.get("key") == key), None)


def judge(m, ps):
    """按北极星出判定。返回 (指标dict, 总判定, 命中项数)"""
    view = ff(m.get("view_count"))
    like = ff(m.get("like_count"))
    fav = ff(m.get("favorite_count"))
    sub = ff(m.get("subscribe_count"))
    comp = ff(m.get("completion_rate"))
    bounce2 = ff(m.get("bounce_rate_2s"))
    fav_like = (fav / like) if like else 0          # 藏/赞（套路库口径）
    sub_per_k = (sub / view * 1000) if view else 0  # 涨粉/千播
    rec = src(ps, "homepage_hot")                    # 推荐流占比（缺失=算法没推）
    flw = src(ps, "follow")                          # 关注页占比
    throttled = (view == 0 and ff(m.get("avg_view_second")) > 0)  # 0播放但有留存=疑似限流

    hits = []
    # 北极星核心：涨粉/千播 > 1
    hits.append(("涨粉/千播", sub_per_k, sub_per_k > 1))
    # 完播率（工具号：>5%合格 >15%优秀）
    hits.append(("完播率", comp, comp > 0.05))
    # 收藏率（藏/赞，>0.5 算精准干货）
    hits.append(("收藏率(藏/赞)", fav_like, fav_like > 0.5))
    # 2s跳出（<0.4 正常）
    hits.append(("2s跳出率", bounce2, bounce2 < 0.4 if bounce2 else None))
    n_hit = sum(1 for _, _, ok in hits if ok)
    # 🚧 小样本护栏：播放太少时，涨粉/千播、收藏率这种比率全是噪声（1个粉÷239播=4.18是假信号）
    small = view < 500
    verdict = ("⚠️样本太小(播放<500)·比率不可信，别判" if small
               else ("命中" if n_hit >= 3 else ("平庸" if n_hit == 2 else "扑")))

    metrics = {
        "播放量": int(view), "点赞": int(like), "收藏": int(fav), "涨粉": int(sub),
        "收藏率(藏/赞)": round(fav_like, 3), "涨粉/千播": round(sub_per_k, 2),
        "完播率": round(comp, 4), "5s完播": round(ff(m.get("completion_rate_5s")), 4),
        "2s跳出率": round(bounce2, 4),
        "推荐流占比": round(rec, 3) if rec is not None else 0.0,
        "关注页占比": round(flw, 3) if flw is not None else None,
        "_throttled": throttled,
    }
    return metrics, verdict, n_hit


def retention_hint(curves):
    """从留存曲线给归因提示：开头掉=钩子；中段掉=结构。"""
    ret = curves.get("retention", {})
    cur = ret.get("current_item", [])
    sim = ret.get("similar_author", [])
    if not cur:
        return "（无留存数据）"
    # 取前5秒附近的留存值
    def at(lst, sec):
        for p in lst:
            k = p.get("key", "")
            if k.endswith(f":{sec:02d}") or k == f"00:{sec:02d}":
                return ff(p.get("value"))
        return None
    c5, s5 = at(cur, 5), at(sim, 5)
    hint = []
    if c5 is not None:
        line = f"5s留存={c5:.0%}"
        if s5 is not None:
            line += f"（同类{s5:.0%}，{'低于大盘→钩子偏弱' if c5 < s5 else '不输大盘→钩子OK'}）"
        hint.append(line)
    valley = ret.get("valley_list", {})
    if valley:
        hint.append(f"低谷时段：{valley}")
    return " ｜ ".join(hint) if hint else "（留存曲线已取，需人工看图）"


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--latest", action="store_true", help="复盘最新一条公开视频")
    g.add_argument("--item-id", help="指定 item_id_plain")
    ap.add_argument("--cookie-file", default="~/.douyin_cookie")
    args = ap.parse_args()

    cookie = Path(args.cookie_file).expanduser().read_text().strip()
    s = make_session(cookie)

    user = get_user_info(s)
    if not user.get("nick_name"):
        sys.exit("❌ Cookie 可能已失效（拿不到用户信息）。请刷新 ~/.douyin_cookie 后重试。")
    print(f"账号：{user['nick_name']} ｜ 粉丝：{user['follower_count']}", file=sys.stderr)

    if args.latest:
        ids = get_creator_item_ids(s)
        if not ids:
            sys.exit("❌ 没拉到视频列表")

        def ct_key(v):
            ct = str(v.get("create_time") or "")
            mt = re.search(r'(\d{4})\D+(\d{1,2})\D+(\d{1,2})\D+(\d{1,2}):(\d{2})', ct)
            if mt:
                return datetime(*map(int, mt.groups())).timestamp()
            try: return float(ct)
            except: return 0.0

        ids.sort(key=ct_key, reverse=True)
        item_id = ids[0]["item_id"]
        title0 = ids[0].get("title", "")
    else:
        item_id, title0 = args.item_id, ""

    print(f"复盘视频：{item_id} {title0[:20]}", file=sys.stderr)
    mm = get_metrics_batch(s, [item_id])
    m = mm.get(item_id, {})
    create_ts = int(m.get("_create_time") or 0)
    title = (m.get("_description") or title0 or item_id)[:40]
    compare = get_item_compare(s, item_id); time.sleep(0.3)
    curves = get_retention_curves(s, item_id); time.sleep(0.3)
    psource = get_play_source(s, item_id)

    metrics, verdict, n_hit = judge(m, psource)
    pub = datetime.fromtimestamp(create_ts).strftime("%Y-%m-%d %H:%M") if create_ts else "?"
    hours = round((time.time() - create_ts) / 3600, 1) if create_ts else "?"

    OUT.mkdir(exist_ok=True)
    safe = "".join(c for c in title if c not in '\\/:*?"<>|').strip()[:30]
    date = datetime.fromtimestamp(create_ts).strftime("%Y%m%d") if create_ts else "x"
    base = OUT / f"{date}-{safe}"

    raw = {"user": user, "item_id": item_id, "title": title, "publish": pub,
           "fetch_time": datetime.now().isoformat(), "metrics": metrics,
           "compare": compare, "play_source": psource, "retention_curves": curves}
    base.with_suffix(".json").write_text(json.dumps(raw, ensure_ascii=False, indent=2))

    md = f"""# 复盘卡 · {title}

> item_id：{item_id} ｜ 发布：{pub} ｜ 取数：{datetime.now():%Y-%m-%d %H:%M}（发布后约 {hours}h）

## ① 实际数据（看北极星，不看播放）

| 指标 | 实际 |
|---|---|
| 收藏率(藏/赞) | {metrics['收藏率(藏/赞)']} |
| 完播率 | {metrics['完播率']:.1%} ｜ 5s完播 {metrics['5s完播']:.1%} |
| 涨粉/千播 | {metrics['涨粉/千播']} |
| 2s跳出率 | {metrics['2s跳出率']:.1%} |
| 推荐流占比 | {metrics['推荐流占比']} |
| 关注页占比 | {metrics['关注页占比']} |
| 播放/赞/藏/涨粉 | {metrics['播放量']} / {metrics['点赞']} / {metrics['收藏']} / {metrics['涨粉']} |

**总判定：{verdict}**（北极星命中 {n_hit}/4）
{'> 🚨 **疑似限流/仅自己可见**：0 播放但有零星留存数据，且无推荐流。先查标签/红线/可见性，别急着归因内容。' if metrics.get('_throttled') else ''}

## ② 归因（选题 vs 执行）
- 留存：{retention_hint(curves)}
- 2s跳出 {metrics['2s跳出率']:.1%} → {'钩子偏弱' if metrics['2s跳出率']>0.4 else '钩子OK'}
- 推荐流占比 {metrics['推荐流占比']} → {'算法几乎没推（限流/降权/标签问题，优先排查）' if (metrics['推荐流占比'] or 0)<0.6 else '算法正常推'}
- 初步：▢限流(先排查) ▢选题不行 ▢执行不行 ▢没爆苗 ▢都行

## ③ 这条用了哪些套路（人工回填）
- 选题类型： ｜ 钩子： ｜ 评分卡当初打了 ?分 ｜ 预测卡 vs 实际 diff：

## ④ 更新动作（待 👤 确认）
- [ ] 套路库加权/降权：
- [ ] 预测器校准：
- [ ] 评分卡维度调整：

> ⚠️ 单条不下结论，同类攒 2-3 条再改库。
"""
    base.with_suffix(".md").write_text(md)
    print(f"\n✅ 复盘卡 → {base.with_suffix('.md')}", file=sys.stderr)
    print(f"   判定：{verdict}（{n_hit}/4）｜ 收藏率{metrics['收藏率(藏/赞)']} 完播{metrics['完播率']:.1%} 涨粉/千播{metrics['涨粉/千播']}", file=sys.stderr)


if __name__ == "__main__":
    main()
