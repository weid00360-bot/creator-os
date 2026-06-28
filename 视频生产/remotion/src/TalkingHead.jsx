import { AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { Captions } from './components/Captions.jsx';
import { BrollLayer } from './components/BrollCut.jsx';

// 主合成。图层从下到上：
//   1. 口播原视频（真人画面，保留全程，不剪）
//   2. B-roll 全屏切（指定几秒盖住人脸）
//   3. 逐词字幕（始终在最上层，B-roll 期间也继续可读）
export const TalkingHead = (props) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { source, captions, broll } = props;

  return (
    <AbsoluteFill style={{
      backgroundColor: '#0a0a12',
      fontFamily: "'PingFang SC', 'Noto Sans SC', 'Hiragino Sans GB', sans-serif",
    }}>
      {source && (
        <OffthreadVideo src={staticFile(source)} />
      )}
      <BrollLayer broll={broll} fps={fps} />
      <Captions captions={captions} frame={frame} fps={fps} />
    </AbsoluteFill>
  );
};
