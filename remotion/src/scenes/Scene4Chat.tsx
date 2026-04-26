import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { COLORS } from "../components/colors";

const QUESTION = "有給休暇の申請手続きを教えてください";
const ANSWER = `有給休暇の申請は以下の手順で行います。

1. **申請フォームの記入** — 社内ポータルから「有給申請書」をダウンロード
2. **上長への提出** — 取得希望日の 3 営業日前までに提出
3. **承認確認** — メールで承認通知が届いたら手続き完了

有給は年間 **20日** 付与され、未消化分は翌年に繰越可能です。`;

export const Scene4Chat: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const stepOpacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });

  // Question bubble appears
  const qOpacity = interpolate(frame, [15, 28], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const qX = interpolate(frame, [15, 28], [30, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Typing indicator
  const typingOpacity = interpolate(frame, [35, 45, 95, 105], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Answer appears char by char
  const answerProgress = interpolate(frame, [105, 195], [0, ANSWER.length], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const visibleAnswer = ANSWER.slice(0, Math.floor(answerProgress));
  const answerOpacity = interpolate(frame, [105, 115], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Citation sidebar
  const sidebarOpacity = interpolate(frame, [200, 215], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const sidebarX = interpolate(frame, [200, 215], [40, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Feedback buttons
  const fbOpacity = interpolate(frame, [210, 225], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <div style={{
      width, height, background: COLORS.bg,
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
    }}>
      {/* Step label */}
      <div style={{ opacity: stepOpacity, marginBottom: 24, background: COLORS.green, borderRadius: 999, padding: "6px 24px" }}>
        <span style={{ fontSize: 18, fontWeight: 700, color: "#fff", fontFamily: "Inter, sans-serif" }}>
          STEP 2 — チャットで質問する
        </span>
      </div>

      <div style={{ display: "flex", gap: 20, width: 1140, alignItems: "flex-start" }}>
        {/* Chat window */}
        <div style={{
          flex: 1, background: COLORS.bgCard, borderRadius: 16,
          border: `1px solid ${COLORS.border}`, overflow: "hidden",
          boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
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
            <span style={{ marginLeft: 16, color: COLORS.textSecondary, fontSize: 14 }}>💬 DocuMate チャット</span>
          </div>

          <div style={{ padding: "24px 28px", minHeight: 400 }}>
            {/* User question */}
            <div style={{
              opacity: qOpacity, transform: `translateX(${qX}px)`,
              display: "flex", justifyContent: "flex-end", marginBottom: 20,
            }}>
              <div style={{
                background: COLORS.accent, borderRadius: "16px 16px 4px 16px",
                padding: "12px 20px", maxWidth: "70%",
                color: "#fff", fontSize: 17, fontFamily: "'Noto Sans JP', sans-serif",
              }}>
                {QUESTION}
              </div>
            </div>

            {/* Typing indicator */}
            <div style={{ opacity: typingOpacity, display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
              <span style={{ fontSize: 24 }}>🤖</span>
              <div style={{
                background: COLORS.bgCard, border: `1px solid ${COLORS.border}`,
                borderRadius: "4px 16px 16px 16px", padding: "12px 20px",
              }}>
                <span style={{ color: COLORS.textSecondary, fontSize: 16 }}>⏳ 回答を生成中…</span>
              </div>
            </div>

            {/* Answer */}
            <div style={{ opacity: answerOpacity, display: "flex", gap: 12, alignItems: "flex-start" }}>
              <span style={{ fontSize: 24, flexShrink: 0 }}>🤖</span>
              <div style={{
                background: "#1e2235", border: `1px solid ${COLORS.border}`,
                borderRadius: "4px 16px 16px 16px", padding: "16px 20px", flex: 1,
              }}>
                <pre style={{
                  color: COLORS.textPrimary, fontSize: 15,
                  fontFamily: "'Noto Sans JP', sans-serif",
                  whiteSpace: "pre-wrap", margin: 0, lineHeight: 1.7,
                }}>
                  {visibleAnswer}
                  {Math.floor(answerProgress) < ANSWER.length && (
                    <span style={{ background: COLORS.accent, width: 2, display: "inline-block" }}>&nbsp;</span>
                  )}
                </pre>

                {/* Feedback buttons */}
                <div style={{ opacity: fbOpacity, display: "flex", gap: 10, marginTop: 16 }}>
                  <button style={{
                    background: "rgba(16,185,129,0.15)", border: `1px solid ${COLORS.green}`,
                    borderRadius: 8, padding: "6px 16px", color: COLORS.green,
                    fontSize: 15, cursor: "pointer",
                  }}>👍 役立った</button>
                  <button style={{
                    background: "rgba(239,68,68,0.1)", border: `1px solid ${COLORS.red}`,
                    borderRadius: 8, padding: "6px 16px", color: COLORS.red,
                    fontSize: 15, cursor: "pointer",
                  }}>👎 的外れ</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Citation sidebar */}
        <div style={{
          width: 280, opacity: sidebarOpacity, transform: `translateX(${sidebarX}px)`,
          background: COLORS.bgCard, borderRadius: 16,
          border: `1px solid ${COLORS.border}`, padding: 20,
          boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
        }}>
          <h3 style={{ color: COLORS.textPrimary, fontSize: 16, margin: "0 0 16px 0" }}>📄 引用元</h3>
          {[
            { file: "company_manual.pdf", page: 12, score: "0.9241", excerpt: "有給休暇の申請は取得希望日の3営業日前までに..." },
            { file: "company_manual.pdf", page: 13, score: "0.8873", excerpt: "年間20日の有給が付与され、未消化分は..." },
            { file: "hr_policy.pdf", page: 5, score: "0.8102", excerpt: "上長の承認後、メールにて通知が..." },
          ].map((src, i) => (
            <div key={i} style={{
              marginBottom: 12, background: COLORS.bg,
              borderRadius: 10, padding: 12,
              border: `1px solid ${COLORS.border}`,
              opacity: interpolate(frame, [200 + i * 8, 215 + i * 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            }}>
              <div style={{ color: COLORS.accentLight, fontSize: 13, fontWeight: 600 }}>
                {src.file}  p.{src.page}
              </div>
              <div style={{ color: COLORS.textSecondary, fontSize: 11, marginTop: 4 }}>
                スコア: {src.score}
              </div>
              <div style={{ color: COLORS.textSecondary, fontSize: 12, marginTop: 6 }}>
                {src.excerpt}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
