import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { COLORS } from "../components/colors";

const TEST_LINES = [
  { text: "tests/test_chunker.py::test_chunker_produces_chunks", status: "PASSED" },
  { text: "tests/test_chunker.py::test_chunker_preserves_metadata", status: "PASSED" },
  { text: "tests/test_generator.py::test_generate_returns_string", status: "PASSED" },
  { text: "tests/test_generator.py::test_stream_yields_tokens", status: "PASSED" },
  { text: "tests/test_loader.py::test_load_pdf_returns_pages", status: "PASSED" },
  { text: "tests/test_loader.py::test_load_docx_text_contains_content", status: "PASSED" },
  { text: "tests/test_pipeline.py::test_query_returns_chat_response", status: "PASSED" },
  { text: "tests/test_retriever.py::test_rrf_merge_deduplicates", status: "PASSED" },
  { text: "tests/test_retriever.py::test_retriever_returns_results", status: "PASSED" },
];

export const Scene6Quality: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  const titleOpacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });

  // Feedback demo
  const fbOpacity = interpolate(frame, [10, 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const thumbScale = spring({ frame: Math.max(0, frame - 40), fps: 30, config: { damping: 10, stiffness: 150 } });
  const toastOpacity = interpolate(frame, [55, 65, 105, 115], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Test lines appear
  const testLinesStart = 80;
  const passed49Scale = spring({ frame: Math.max(0, frame - testLinesStart + TEST_LINES.length * 8 + 10), fps: 30, config: { damping: 12, stiffness: 100 } });
  const passed49Opacity = interpolate(
    frame,
    [testLinesStart + TEST_LINES.length * 8 + 10, testLinesStart + TEST_LINES.length * 8 + 22],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <div style={{
      width, height, background: COLORS.bg,
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
      gap: 24,
    }}>
      <div style={{ opacity: titleOpacity }}>
        <h2 style={{ color: COLORS.textPrimary, fontSize: 34, margin: 0, textAlign: "center", fontFamily: "Inter, sans-serif" }}>
          品質へのこだわり
        </h2>
      </div>

      <div style={{ display: "flex", gap: 32, alignItems: "flex-start" }}>
        {/* Feedback panel */}
        <div style={{
          opacity: fbOpacity, width: 380,
          background: COLORS.bgCard, borderRadius: 16,
          border: `1px solid ${COLORS.border}`, padding: 24,
        }}>
          <h3 style={{ color: COLORS.textSecondary, fontSize: 15, margin: "0 0 16px 0" }}>ユーザーフィードバック収集</h3>
          <div style={{ color: COLORS.textPrimary, fontSize: 15, marginBottom: 20, lineHeight: 1.6 }}>
            「有給休暇の申請手続きを教えてください」
            <div style={{ color: COLORS.textSecondary, fontSize: 13, marginTop: 4 }}>
              → 3件の引用元付き回答を生成
            </div>
          </div>
          <div style={{ display: "flex", gap: 12 }}>
            <div style={{
              transform: `scale(${thumbScale})`,
              background: "rgba(16,185,129,0.2)", border: `2px solid ${COLORS.green}`,
              borderRadius: 10, padding: "10px 20px",
              color: COLORS.green, fontWeight: 700, fontSize: 16,
              boxShadow: `0 0 20px rgba(16,185,129,0.4)`,
            }}>
              👍 役立った
            </div>
            <div style={{
              background: "rgba(239,68,68,0.1)", border: `1px solid ${COLORS.border}`,
              borderRadius: 10, padding: "10px 20px",
              color: COLORS.textSecondary, fontSize: 16,
            }}>
              👎 的外れ
            </div>
          </div>

          {/* Toast */}
          <div style={{
            opacity: toastOpacity,
            marginTop: 16, background: COLORS.green,
            borderRadius: 8, padding: "10px 16px",
            color: "#fff", fontSize: 14, fontWeight: 600,
          }}>
            ✅ フィードバックありがとうございます！
          </div>
        </div>

        {/* Test terminal */}
        <div style={{
          width: 540, background: "#0d1117",
          borderRadius: 16, border: `1px solid ${COLORS.border}`,
          overflow: "hidden",
        }}>
          <div style={{
            background: "#161b22", padding: "10px 16px",
            borderBottom: `1px solid ${COLORS.border}`,
            display: "flex", alignItems: "center", gap: 8,
          }}>
            <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#ef4444" }} />
            <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#f59e0b" }} />
            <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#10b981" }} />
            <span style={{ color: COLORS.textSecondary, fontSize: 13, marginLeft: 8, fontFamily: "monospace" }}>
              $ py -m pytest tests/ -v
            </span>
          </div>

          <div style={{ padding: 16, fontFamily: "monospace", fontSize: 13 }}>
            {TEST_LINES.map((line, i) => {
              const lineOpacity = interpolate(
                frame,
                [testLinesStart + i * 8, testLinesStart + i * 8 + 10],
                [0, 1],
                { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
              );
              return (
                <div key={i} style={{ opacity: lineOpacity, marginBottom: 3, display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: COLORS.textSecondary, fontSize: 12 }}>{line.text}</span>
                  <span style={{ color: COLORS.green, fontWeight: 700, marginLeft: 8 }}>{line.status}</span>
                </div>
              );
            })}

            <div style={{
              opacity: passed49Opacity,
              transform: `scale(${passed49Scale})`,
              marginTop: 16, padding: "10px 16px",
              background: "rgba(16,185,129,0.15)",
              border: `1px solid ${COLORS.green}`,
              borderRadius: 8,
              color: COLORS.green, fontWeight: 700, fontSize: 16,
              textAlign: "center",
            }}>
              ✅ 49 passed in 6.14s
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
