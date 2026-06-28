#!/usr/bin/env node
// 一键新建一个口播项目。
// 用法: node scripts/new_project.mjs <项目名> <口播视频路径>
//   例: node scripts/new_project.mjs 002 ~/Desktop/xxx.mov
//
// 做的事：建目录 + 把视频硬链(同卷不占空间，跨卷自动复制)成 input.mov + 放一张投稿单。
import { mkdirSync, linkSync, copyFileSync, writeFileSync, existsSync } from 'node:fs';
import { resolve, join } from 'node:path';

const [name, video] = process.argv.slice(2);
if (!name || !video) {
  console.error('用法: node scripts/new_project.mjs <项目名> <口播视频路径>');
  process.exit(1);
}
const proj = resolve('projects', name);
if (existsSync(proj)) { console.error(`❌ 项目已存在: ${proj}`); process.exit(1); }
const src = resolve(video.replace(/^~/, process.env.HOME));
if (!existsSync(src)) { console.error(`❌ 找不到视频: ${src}`); process.exit(1); }

mkdirSync(join(proj, 'broll'), { recursive: true });
const dst = join(proj, 'input.mov');
try { linkSync(src, dst); }                       // 同卷硬链，0 额外空间
catch { copyFileSync(src, dst); }                  // 跨卷退化为复制

const form = `# 投稿单 · ${name}

> 填好下面这些（除①外都可选），我就能接手。括号里是默认值。

## ① 口播视频  ✅ 已就位
input.mov（竖屏 1080×1920 / 30fps）

## ② 选题一句话（可选，用于开头标题/文案/标签）

## ③ 想强调的重点（可选）
- 哪些词/金句要高亮弹一下：
- 哪几个画面想全屏插图（B-roll）：

## ④ 风格（默认：沿用上次定稿模板）

---
我会：转写 → 生成字幕时间线 → 给你「补图清单」→ 你补图 → Studio 定稿 → 你说导出再渲染。
`;
writeFileSync(join(proj, '投稿单.md'), form);

console.log(`✅ 新项目就绪: ${proj}`);
console.log(`   下一步（把项目名喂给 Claude，或自己跑）:`);
console.log(`   python3 scripts/transcribe.py ${join('projects', name, 'input.mov')} projects/${name} --model small`);
