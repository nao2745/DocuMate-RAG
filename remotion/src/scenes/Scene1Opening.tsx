import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { COLORS } from "../components/colors";

const FileIcon: React.FC<{ x: number; y: number; delay: number; label: string }> = ({ x, y, delay, label }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacity = interpolate(frame, [delay, delay + 8], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const translateY = interpolate(frame, [delay, delay + 8], [-20, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  return (
    <div style={{ position: "absolute", left: x, top: y + translateY, opacity, textAlign: "center" }}>
      <div style={{
        width: 64, height: 80, borderRadius: 6,
        background: COLORS.bgCard, border: `2px solid ${COLORS.border}`,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 28,
      }}>
        📄
      </div>
      <div style={{ fontSize: 11, color: COLORS.textSecondary, marginTop: 4, width: 70 }}>{label}</div>
    </div>
  );
};

export const Scene1Opening: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const fadeOut = interpolate(frame, [220, 270], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const textOpacity = interpolate(frame, [10, 25], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const textY = interpolate(frame, [10, 25], [20, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const files = [
    { x: 120, y: 150, delay: 0, label: "規程.pdf" },
    { x: 240, y: 130, delay: 5, label: "manual.docx" },
    { x: 360, y: 160, delay: 10, label: "議事録.md" },
    { x: 480, y: 140, delay: 15, label: "FAQ.txt" },
    { x: 600, y: 155, delay: 20, label: "仕様書.pdf" },
    { x: 720, y: 135, delay: 25, label: "報告書.docx" },
    { x: 840, y: 160, delay: 30, label: "手順書.pdf" },
    { x: 960, y: 145, delay: 35, label: "契約書.pdf" },
    { x: 200, y: 290, delay: 8, label: "設計書.pdf" },
    { x: 340, y: 275, delay: 14, label: "log.txt" },
    { x: 470, y: 300, delay: 22, label: "会議録.md" },
    { x: 600, y: 280, delay: 28, label: "予算.docx" },
    { x: 730, y: 295, delay: 33, label: "規約.pdf" },
    { x: 860, y: 270, delay: 38, label: "メモ.txt" },
  ];

  return (
    <div style={{
      width, height, background: COLORS.bg, overflow: "hidden", opacity: fadeOut,
      display: "flex", flexDirection: "column", alignItems: "center",
    }}>
      {/* Floating files */}
      <div style={{ position: "relative", width: "100%", height: 440 }}>
        {files.map((f, i) => <FileIcon key={i} {...f} />)}
        {/* Confused person emoji */}
        <div style={{
          position: "absolute", left: "50%", top: "50%",
          transform: "translate(-50%,-50%)",
          fontSize: 80, opacity: interpolate(frame, [50, 65], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}>
          😵
        </div>
      </div>

      {/* Text */}
      <div style={{
        opacity: textOpacity, transform: `translateY(${textY}px)`,
        textAlign: "center", padding: "0 80px",
      }}>
        <p style={{
          fontSize: 38, fontWeight: 700, color: COLORS.textPrimary,
          fontFamily: "'Noto Sans JP', sans-serif", lineHeight: 1.5,
        }}>
          社内ドキュメント、膨大すぎて<br />
          <span style={{ color: COLORS.accentLight }}>必要な情報を探すのに時間がかかっていませんか？</span>
        </p>
      </div>
    </div>
  );
};
