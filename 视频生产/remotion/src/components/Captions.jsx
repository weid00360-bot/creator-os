import { AbsoluteFill, interpolate, spring } from 'remotion';

// ── 配色 ──────────────────────────────────────────────────────
const GREEN = '#4ade80';
const YELLOW = '#facc15';
const RED = '#f87171';
const BLUE = '#60a5fa';
const WHITE = '#ffffff';
const HL_COLORS = { green: GREEN, yellow: YELLOW, red: RED, blue: BLUE };

// 版面预设：竖版(v)字幕在下三分之一避人脸；横版(h)在底部居中、字号小、留白宽。
const LAYOUTS = {
  v: { font: 70, maxw: 900, bottom: 420, tagFont: 30, emoji: 58, stroke: 10 },
  h: { font: 56, maxw: 1400, bottom: 80, tagFont: 26, emoji: 46, stroke: 8 },
};

// ── 单词 ──────────────────────────────────────────────────────
function Word({ word, lf, fps, cfg }) {
  const wf = lf - (word.at ?? 0);
  if (wf < 0) return null;

  const s = spring({ fps, frame: wf, config: { damping: 11, stiffness: 320, mass: 0.6 } });
  const scale = interpolate(s, [0, 1], [1.45, 1]);
  const opacity = interpolate(wf, [0, 3], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const color = word.highlight ? HL_COLORS[word.highlight] : WHITE;

  return (
    <span style={{
      display: 'inline-block',
      position: 'relative',
      margin: '0 10px',
      opacity,
      transform: `scale(${scale})`,
      color,
      WebkitTextStroke: `${cfg.stroke}px black`,
      paintOrder: 'stroke fill',
      textShadow: word.highlight
        ? `0 0 30px ${color}88, 0 6px 0 rgba(0,0,0,0.9)`
        : '0 6px 0 rgba(0,0,0,0.9)',
    }}>
      {word.t}
      {word.emoji && (
        <span style={{
          position: 'absolute',
          top: -(cfg.emoji + 4), left: '50%',
          fontSize: cfg.emoji,
          WebkitTextStroke: '0px',
          transform: `translateX(-50%) scale(${interpolate(s, [0, 1], [0, 1])}) rotate(${interpolate(s, [0, 1], [-25, 0])}deg)`,
          filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.6))',
        }}>
          {word.emoji}
        </span>
      )}
    </span>
  );
}

// ── 一屏字幕 ──────────────────────────────────────────────────
function CaptionGroup({ group, frame, fps, cfg }) {
  const lf = frame - group.start;
  if (lf < 0 || frame >= group.end) return null;

  let punchScale = 1;
  for (const w of group.words) {
    if (!w.punch) continue;
    const wf = lf - (w.at ?? 0);
    if (wf >= 0 && wf < 12) {
      punchScale = 1 + interpolate(wf, [0, 4, 12], [0, 0.06, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
    }
  }

  const groupOpacity = interpolate(frame, [group.end - 6, group.end], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'flex-end',
      paddingBottom: cfg.bottom,
      paddingLeft: 60,
      paddingRight: 60,
      opacity: groupOpacity,
      transform: `scale(${punchScale})`,
    }}>
      {group.tag && (
        <div style={{
          marginBottom: 28,
          transform: `translateY(${interpolate(lf, [0, 10], [-20, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })}px)`,
          opacity: interpolate(lf, [0, 10], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }),
          background: 'rgba(250,204,21,0.14)',
          border: '2px solid rgba(250,204,21,0.5)',
          borderRadius: 50,
          padding: '8px 28px',
          fontSize: cfg.tagFont,
          fontWeight: 800,
          color: YELLOW,
          letterSpacing: 3,
        }}>
          {group.tag}
        </div>
      )}
      <div style={{
        textAlign: 'center',
        fontSize: cfg.font,
        fontWeight: 900,
        lineHeight: 1.5,
        letterSpacing: '1px',
        maxWidth: cfg.maxw,
      }}>
        {group.words.map((w, i) => (
          <Word key={i} word={w} lf={lf} fps={fps} cfg={cfg} />
        ))}
      </div>
    </AbsoluteFill>
  );
}

export function Captions({ captions, frame, fps, layout = 'v' }) {
  const cfg = LAYOUTS[layout] ?? LAYOUTS.v;
  return (
    <>
      {(captions ?? []).map((g, i) => (
        <CaptionGroup key={i} group={g} frame={frame} fps={fps} cfg={cfg} />
      ))}
    </>
  );
}
