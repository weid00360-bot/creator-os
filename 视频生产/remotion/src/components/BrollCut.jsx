import { AbsoluteFill, Img, interpolate, staticFile, Sequence } from 'remotion';

// 全屏 B-roll 切：在 [from, to) 期间盖住人脸，几秒后切回。
// asset 为空时显示「待补图」占位卡（带 label），管线在补图前也能跑通。
function Card({ asset, label, lf, dur }) {
  const fadeIn = interpolate(lf, [0, 6], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const fadeOut = interpolate(lf, [dur - 6, dur], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const opacity = Math.min(fadeIn, fadeOut);
  const scale = interpolate(lf, [0, 12], [1.06, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ opacity, background: '#0a0a12' }}>
      {asset ? (
        <Img
          src={staticFile(asset)}
          style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})` }}
        />
      ) : (
        <AbsoluteFill style={{
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexDirection: 'column', padding: 80, textAlign: 'center',
          border: '6px dashed rgba(250,204,21,0.5)',
        }}>
          <div style={{ fontSize: 44, color: '#facc15', fontWeight: 900, marginBottom: 24 }}>📷 待补图</div>
          <div style={{ fontSize: 40, color: '#fff', fontWeight: 700, lineHeight: 1.5 }}>{label}</div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
}

export function BrollLayer({ broll, fps }) {
  return (
    <>
      {(broll ?? []).map((b, i) => {
        const from = Math.round(b.from);
        const dur = Math.max(1, Math.round(b.to - b.from));
        return (
          <Sequence key={i} from={from} durationInFrames={dur} name={`broll-${i}`}>
            <BrollInner asset={b.asset} label={b.label} dur={dur} />
          </Sequence>
        );
      })}
    </>
  );
}

// Sequence 内 useCurrentFrame 从 0 起算，正好当作本段局部帧
import { useCurrentFrame } from 'remotion';
function BrollInner({ asset, label, dur }) {
  const lf = useCurrentFrame();
  return <Card asset={asset} label={label} lf={lf} dur={dur} />;
}
