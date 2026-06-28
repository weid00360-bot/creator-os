import { AbsoluteFill, Audio, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { PersonWindow } from './components/PersonWindow.jsx';
import { BgScene } from './components/BgScene.jsx';
import { GraphicLayer } from './components/GraphicCard.jsx';

// 横版主合成 1920×1080（背景电视框 + 圆窗蒙版人物）。图层从下到上：
//   1. 背景场景（暖墙 + 电视机框，替代纯黑暗场）
//   2. 图卡层（PPT 显示在电视屏幕区，多种转场换台）
//   3. 右上圆形蒙版人物窗（不抠像，压暗融场）
//   4. 独立口播音频轨（不跟圆窗视频走，避免预览 seek 重播）
//   字幕不在此生成 —— 迪迪后期用剪映自动加。
export const TalkingHeadH = (props) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { source, broll, person, fallbackAsset, bgAsset } = props;

  return (
    <AbsoluteFill style={{
      backgroundColor: '#E5DFD2',
      fontFamily: "'Hiragino Sans GB', 'PingFang SC', 'Noto Sans SC', sans-serif",
    }}>
      <BgScene asset={bgAsset} />
      <GraphicLayer broll={broll} fps={fps} frame={frame} fallbackAsset={fallbackAsset} />
      <PersonWindow source={source} person={person} />
      {source && <Audio src={staticFile(source)} />}
    </AbsoluteFill>
  );
};
