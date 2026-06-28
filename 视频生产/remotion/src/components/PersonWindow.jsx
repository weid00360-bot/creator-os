import { OffthreadVideo, staticFile } from 'remotion';

// 圆形蒙版人物窗（不抠像）。把竖版口播源按裁剪框 cover-fit 进圆，压暗融进暗场。
// 参数全部从 props.person 读，换源/换构图零改代码。详见 模板库/画面与动效.md SC-01。
const SRC_W = 1080;
const SRC_H = 1920;
const COBALT = '#1F4ED8';

export function PersonWindow({ source, person }) {
  if (!source || !person) return null;
  const {
    cropX = 103, cropY = 440, cropSize = 875, // 1080×1920 源上的取景方框
    diameter = 300,                            // 圆窗直径
    marginRight = 60, marginTop = 60,          // 右上角定位
    brightness = 0.86, saturate = 0.9,         // 压暗融场
    name = '迪迪',
  } = person;

  const scale = diameter / cropSize;
  const vW = SRC_W * scale;
  const vH = SRC_H * scale;
  const vLeft = -cropX * scale;
  const vTop = -cropY * scale;

  return (
    <div style={{ position: 'absolute', right: marginRight, top: marginTop, width: diameter, height: diameter }}>
      <div style={{
        width: diameter, height: diameter, borderRadius: '50%', overflow: 'hidden',
        position: 'relative',
        filter: `brightness(${brightness}) saturate(${saturate})`,
        boxShadow: `0 0 0 3px ${COBALT}, 0 0 0 8px #1A3370, 0 0 0 13px #0E1A38, 0 0 32px rgba(31,78,216,0.45)`,
      }}>
        <OffthreadVideo src={staticFile(source)} muted style={{
          position: 'absolute', width: vW, height: vH, left: vLeft, top: vTop, maxWidth: 'none',
        }} />
      </div>
      {name && (
        <div style={{
          position: 'absolute', left: '50%', top: diameter + 14, transform: 'translateX(-50%)',
          background: COBALT, color: '#fff', fontWeight: 800, fontSize: 22,
          padding: '5px 22px', borderRadius: 10, whiteSpace: 'nowrap', letterSpacing: 2,
        }}>{name}</div>
      )}
    </div>
  );
}
