import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { COLORS } from "../components/colors";

const Node: React.FC<{ label: string; icon: string; x: number; y: number; delay: number; color?: string }> = ({
  label, icon, x, y, delay, color = COLORS.accent,
}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [delay, delay + 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const scale = interpolate(frame, [delay, delay + 15], [0.7, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <div style={{
      position: "absolute", left: x, top: y,
      opacity, transform: `scale(${scale})`,
      display: "flex", flexDirection: "column", alignItems: "center",
      width: 130,
    }}>
      <div style={{
        width: 80, height: 80, borderRadius: 16,
        background: `${color}22`, border: `2px solid ${color}`,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 34,
      }}>{icon}</div>
      <div style={{
        marginTop: 8, fontSize: 13, color: COLORS.textPrimary,
        textAlign: "center", fontWeight: 600, fontFamily: "Inter, sans-serif",
      }}>{label}</div>
    </div>
  );
};

const Arrow: React.FC<{ x1: number; y1: number; x2: number; y2: number; delay: number; label?: string }> = ({ x1, y1, x2, y2, delay, label }) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [delay, delay + 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const cx = (x1 + x2) / 2;
  const cy = (y1 + y2) / 2;
  const len = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
  const dashOffset = len * (1 - progress);

  return (
    <g>
      <defs>
        <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="6" refY="3" orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill={COLORS.accent} />
        </marker>
      </defs>
      <line
        x1={x1} y1={y1} x2={x2} y2={y2}
        stroke={COLORS.accent} strokeWidth="2"
        strokeDasharray={len} strokeDashoffset={dashOffset}
        markerEnd="url(#arrowhead)"
      />
      {label && (
        <text x={cx} y={cy - 8} fill={COLORS.textSecondary} fontSize="12" textAnchor="middle">{label}</text>
      )}
    </g>
  );
};

export const Scene5Architecture: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  const titleOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });

  const techBadges = [
    { text: "FastAPI", color: COLORS.green, delay: 120 },
    { text: "LangChain", color: COLORS.accent, delay: 130 },
    { text: "Chroma DB", color: "#f59e0b", delay: 140 },
    { text: "Hybrid Search", color: "#ec4899", delay: 150 },
    { text: "Claude / GPT", color: COLORS.accentLight, delay: 160 },
  ];

  return (
    <div style={{
      width, height, background: COLORS.bg,
      display: "flex", flexDirection: "column", alignItems: "center",
    }}>
      <div style={{ opacity: titleOpacity, marginTop: 48, marginBottom: 16, textAlign: "center" }}>
        <h2 style={{ color: COLORS.textPrimary, fontSize: 34, margin: 0, fontFamily: "Inter, sans-serif" }}>
          技術スタック
        </h2>
        <p style={{ color: COLORS.textSecondary, fontSize: 18, margin: "8px 0 0 0" }}>RAG Pipeline Architecture</p>
      </div>

      {/* Architecture diagram */}
      <div style={{ position: "relative", width: 960, height: 340 }}>
        {/* SVG arrows */}
        <svg style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}>
          <Arrow x1={195} y1={100} x2={295} y2={100} delay={60} label="질문" />
          <Arrow x1={460} y1={100} x2={545} y2={100} delay={75} />
          <Arrow x1={700} y1={100} x2={780} y2={100} delay={90} />
          <Arrow x1={545} y1={180} x2={545} y2={240} delay={100} label="検索" />
          <Arrow x1={700} y1={260} x2={620} y2={180} delay={110} />
        </svg>

        {/* Nodes */}
        <Node label="Browser" icon="🌐" x={65} y={40} delay={15} color={COLORS.textSecondary} />
        <Node label="Streamlit UI" icon="🖥️" x={295} y={40} delay={25} color={COLORS.green} />
        <Node label="FastAPI" icon="⚡" x={545} y={40} delay={35} color={COLORS.accent} />
        <Node label="LLM (Claude)" icon="🤖" x={795} y={40} delay={45} color={COLORS.accentLight} />
        <Node label="Chroma\nVector DB" icon="🗄️" x={480} y={200} delay={55} color="#f59e0b" />
        <Node label="BM25 Search" icon="🔍" x={660} y={200} delay={65} color="#ec4899" />
      </div>

      {/* Tech badges */}
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", justifyContent: "center", marginTop: 8 }}>
        {techBadges.map((b, i) => (
          <div key={i} style={{
            opacity: interpolate(frame, [b.delay, b.delay + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            background: `${b.color}22`, border: `1px solid ${b.color}`,
            borderRadius: 999, padding: "6px 18px",
            color: b.color, fontWeight: 700, fontSize: 15, fontFamily: "Inter, sans-serif",
          }}>
            {b.text}
          </div>
        ))}
      </div>

      {/* Code snippet */}
      <div style={{
        marginTop: 24,
        opacity: interpolate(frame, [170, 185], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        background: "#0d1117", borderRadius: 12,
        border: `1px solid ${COLORS.border}`, padding: "16px 24px",
        fontFamily: "monospace", fontSize: 14, lineHeight: 1.6,
        width: 680,
      }}>
        <span style={{ color: "#7c3aed" }}>def</span>
        <span style={{ color: "#60a5fa" }}> hybrid_search</span>
        <span style={{ color: COLORS.textSecondary }}>(query, top_k=5):</span>
        <br />
        <span style={{ color: COLORS.textSecondary }}>    vector_hits = </span>
        <span style={{ color: COLORS.green }}>vectorstore.similarity_search</span>
        <span style={{ color: COLORS.textSecondary }}>(query)</span>
        <br />
        <span style={{ color: COLORS.textSecondary }}>    bm25_hits = </span>
        <span style={{ color: COLORS.green }}>bm25.get_top_n</span>
        <span style={{ color: COLORS.textSecondary }}>(query, corpus)</span>
        <br />
        <span style={{ color: COLORS.textSecondary }}>    </span>
        <span style={{ color: "#7c3aed" }}>return </span>
        <span style={{ color: COLORS.green }}>rrf_merge</span>
        <span style={{ color: COLORS.textSecondary }}>(vector_hits, bm25_hits, top_k)</span>
      </div>
    </div>
  );
};
