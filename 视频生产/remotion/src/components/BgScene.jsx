import { AbsoluteFill, Img, staticFile } from 'remotion';

// 背景场景：暖色墙面 + 电视机框（PNG，屏幕区留给图卡）。替代纯黑暗场，让人物/PPT不割裂。
export function BgScene({ asset = 'assets/bg_tv.png' }) {
  return (
    <AbsoluteFill style={{ backgroundColor: '#E5DFD2' }}>
      <Img src={staticFile(asset)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
    </AbsoluteFill>
  );
}
