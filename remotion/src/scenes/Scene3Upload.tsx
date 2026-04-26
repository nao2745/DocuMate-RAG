import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { COLORS } from "../components/colors";

export const Scene3Upload: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const panelOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });

  // Step label
  const stepOpacity = interpolate(frame, [5, 18], [0, 1], { extrapolateRight: "clamp" });

  // Upload zone highlight
  const uploadGlow = interpolate(frame, [30, 50, 70, 90], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // File drops in
  const fileDropY = interpolate(frame, [55, 75], [-60, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const fileDropOpacity = interpolate(frame, [55, 70], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Spinner → checkmark
  const spinnerOpacity = interpolate(frame, [80, 95, 130, 145], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const checkOpacity = interpolate(frame, [145, 158], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const checkScale = spring({ frame: Math.max(0, frame - 145), fps, config: { damping: 12, stiffness: 120 } });

  return (
    <div style={{
      width, height, background: COLORS.bg,
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
    }}>
      {/* Step label */}
      <div style={{
        opacity: stepOpacity, marginBottom: 32,
        background: COLORS.accent, borderRadius: 999,
        padding: "6px 24px",
      }}>
        <span style={{ fontSize: 18, fontWeight: 700, color: "#fff", fontFamily: "Inter, sans-serif" }}>
          STEP 1 — ドキュメントを取り込む
        </span>
      </div>

      {/* App window */}
      <div style={{
        opacity: panelOpacity,
        width: 780, background: COLORS.bgCard,
        borderRadius: 16, border: `1px solid ${COLORS.border}`,
        overflow: "hidden", boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
      }}>
        {/* Title bar */}
        <div style={{
          background: "#13162a", padding: "12px 20px",
          borderBottom: `1px solid ${COLORS.border}`,
          display: "flex", alignItems: "center", gap: 8,
        }}>
          <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#ef4444" }} />
          <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#f59e0b" }} />
          <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#10b981" }} />
          <span style={{ marginLeft: 16, color: COLORS.textSecondary, fontSize: 14 }}>📁 ドキュメント管理</span>
        </div>

        <div style={{ padding: 32 }}>
          {/* Upload zone */}
          <div style={{
            border: `2px dashed ${uploadGlow > 0.5 ? COLORS.accent : COLORS.border}`,
            borderRadius: 12, padding: 32, textAlign: "center",
            background: uploadGlow > 0.5 ? "rgba(108,99,255,0.08)" : "transparent",
            transition: "all 0.2s",
            position: "relative", minHeight: 160,
            display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
          }}>
            {/* Dropping file */}
            <div style={{
              opacity: fileDropOpacity,
              transform: `translateY(${fileDropY}px)`,
              position: "absolute", top: 30,
            }}>
              <div style={{
                background: COLORS.bg, border: `1px solid ${COLORS.accent}`,
                borderRadius: 8, padding: "8px 20px",
                display: "flex", alignItems: "center", gap: 10,
                boxShadow: `0 4px 20px rgba(108,99,255,0.4)`,
              }}>
                <span style={{ fontSize: 24 }}>📄</span>
                <span style={{ color: COLORS.textPrimary, fontSize: 16 }}>company_manual.pdf</span>
              </div>
            </div>

            <span style={{ fontSize: 40, marginBottom: 12, opacity: fileDropOpacity < 0.5 ? 1 : 0.3 }}>☁️</span>
            <p style={{ color: COLORS.textSecondary, fontSize: 18, margin: 0 }}>
              PDF / Word / Markdown / TXT をドロップ
            </p>
          </div>

          {/* Category input */}
          <div style={{ marginTop: 20, display: "flex", gap: 12, alignItems: "center" }}>
            <span style={{ color: COLORS.textSecondary, fontSize: 16 }}>カテゴリ:</span>
            <div style={{
              background: COLORS.bg, border: `1px solid ${COLORS.border}`,
              borderRadius: 8, padding: "8px 16px", flex: 1,
              color: COLORS.textPrimary, fontSize: 16,
            }}>general</div>
            <div style={{
              background: COLORS.accent, borderRadius: 8,
              padding: "8px 24px", cursor: "pointer",
              color: "#fff", fontWeight: 700, fontSize: 16,
            }}>取り込む</div>
          </div>

          {/* Status */}
          <div style={{ marginTop: 24, minHeight: 48, display: "flex", alignItems: "center", justifyContent: "center" }}>
            {/* Spinner */}
            <div style={{ opacity: spinnerOpacity, display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{
                width: 24, height: 24, border: `3px solid ${COLORS.accent}`,
                borderTopColor: "transparent", borderRadius: "50%",
                animation: "spin 1s linear infinite",
              }} />
              <span style={{ color: COLORS.textSecondary, fontSize: 16 }}>company_manual.pdf を取り込み中…</span>
            </div>

            {/* Success */}
            <div style={{
              opacity: checkOpacity,
              transform: `scale(${checkScale})`,
              display: "flex", alignItems: "center", gap: 12,
              background: "rgba(16,185,129,0.15)", border: `1px solid ${COLORS.green}`,
              borderRadius: 10, padding: "10px 20px",
            }}>
              <span style={{ fontSize: 24 }}>✅</span>
              <span style={{ color: COLORS.green, fontSize: 18, fontWeight: 600 }}>
                company_manual.pdf (42 ページ) — 取り込み完了
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
