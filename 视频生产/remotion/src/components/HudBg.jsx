import { AbsoluteFill } from 'remotion';

// 暗场 HUD 背景：点阵 + 四角括号线 + 左上 ● REC 元数据。对齐 PIL 样张。
const DARK = '#15171C';
const HUD = '#2A3550';

function Corner({ style, h }) {
  return (
    <div style={{ position: 'absolute', ...style }}>
      <div style={{ position: 'absolute', width: 120, height: 2, background: HUD, ...(h.hx) }} />
      <div style={{ position: 'absolute', width: 2, height: 80, background: HUD, ...(h.vy) }} />
    </div>
  );
}

export function HudBg({ meta = '● REC  1920×1080  ·  SC-01 暗场HUD' }) {
  return (
    <AbsoluteFill style={{
      backgroundColor: DARK,
      backgroundImage: `radial-gradient(circle, #23262E 1.4px, transparent 1.5px)`,
      backgroundSize: '44px 44px',
      backgroundPosition: '0 0',
    }}>
      {/* 四角括号 */}
      <Corner style={{ left: 40, top: 40 }} h={{ hx: { left: 0, top: 0 }, vy: { left: 0, top: 0 } }} />
      <Corner style={{ right: 40, top: 40 }} h={{ hx: { right: 0, top: 0 }, vy: { right: 0, top: 0 } }} />
      <Corner style={{ left: 40, bottom: 40 }} h={{ hx: { left: 0, bottom: 0 }, vy: { left: 0, bottom: 0 } }} />
      <Corner style={{ right: 40, bottom: 40 }} h={{ hx: { right: 0, bottom: 0 }, vy: { right: 0, bottom: 0 } }} />
      {/* 左上元数据 */}
      <div style={{
        position: 'absolute', left: 60, top: 46,
        fontFamily: 'Menlo, monospace', fontSize: 16, color: HUD, letterSpacing: 1,
      }}>{meta}</div>
    </AbsoluteFill>
  );
}
