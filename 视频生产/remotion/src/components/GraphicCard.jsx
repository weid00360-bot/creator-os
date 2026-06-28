import { Img, staticFile, interpolate, spring } from 'remotion';

// 图卡层（横版）：图卡显示在背景电视的「屏幕区」里，多种转场轮换换台。
// 屏幕区坐标须与 assets/bg_tv.png 的屏幕凹槽对齐。
const SCREEN = { left: 96, top: 176, width: 1080, height: 752 };
const RADIUS = 16;

// 转场类型（按段 index 轮换，像电视换台）
const TRANSITIONS = ['slideRight', 'zoomIn', 'slideUp', 'flipIn'];

function enterTransform(type, s) {
  switch (type) {
    case 'slideRight': return { transform: `translateX(${interpolate(s, [0, 1], [SCREEN.width * 0.6, 0])}px)` };
    case 'slideUp':    return { transform: `translateY(${interpolate(s, [0, 1], [SCREEN.height * 0.5, 0])}px)` };
    case 'zoomIn':     return { transform: `scale(${interpolate(s, [0, 1], [0.7, 1])})` };
    case 'flipIn':     return { transform: `perspective(1400px) rotateY(${interpolate(s, [0, 1], [78, 0])}deg)`, transformOrigin: 'left center' };
    default:           return {};
  }
}

function Card({ asset, label, opacity = 1, extra = {}, dim = false }) {
  return (
    <div style={{
      position: 'absolute', left: 0, top: 0, width: SCREEN.width, height: SCREEN.height,
      opacity, ...extra,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: asset ? '#15171C' : '#20242C',
    }}>
      {asset ? (
        <Img src={staticFile(asset)} style={{
          width: '100%', height: '100%', objectFit: 'contain',
          filter: dim ? 'brightness(0.5) saturate(0.85)' : 'none',
        }} />
      ) : (
        <div style={{ textAlign: 'center', color: '#7E8CA8', fontWeight: 800 }}>
          <div style={{ fontSize: 56, marginBottom: 14 }}>📺</div>
          <div style={{ fontSize: 30 }}>待补图</div>
          {label && <div style={{ fontSize: 22, marginTop: 8, color: '#5B6680' }}>{label}</div>}
        </div>
      )}
    </div>
  );
}

export function GraphicLayer({ broll, fps, frame, fallbackAsset }) {
  return (
    // 屏幕区裁切容器：转场滑入/翻转都被屏幕边界裁掉，像真电视换台
    <div style={{
      position: 'absolute', ...SCREEN, borderRadius: RADIUS, overflow: 'hidden',
    }}>
      {/* 底层常驻框架图（压暗），防屏幕空黑 */}
      {fallbackAsset && <Card asset={fallbackAsset} dim opacity={0.9} />}
      {/* 各段图卡，转场入场 */}
      {(broll ?? []).map((b, i) => {
        if (frame < b.from || frame >= b.to) return null;
        const lf = frame - b.from;
        const type = b.transition || TRANSITIONS[i % TRANSITIONS.length];
        const s = spring({ fps, frame: lf, config: { damping: 18, stiffness: 170, mass: 0.8 } });
        const opIn = interpolate(lf, [0, 8], [0, 1], { extrapolateRight: 'clamp' });
        const opOut = interpolate(frame, [b.to - 8, b.to], [1, 0], { extrapolateLeft: 'clamp' });
        // 转场期间轻微运动模糊
        const blur = interpolate(s, [0, 0.6, 1], [6, 1, 0], { extrapolateRight: 'clamp' });
        const ent = enterTransform(type, s);
        return (
          <Card key={i} asset={b.asset} label={b.label}
            opacity={opIn * opOut}
            extra={{ ...ent, filter: `blur(${blur}px)` }} />
        );
      })}
    </div>
  );
}
