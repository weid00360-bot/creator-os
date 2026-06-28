#!/usr/bin/env node
// 批量渲染打字机 PPT 视频。用法: node scripts/render_slides.mjs <项目目录> [输出目录]
// 读 <项目目录>/slides.json，逐段渲染 16:9 mp4。时长由 Typewriter 的 calculateMetadata 按字数算。
import { execFileSync } from 'node:child_process';
import { readFileSync, mkdirSync } from 'node:fs';
import { resolve, join } from 'node:path';

const proj = resolve(process.argv[2] || 'projects/专家更值钱');
const outDir = resolve(process.argv[3] || join(process.env.HOME, 'Desktop/迪迪视频预览/AI让懂行的人更值钱/打字机视频'));
mkdirSync(outDir, { recursive: true });

const slides = JSON.parse(readFileSync(join(proj, 'slides.json'), 'utf8'));
console.log(`🎬 渲染 ${slides.length} 段打字机 PPT → ${outDir}\n`);

for (const s of slides) {
  const out = join(outDir, `PPT视频_${s.id}.mp4`);
  console.log(`▶ ${s.id} (cps=${s.cps ?? 5}) …`);
  execFileSync('npx', [
    'remotion', 'render', 'Typewriter', out,
    `--props=${JSON.stringify(s)}`,
    `--public-dir=${proj}`,
  ], { stdio: 'inherit', cwd: resolve('remotion') });
  console.log(`  ✅ ${out}\n`);
}
console.log('全部完成。');
