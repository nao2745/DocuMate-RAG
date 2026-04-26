import React from "react";
import { AbsoluteFill, Series } from "remotion";
import { Scene1Opening } from "./scenes/Scene1Opening";
import { Scene2Intro } from "./scenes/Scene2Intro";
import { Scene3Upload } from "./scenes/Scene3Upload";
import { Scene4Chat } from "./scenes/Scene4Chat";
import { Scene5Architecture } from "./scenes/Scene5Architecture";
import { Scene6Quality } from "./scenes/Scene6Quality";
import { Scene7Closing } from "./scenes/Scene7Closing";

// 30fps: 1s = 30 frames
// Total ~90s = 2700 frames
export const DocuMatePromo: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: "#0f1117" }}>
      <Series>
        <Series.Sequence durationInFrames={300}>  {/* 0:00-0:10 */}
          <Scene1Opening />
        </Series.Sequence>
        <Series.Sequence durationInFrames={450}>  {/* 0:10-0:25 */}
          <Scene2Intro />
        </Series.Sequence>
        <Series.Sequence durationInFrames={300}>  {/* 0:25-0:35 */}
          <Scene3Upload />
        </Series.Sequence>
        <Series.Sequence durationInFrames={450}>  {/* 0:35-0:50 */}
          <Scene4Chat />
        </Series.Sequence>
        <Series.Sequence durationInFrames={450}>  {/* 0:50-1:05 */}
          <Scene5Architecture />
        </Series.Sequence>
        <Series.Sequence durationInFrames={450}>  {/* 1:05-1:20 */}
          <Scene6Quality />
        </Series.Sequence>
        <Series.Sequence durationInFrames={300}>  {/* 1:20-1:30 */}
          <Scene7Closing />
        </Series.Sequence>
      </Series>
    </AbsoluteFill>
  );
};
