import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from 'remotion';

// 打字机 PPT 视频：标题 + 正文逐字符"打印"出现，跟语速。16:9，奶油底，放进电视屏幕区。
// props: { title, subtitle, lines:[{text, color}], cps(每秒字数), fps }
const COBALT = '#1F4ED8';
const RED = '#D63737';
const BLACK = '#1C1E24';
const GRAY = '#787880';
const CREAM = '#F3EFE7';
const COLORS = { cobalt: COBALT, red: RED, black: BLACK, gray: GRAY };

export const TypewriterSlide = (props) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { title, subtitle, lines = [], cps = 9, titleInstant = true } = props;

  // 标题：可瞬显（titleInstant）或也参与打字
  const bodyLines = lines.map((l) => (typeof l === 'string' ? { text: l, color: 'black' } : l));

  // 正文逐字：把所有行拼成一个字符流，按 cps 推进
  const flat = [];
  bodyLines.forEach((ln, li) => {
    for (let ci = 0; ci < ln.text.length; ci++) flat.push({ li, ch: ln.text[ci], color: ln.color || 'black' });
    if (li < bodyLines.length - 1) flat.push({ li, ch: '\n', color: ln.color });
  });

  const titleChars = titleInstant ? 0 : (title?.length || 0);
  const startFrame = titleInstant ? 6 : 0; // 标题瞬显后停半拍再打正文
  const visible = Math.max(0, Math.floor(((frame - startFrame) * cps) / fps));

  // 当前每行已显示的字符
  const shownByLine = bodyLines.map(() => '');
  let count = 0;
  for (const item of flat) {
    if (count >= visible) break;
    if (item.ch !== '\n') shownByLine[item.li] += item.ch;
    count++;
  }
  const typing = visible < flat.length;
  const cursorOn = Math.floor(frame / 8) % 2 === 0; // 光标闪烁
  // 当前正在打的行
  let curLine = 0;
  { let c = 0; for (const it of flat) { if (c >= visible) break; curLine = it.li; c++; } }

  const titleOpacity = titleInstant ? interpolate(frame, [0, 5], [0, 1], { extrapolateRight: 'clamp' }) : 1;

  return (
    <AbsoluteFill style={{
      background: CREAM,
      fontFamily: "'Hiragino Sans GB', 'PingFang SC', sans-serif",
      padding: '70px 90px',
    }}>
      {/* 点阵底纹 */}
      <AbsoluteFill style={{
        backgroundImage: 'radial-gradient(circle, #DDD8CE 1.5px, transparent 1.6px)',
        backgroundSize: '34px 34px', opacity: 0.6,
      }} />

      {/* 标题 */}
      <div style={{ position: 'relative', opacity: titleOpacity }}>
        <div style={{ fontSize: 66, fontWeight: 900, color: COBALT, letterSpacing: 1 }}>{title}</div>
        <div style={{ height: 8, width: 220, background: RED, borderRadius: 4, marginTop: 10 }} />
        {subtitle && <div style={{ fontSize: 34, fontWeight: 700, color: GRAY, marginTop: 22 }}>{subtitle}</div>}
      </div>

      {/* 正文逐字 */}
      <div style={{ position: 'relative', marginTop: 46, fontSize: 40, fontWeight: 700, lineHeight: 1.7 }}>
        {bodyLines.map((ln, i) => (
          <div key={i} style={{ color: COLORS[ln.color] || BLACK, minHeight: 56 }}>
            <span style={{
              textDecoration: ln.strike ? 'line-through' : 'none',
              textDecorationColor: RED,
              textDecorationThickness: 4,
            }}>{shownByLine[i]}</span>
            {typing && i === curLine && (
              <span style={{ opacity: cursorOn ? 1 : 0, color: COBALT, fontWeight: 900 }}>▋</span>
            )}
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
