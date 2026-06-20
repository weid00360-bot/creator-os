# 迪迪剪辑 Agent · 视频生产工作台

## 工作流（必须按顺序）

### 录前·规划阶段
1. 迪迪给文案 → Claude 出逐段编排方案（展示方式+风格+素材分工）
2. 迪迪确认方案 → Claude 做1-2张 PPT 示意图
3. 迪迪确认风格 → 开始录视频

### 录后·制作阶段
4. 迪迪给口播视频 → 跑 `transcribe.py` → `words.json`
5. 跑 `build_timeline.py` → `timeline.json`（字幕+broll点位）
6. 跑 `studio.mjs` → 启动 Remotion Studio 网页端预览
7. **网页端定稿 → 再导出（不提前渲染！）**
8. 做完复盘 → 沉淀模板库

### 人工卡点（AI不替代）
- 选题拍板：迪迪决定
- 文案修改：迪迪改成自己口吻 + 过红线

## 视觉风格（已定死，不改）

### 配色
| 色名 | Hex |
|------|-----|
| 奶油白 | `#F3EFE7` |
| 宝蓝 | `#1F4ED8` |
| 红 | `#D63737` |
| 墨黑 | `#1C1E24` |
| 灰 | `#787880` |

### 字体（PIL）
- 中文粗体：`Hiragino Sans GB.ttc index=1`（Bold）
- 中文常规：`Hiragino Sans GB.ttc index=0`
- 数字/标签：`Menlo`

### 幻灯片风格
- **SL-01**（主用）：奶油底 + 宝蓝/红撞色 + 超大粗黑 + 大留白 + 手绘红圈/下划线
- **SL-02**（SL-01变体）：加手绘小人，轻松段/情绪点少量掺
- **SL-04**（SL-01变体）：宝蓝表头 + 色编码单元格 + 铁律条
- ❌ 暗黑玻璃科技风：已弃用（太黑，和暗场背景融合）

### 关键反差原则
亮底幻灯片（SL系列）压在暗场HUD背景上 = 故意制造视觉反差 = 突出效果

### 画面构型（横版目标）
SC-01：暗场HUD背景 + 扣像人物（右侧）+ 屏幕框录屏 + 字幕

## 技术参数
- 字幕分组：`GAP_BREAK=0.30s / MAX_DUR=2.2s / MAX_WORDS=5`
- 字幕位置：`CAP_BOTTOM=420px`（画面下1/3）
- 高亮规则：`HL_RULES`（regex）→ 关键词绿/黄/红/蓝
- 练手01：1080×1920 / 30fps / 217.2s / durationInFrames=6516
- 目标成品：横版 1920×1080

## 目录结构
```
视频生产/
├── scripts/
│   ├── transcribe.py    ← openai-whisper → words.json
│   ├── build_timeline.py ← jieba分词 → timeline.json
│   ├── render.mjs       ← 渲染导出
│   └── studio.mjs       ← 启动预览（copy timeline→_active.json）
├── remotion/src/
│   ├── TalkingHead.jsx  ← 主合成（OffthreadVideo+BrollLayer+Captions）
│   ├── Root.jsx         ← 读 _active.json
│   └── components/
│       ├── Captions.jsx ← 字幕（spring动效+霓虹高亮+emoji标签）
│       └── BrollCut.jsx ← broll插播（null→"待补图"占位）
├── projects/
│   ├── 练手01/          ← 竖版，仅流程测试
│   └── agent五要素/     ← 当前项目（进行中）
└── 模板库/
    ├── README.md
    ├── 编排方案模板.md
    ├── 幻灯片风格.md
    ├── 画面与动效.md
    └── 博主拆解.md
```

## 素材输出规则（每条视频独立子文件夹）
- 根目录：`~/Desktop/迪迪视频预览/`
- **每条视频建一个子文件夹，文件夹名 = 视频标题**，该片所有预览图都进去
- 跨视频通用的风格样张放 `_通用样张/`
- 现有：`agent五要素/`（15张）· `AI让懂行的人更值钱/`（7张）· `_通用样张/`

## 当前项目：agent五要素（进行中）
素材目录：`~/Desktop/迪迪视频预览/agent五要素/`

已完成（~/Desktop/迪迪视频预览/）：
- ✅ 表格图_选题评分卡.png
- ✅ 表格图_收藏率赛道匹配器.png
- ✅ 迪迪幻灯片_活泼版.png（SL-02，收藏率对撞）
- ✅ AI对话_展示示意.png
- ✅ 五要素闭环图_hero.png（总览·全程常驻）
- ✅ 北极星指标表.png
- ✅ 6维度↔6问题表.png
- ✅ 主链路11步流程图.png（人工卡点琥珀色）
- ✅ 剪辑agent子流程.png（录前/录中/录后三阶段）
- ✅ 闭环迭代图.png
- ✅ 金句卡.png
- ✅ 结尾CTA卡.png

待做（Claude负责）：
- ❌ 钱从哪来逻辑链（①目标段·等迪迪给AI对话截图后配合做）

待迪迪提供：
- 📱 AI对话截图×2
- 🎥 录屏×2（钩子拼贴 / 最终结果）
- 📊 掉粉/完播数据截图

## 已踩坑（避免重复）
1. Remotion资源必须用**硬链接**（`ln`），symlink会报404
2. `remotion still` 不跑 calculateMetadata → 用 `remotion render --frames=a-b`
3. PIL中文字体：PingFang.ttc不行 → 用 `Hiragino Sans GB.ttc`（idx1=粗）
4. PIL渲染图用户看不到内联图 → 全部存 `~/Desktop/迪迪视频预览/` 给路径
5. 预览文件统一放 `~/Desktop/迪迪视频预览/` 子文件夹，别散落桌面
6. jieba分词英文sub-token乱切（skill→sk|ill）→ 先跑ASCII_FIX再做char stream
7. 手绘大红X难看 → 改用发光标注框+tag chip+细连接线
8. 暗黑玻璃PPT和暗场背景融合 → 改用亮底SL-01
9. whisper同音字错误（适→试）→ `apply_context_fix()` 修

## 复盘仪式（每条视频做完必做）
1. 记录本条出现的错误/新发现
2. 提炼可复用元素 → 沉淀到 `模板库/`
3. 向迪迪汇报：沉淀了哪些 / 模板库新增什么

素材沉淀标准：好风格 → 分享→拆→做样张验证→通过才沉淀；不好列入❌弃用并注明原因
