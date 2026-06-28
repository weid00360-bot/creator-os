#!/usr/bin/env node
// 一条命令：项目目录 → out.mp4
// 用法: node scripts/render.mjs projects/练手01
//
// 约定：项目目录里有 timeline.json，其中 source 指向同目录下的口播视频(如 input.mov)，
//       broll 资源放在同目录 broll/ 下。--public-dir 指向项目目录，staticFile 即可解析。
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { resolve, join } from 'node:path';

const projDir = process.argv[2];
if (!projDir) {
  console.error('用法: node scripts/render.mjs <项目目录>  例: node scripts/render.mjs projects/练手01');
  process.exit(1);
}
const abs = resolve(projDir);
const timelinePath = join(abs, 'timeline.json');
if (!existsSync(timelinePath)) {
  console.error(`❌ 找不到 ${timelinePath}（先生成 timeline.json）`);
  process.exit(1);
}

const timeline = JSON.parse(readFileSync(timelinePath, 'utf8'));
const fps = timeline.fps ?? 30;

// 补全 durationInFrames：口播全程保留，时长 = 视频时长
if (!timeline.durationInFrames && timeline.source) {
  const src = join(abs, timeline.source);
  if (existsSync(src)) {
    const dur = parseFloat(execFileSync('ffprobe', [
      '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src,
    ]).toString().trim());
    timeline.durationInFrames = Math.round(dur * fps);
    writeFileSync(timelinePath, JSON.stringify(timeline, null, 2));
    console.log(`ℹ️  自动写入 durationInFrames=${timeline.durationInFrames}（${dur.toFixed(1)}s × ${fps}fps）`);
  }
}

const out = join(abs, 'out.mp4');
console.log(`🎬 渲染 → ${out}`);
execFileSync('npx', [
  'remotion', 'render', 'TalkingHead', out,
  `--props=${timelinePath}`,
  `--public-dir=${abs}`,
  '--log=info',
], { stdio: 'inherit', cwd: resolve('remotion') });
console.log(`✅ 成片: ${out}`);
