import { Composition } from 'remotion';
import { TalkingHead } from './TalkingHead.jsx';
import { TalkingHeadH } from './TalkingHeadH.jsx';
import { TypewriterSlide } from './Typewriter.jsx';
// Studio 预览用：加载「当前项目」时间线（渲染时仍会被 --props 覆盖）。
// _active.json 由 studio.mjs 在启动时从目标项目复制过来，换项目零改代码。
import activeTimeline from './_active.json';

// 裸开占位（activeTimeline 缺失时的兜底）。
const DEMO_PROPS = {
  fps: 30,
  width: 1080,
  height: 1920,
  source: null, // 没有底层视频时只显示字幕，方便单测字幕样式
  durationInFrames: 90,
  captions: [
    { start: 0, end: 90, tag: '占位', words: [
      { t: '把', at: 0 },
      { t: 'timeline.json', at: 6, highlight: 'green', punch: true },
      { t: '喂进来', at: 22, emoji: '👇' },
    ]},
  ],
  broll: [],
};

const calc = ({ props }) => {
  const fps = props.fps ?? 30;
  const lastCap = (props.captions ?? []).reduce((m, c) => Math.max(m, c.end ?? 0), 0);
  const lastBroll = (props.broll ?? []).reduce((m, b) => Math.max(m, b.to ?? 0), 0);
  const durationInFrames = props.durationInFrames ?? Math.max(lastCap, lastBroll, 30);
  return {
    durationInFrames: Math.round(durationInFrames),
    fps,
    width: props.width ?? 1080,
    height: props.height ?? 1920,
  };
};

// 横版裸开占位（含圆窗参数，单测构图用）。
const DEMO_H = {
  fps: 30, width: 1920, height: 1080, durationInFrames: 90,
  source: 'input.mov',
  person: { cropX: 103, cropY: 440, cropSize: 875, diameter: 300, marginRight: 60, marginTop: 60, brightness: 0.86, saturate: 0.9, name: '迪迪' },
  captions: [
    { start: 0, end: 90, tag: '钩子', words: [
      { t: '但我今天', at: 0 },
      { t: '不想', at: 8, highlight: 'red', punch: true },
      { t: '像卖课一样', at: 18 },
    ]},
  ],
  broll: [],
  meta: '● REC  1920×1080  ·  SC-01 暗场HUD',
};

export const RemotionRoot = () => {
  return (
    <>
      <Composition
        id="TalkingHead"
        component={TalkingHead}
        defaultProps={activeTimeline ?? DEMO_PROPS}
        calculateMetadata={calc}
        fps={30}
        width={1080}
        height={1920}
        durationInFrames={90}
      />
      <Composition
        id="TalkingHeadH"
        component={TalkingHeadH}
        defaultProps={(activeTimeline && activeTimeline.width >= activeTimeline.height) ? activeTimeline : DEMO_H}
        calculateMetadata={calc}
        fps={30}
        width={1920}
        height={1080}
        durationInFrames={90}
      />
      <Composition
        id="Typewriter"
        component={TypewriterSlide}
        defaultProps={{
          title: '① 分工定型了',
          subtitle: '人管「做什么」· AI 管「怎么做」',
          cps: 5,
          lines: [
            { text: '人做 70% 规划 · AI 做 80% 执行', color: 'cobalt' },
            { text: '越懂行，AI 每条指令干的活越多越准', color: 'black' },
            { text: '专家 12 动作 vs 小白 5 个 = 2.4 倍', color: 'red' },
            { text: '洞察：判断力，就是 AI 的乘数', color: 'cobalt' },
          ],
        }}
        calculateMetadata={({ props }) => {
          const fps = 30;
          const cps = props.cps ?? 5;
          const chars = (props.lines ?? []).reduce((n, l) => n + (l.text?.length ?? 0), 0);
          const START = 6, HOLD = 72; // 标题瞬显延迟 + 打完停留2.4s
          return { fps, width: 1280, height: 720, durationInFrames: Math.ceil(START + (chars / cps) * fps + HOLD) };
        }}
        fps={30}
        width={1280}
        height={720}
        durationInFrames={300}
      />
    </>
  );
};
