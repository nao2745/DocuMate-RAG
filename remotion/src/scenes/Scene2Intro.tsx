import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { COLORS } from "../components/colors";

export const Scene2Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const logoScale = spring({ frame, fps, config: { damping: 14, stiffness: 100 } });
  const logoOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });

  const subtitleOpacity = interpolate(frame, [20, 35], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const subtitleY = interpolate(frame, [20, 35], [15, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const featureOpacity = (delay: number) =>
    interpolate(frame, [delay, delay + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const featureX = (delay: number) =>
    interpolate(frame, [delay, delay + 12], [-30, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const features = [
    { icon: "📄", text: "PDF / Word / Markdown / TXT に対応", delay: 40 },
    { icon: "🔍", text: "ハイブリッド検索で高精度な文脈取得", delay: 55 },
    { icon: "💬", text: "自然言語で即座に回答生成", delay: 70 },
    { icon: "📌", text: "引用元・ページ番号付きで回答", delay: 85 },
  ];

  return (
    <div style={{
      width, height, background: `linear-gradient(135deg, ${COLORS.bg} 0%, #1a1040 100%)`,
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
    }}>
      {/* Logo */}
      <div style={{
        opacity: logoOpacity,
        transform: `scale(${logoScale})`,
        textAlign: "center", marginBottom: 16,
      }}>
        <div style={{ fontSize: 72 }}>📚</div>
        <h1 style={{
          fontSize: 72, fontWeight: 900, color: COLORS.textPrimary,
          fontFamily: "Inter, sans-serif", margin: 0,
          background: `linear-gradient(90deg, ${COLORS.accent}, ${COLORS.accentLight})`,
          WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
        }}>
          DocuMate
        </h1>
      </div>

      {/* Subtitle */}
      <p style={{
        opacity: subtitleOpacity,
        transform: `translateY(${subtitleY}px)`,
        fontSize: 26, color: COLORS.textSecondary,
        fontFamily: "'Noto Sans JP', sans-serif",
        marginBottom: 48,
      }}>
        社内ドキュメントに AI で直接"質問"する
      </p>

      {/* Features */}
      <div style={{ display: "flex", flexDirection: "column", gap: 16, width: 560 }}>
        {features.map((f, i) => (
          <div key={i} style={{
            opacity: featureOpacity(f.delay),
            transform: `translateX(${featureX(f.delay)}px)`,
            display: "flex", alignItems: "center", gap: 16,
            background: COLORS.bgCard, borderRadius: 12,
            padding: "14px 24px", border: `1px solid ${COLORS.border}`,
          }}>
            <span style={{ fontSize: 28 }}>{f.icon}</span>
            <span style={{ fontSize: 20, color: COLORS.textPrimary, fontFamily: "'Noto Sans JP', sans-serif" }}>
              {f.text}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
