import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { COLORS } from "../components/colors";

export const Scene7Closing: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const logoScale = spring({ frame, fps, config: { damping: 14, stiffness: 90 } });
  const logoOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });

  const taglineOpacity = interpolate(frame, [25, 40], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const taglineY = interpolate(frame, [25, 40], [20, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const dividerWidth = interpolate(frame, [45, 70], [0, 320], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const contactOpacity = interpolate(frame, [75, 90], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const statsOpacity = (delay: number) =>
    interpolate(frame, [delay, delay + 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const statsScale = (delay: number) =>
    spring({ frame: Math.max(0, frame - delay), fps, config: { damping: 12, stiffness: 100 } });

  const stats = [
    { value: "4形式", label: "対応ドキュメント", icon: "📄", delay: 95 },
    { value: "≤10s", label: "平均応答時間", icon: "⚡", delay: 108 },
    { value: "49件", label: "自動テスト", icon: "✅", delay: 121 },
    { value: "≥95%", label: "引用精度目標", icon: "🎯", delay: 134 },
  ];

  // Particle-like dots in background
  const dots = Array.from({ length: 20 }, (_, i) => ({
    x: (i * 67 + 120) % width,
    y: (i * 113 + 80) % height,
    size: 2 + (i % 3),
    opacity: 0.15 + (i % 4) * 0.05,
  }));

  return (
    <div style={{
      width, height,
      background: `radial-gradient(ellipse at center, #1a1040 0%, ${COLORS.bg} 70%)`,
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
      overflow: "hidden", position: "relative",
    }}>
      {/* Background dots */}
      {dots.map((d, i) => (
        <div key={i} style={{
          position: "absolute", left: d.x, top: d.y,
          width: d.size, height: d.size, borderRadius: "50%",
          background: COLORS.accent, opacity: d.opacity,
        }} />
      ))}

      {/* Logo */}
      <div style={{
        opacity: logoOpacity,
        transform: `scale(${logoScale})`,
        textAlign: "center", marginBottom: 8,
      }}>
        <div style={{ fontSize: 80 }}>📚</div>
        <h1 style={{
          fontSize: 96, fontWeight: 900, margin: 0,
          fontFamily: "Inter, sans-serif",
          background: `linear-gradient(90deg, ${COLORS.accent}, ${COLORS.accentLight}, #ec4899)`,
          WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
        }}>
          DocuMate
        </h1>
      </div>

      {/* Tagline */}
      <p style={{
        opacity: taglineOpacity,
        transform: `translateY(${taglineY}px)`,
        fontSize: 24, color: COLORS.textSecondary,
        fontFamily: "'Noto Sans JP', sans-serif",
        textAlign: "center", margin: "0 0 24px 0",
      }}>
        あなたの社内ドキュメントを、即答できる AI アシスタントに。
      </p>

      {/* Divider */}
      <div style={{
        width: dividerWidth, height: 2,
        background: `linear-gradient(90deg, ${COLORS.accent}, ${COLORS.accentLight})`,
        borderRadius: 2, marginBottom: 28,
      }} />

      {/* Stats */}
      <div style={{ display: "flex", gap: 24, marginBottom: 32 }}>
        {stats.map((s, i) => (
          <div key={i} style={{
            opacity: statsOpacity(s.delay),
            transform: `scale(${statsScale(s.delay)})`,
            background: COLORS.bgCard, border: `1px solid ${COLORS.border}`,
            borderRadius: 14, padding: "16px 24px", textAlign: "center", minWidth: 130,
          }}>
            <div style={{ fontSize: 28, marginBottom: 6 }}>{s.icon}</div>
            <div style={{ fontSize: 28, fontWeight: 900, color: COLORS.accentLight, fontFamily: "Inter, sans-serif" }}>{s.value}</div>
            <div style={{ fontSize: 13, color: COLORS.textSecondary, marginTop: 4 }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Contact */}
      <div style={{
        opacity: contactOpacity,
        display: "flex", gap: 24, alignItems: "center",
      }}>
        <div style={{
          background: COLORS.bgCard, border: `1px solid ${COLORS.border}`,
          borderRadius: 10, padding: "10px 20px",
          display: "flex", alignItems: "center", gap: 10,
        }}>
          <span style={{ fontSize: 18 }}>🐙</span>
          <span style={{ color: COLORS.textSecondary, fontSize: 15 }}>github.com / DocuMate</span>
        </div>
        <div style={{
          background: `linear-gradient(90deg, ${COLORS.accent}, ${COLORS.accentLight})`,
          borderRadius: 10, padding: "10px 24px",
          color: "#fff", fontWeight: 700, fontSize: 15,
        }}>
          お問い合わせはこちら
        </div>
      </div>
    </div>
  );
};
