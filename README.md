# Creator OS

**AI-powered content production system for 抖音 / 小红书 / TikTok**

> From topic selection to published video — nearly zero manual work.  
> Not just automation. Your taste, your standards, your judgment — systematized and compounding.

Works with **Claude Code · Codex · any Claude-compatible agent environment**

---

## 痛点 · The Problem

做内容的人都经历过这些 / Every creator knows these pains:

- 想做但不知道做什么——翻了半天热榜，选了个感觉会爆的，发出去扑了
- 写文案靠感觉，同样的结构下次用又忘了为什么管用
- 发完不知道哪里出了问题，是选题还是钩子还是剪辑节奏
- 积累的东西都在脑子里，带不走、教不了、越做越累

**Topic paralysis. Inconsistent copy. No post-mortem. Knowledge stuck in your head.**

---

## 它解决什么 · What This Solves

| 问题 | 解法 |
|---|---|
| 选题靠直觉 | 五维评分卡 + 数据驱动打分，AI 帮你筛 |
| 文案靠感觉 | 套路库固化爆款结构，对标网红口吻模版化输出 |
| 发完不知咋回事 | 北极星指标自动判定，留存归因精确到帧 |
| 经验在脑子里 | 每条视频强制复盘 → 更新套路库 → 变成你的永久资产 |
| 视频生产靠手感 | 口播稿 → 转写 → 逐帧编排 → 渲染，全程模版化 |

**The goal: minimize garbage work. Maximize judgment preservation.**

---

## 五个核心交付件 · Five Skills

> 每个 Skill 是一个 Claude Code 指令，直接触发完整工作流。  
> Each Skill is a single command that runs a complete workflow.

### `/选题` — Topic Engine
- 拉今日 AI 热点 + 平台热榜
- 读套路库历史规律
- 五维评分卡打分：北极星匹配 / 收藏属性 / 独家性 / 钩子强度 / 时效热点
- 输出排序好的选题清单，每条带评分依据

*Pulls trending topics + your knowledge base → ranked topic list with scoring rationale.*

---

### `/文案` — Copy Engine
- 按套路库结构起草口播稿
- 对标你设定的网红口吻风格（口头禅 / 节奏 / 句式全模版化）
- 配套发布包：标题备选 / 话题标签 / 封面建议 / 发布前预测卡

*Drafts scripts in your benchmarked creator's tone. Every copy element templated.*

---

### `/预审` — Pre-publish Audit
- 对照平台官方红线：限流词 / 违规内容 / 标签禁区
- 输出红黄绿三级清单，标注具体修改建议
- 发前拦截，不发事后补救

*Scans against official platform guidelines. Red/yellow/green audit before you hit publish.*

---

### `/复盘` — Post-mortem Engine
- 自动取后台数据（无需手动查）
- 北极星指标判定：命中 / 平庸 / 扑
- 留存曲线归因：开头掉 = 钩子问题，中段掉 = 结构问题
- 输出复盘卡 + 套路库更新建议（人工确认后才写入）

*Auto-pulls analytics. Diagnoses exactly where viewers dropped off. Feeds learnings back into the system.*

---

### `/视频生产` — Video Production Pipeline
- 口播录完 → Whisper 转写 → 词级时间戳
- 逐帧编排方案（字幕卡点 / 高亮 / B-roll 全模版化）
- Remotion 渲染成片
- 每条片做完出复盘 + 模版库新增沉淀

*Recording → transcript → frame-level edit plan → render. Full pipeline, all templated.*

---

## 套路库 · The Knowledge Base

[`爆款知识库/套路库.md`](爆款知识库/套路库.md)

**持续更新同赛道爆款，每条拆成 6 个维度：**  
*Updated daily with viral content from your niche, dissected across 6 dimensions:*

选题公式 · 开头钩子 · 中段结构 · 收尾金句 · CTA · 数据表现

拆完不只是存档——**输出核心洞察，反哺动作**。比如：  
*Every breakdown produces actionable insights, not just archives. Example:*

> **核心洞察**：收藏率 = 赛道匹配器。藏/赞 > 0.7 才是精准变现受众；点赞高收藏低 = 泛流量陷阱。  
> **反哺动作**：选题评分卡"收藏属性"维度权重上调；文案 Skill 优先套高收藏结构。

[`爆款知识库/拆解卡片/`](爆款知识库/拆解卡片/) — 27 张拆解原始卡，知识库的原材料。

---

## 账号北极星 · Your North Star

[`账号北极星.md`](账号北极星.md) — 整套系统的总策略文件。

**这份文件是 agent 的宪法**。所有 Skill 的判断标准都从这里来：

- 你的账号定位和目标受众
- **核心指标**：根据你的变现路径自定义，写进总文件，agent 的所有判断都对齐它
- 禁区红线：什么内容永远不做
- 平台分工：哪个平台做什么事、如何一鱼多吃

*This is the constitution. Every agent decision traces back to it. Define your own north star metrics — the system aligns to whatever you put here.*

---

## 脚本层 · Scripts

```
scripts/
├── loop_review.py    # 复盘取数：自动拉后台北极星指标，生成复盘卡
├── douyin_hot.py     # 热榜 AI 过滤：只留与你赛道相关的热词
├── monitor.py        # 对标监控：追踪竞品博主新视频数据
└── douyin_ripper.py  # 单条视频数据 + 逐字稿抓取（用于拆解爆款）
```

取数依赖平台创作者后台 API（需配置 cookie），其余无外部依赖。  
*Requires creator backend cookie for analytics pull. No other external dependencies.*

---

## 设计理念 · Design Philosophy

### 沉淀标准，不只是存记录

很多人用 AI 做内容，做完就完了，经验还在脑子里。  
这套系统的核心设计是：**每次出手都要留痕，留痕要能反哺下一次**。

套路库有更新标准（什么样的数据才能改权重）；  
复盘有归因标准（限流先排查，别急着否定内容）；  
视频生产有模版标准（做完一条就沉淀一个模版）。

*Most creators finish a video and move on. This system is designed so every piece of work compounds — standards for when to update the playbook, when to change weights, when a template is worth keeping.*

### Coach 知道你的每一个动作

Agent 不只是执行工具，它是你的 coach。  
它知道你上条视频的钩子数据，知道你这个月哪类选题命中率最高，知道你的套路库哪条规则还没被验证过。  
**它的判断建立在你的真实数据上，不是通用建议。**

*The agent isn't just an executor — it's a coach with memory. It knows your last video's drop-off point, your best-performing hook type this month, which rules in your playbook are still unverified. Its advice is based on your data, not generic best practices.*

### 模版化一切，尤其是视频生产

从口播结构到逐帧字幕布局，从 B-roll 切点到片尾 CTA——  
每一个可以复用的决策都进模版库，下一条视频从模版出发，不从零开始。

*Everything that can be templated, is. Especially video production — from caption timing to B-roll cuts to end-card CTA. Every video adds to the template library.*

---

## 快速上手 · Quick Start

```bash
# 1. Clone
git clone https://github.com/weid00360-bot/creator-os.git
cd creator-os

# 2. 把 skills/ 目录下的 Skill 装进你的 Claude Code 环境
#    Install skills into your Claude Code environment

# 3. 复制 账号北极星.md，填入你自己的定位和核心指标
#    Copy 账号北极星.md and fill in your own positioning + metrics

# 4. 跑第一次选题
/选题

# 5. 写文案
/文案 [你的选题]

# 6. 发布后复盘（需配置平台 cookie）
python3 scripts/loop_review.py --latest
```

详细配置见 [`工作流SOP.md`](工作流SOP.md)。

---

## 目录结构 · Structure

```
creator-os/
├── skills/               ← 五个 Claude Code Skill（选题/文案/预审/复盘/视频生产）
├── scripts/              ← Python 自动化脚本（取数/热榜/对标监控）
├── 爆款知识库/
│   ├── 套路库.md         ← ★ 核心知识库（持续更新）
│   └── 拆解卡片/         ← 27 张爆款拆解原始卡
├── 参考/                 ← 平台官方规则文档（算法/审核红线/优质内容指南）
├── 文案/                 ← 已发布的口播定稿存档
├── 视频生产/             ← Remotion 剪辑管线 + 模版库
├── 账号北极星.md         ← 账号定位 & 北极星指标（系统宪法）
├── 工作流SOP.md          ← 完整运营 SOP
└── CLAUDE.md             ← Claude Code agent 行为规范
```

---

## License

MIT · Build in Public · VibeCoding 大赏参赛作品
