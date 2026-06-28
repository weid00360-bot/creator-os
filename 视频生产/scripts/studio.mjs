#!/usr/bin/env node
// 起 Remotion Studio 做网页端定稿预览。
// 用法: node scripts/studio.mjs [项目目录]   默认 projects/练手01
//
// 自动做两件事，换项目零改代码：
//   1. 把目标项目的 timeline.json 复制成 remotion/src/_active.json（Root 加载它）
//   2. --public-dir 指向项目目录，让 staticFile('input.mov') / broll/* 能解析
import { execFileSync } from 'node:child_process';
import { copyFileSync, existsSync } from 'node:fs';
import { resolve, join } from 'node:path';

const proj = resolve(process.argv[2] || 'projects/练手01');
const timeline = join(proj, 'timeline.json');
if (!existsSync(timeline)) {
  console.error(`❌ 找不到 ${timeline}（先跑 build_timeline.py 生成）`);
  process.exit(1);
}
copyFileSync(timeline, resolve('remotion/src/_active.json'));
console.log(`🎬 Studio 预览项目: ${proj}`);
console.log(`   改 timeline 后刷新页面即热更；改完满意再 render.mjs 导出。`);
execFileSync('npx', ['remotion', 'studio', `--public-dir=${proj}`], {
  stdio: 'inherit',
  cwd: resolve('remotion'),
});
