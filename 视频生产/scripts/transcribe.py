#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
口播 → 词级时间戳
用法:
    python3 transcribe.py <input.mov|wav|mp3> <项目目录> [--model small|medium]

输出到 <项目目录>/:
    transcript.txt   全文逐字稿（人工瞄一眼准不准）
    words.json       词级时间戳 [{ "w": "AI博主", "start": 0.27, "end": 0.61 }, ...]
    segments.json    句级原始结果（备查）

说明: 用 openai-whisper 的 word_timestamps。中文按 token 切分，颗粒度偏粗，
      够阶段一验证管线；要更准可后续换 WhisperX 对齐。
"""
import sys, os, json, argparse, subprocess, tempfile

def extract_audio(src, dst):
    subprocess.run(
        ["ffmpeg", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000", "-f", "wav", dst],
        check=True, capture_output=True,
    )

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("outdir")
    ap.add_argument("--model", default="small")
    ap.add_argument("--lang", default="zh")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    print(f"[1/3] 抽音频 …")
    wav = os.path.join(args.outdir, "audio.wav")
    extract_audio(args.input, wav)

    print(f"[2/3] 加载 whisper（{args.model}）…")
    import whisper
    model = whisper.load_model(args.model)

    print(f"[3/3] 转写 + 词级对齐（耐心等，CPU 较慢）…")
    result = model.transcribe(
        wav, language=args.lang, word_timestamps=True, verbose=False,
    )

    # 全文
    text = result.get("text", "").strip()
    with open(os.path.join(args.outdir, "transcript.txt"), "w", encoding="utf-8") as f:
        f.write(text)

    # 句级
    with open(os.path.join(args.outdir, "segments.json"), "w", encoding="utf-8") as f:
        json.dump(result.get("segments", []), f, ensure_ascii=False, indent=2)

    # 词级（拍平）
    words = []
    for seg in result.get("segments", []):
        for w in seg.get("words", []):
            tok = (w.get("word") or "").strip()
            if not tok:
                continue
            words.append({"w": tok, "start": round(w["start"], 3), "end": round(w["end"], 3)})
    with open(os.path.join(args.outdir, "words.json"), "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

    dur = words[-1]["end"] if words else 0
    print(f"✅ 完成: {len(words)} 个词单元，时长约 {dur:.1f}s")
    print(f"   transcript.txt / words.json / segments.json → {args.outdir}")

if __name__ == "__main__":
    main()
