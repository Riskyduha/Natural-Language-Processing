const SENTIMENT = {
  positive: { label: "Positif",  color: "#22c55e", bg: "rgba(34,197,94,0.08)",  border: "rgba(34,197,94,0.25)",  emoji: "📈", desc: "Sentimen pasar cenderung bullish" },
  neutral:  { label: "Netral",   color: "#f59e0b", bg: "rgba(245,158,11,0.08)", border: "rgba(245,158,11,0.25)", emoji: "➡️", desc: "Sentimen pasar cenderung sideways" },
  negative: { label: "Negatif",  color: "#ef4444", bg: "rgba(239,68,68,0.08)",  border: "rgba(239,68,68,0.25)",  emoji: "📉", desc: "Sentimen pasar cenderung bearish" },
}

function ProbBar({ label, value, color }) {
  const pct = (value * 100).toFixed(1)
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
        <span style={{ fontSize: 12, color: "#9ca3af", fontWeight: 500 }}>{label}</span>
        <span style={{ fontSize: 12, color, fontWeight: 600 }}>{pct}%</span>
      </div>
      <div style={{ height: 6, borderRadius: 99, background: "rgba(255,255,255,0.07)", overflow: "hidden" }}>
        <div style={{
          height: "100%", borderRadius: 99, background: color,
          width: `${pct}%`, transition: "width 0.7s ease",
        }}/>
      </div>
    </div>
  )
}

export default function ResultCard({ result }) {
  const cfg = SENTIMENT[result.label] || SENTIMENT.neutral
  const confidencePct = (result.confidence * 100).toFixed(1)

  return (
    <div style={{
      marginTop: 20,
      borderRadius: 14,
      padding: 20,
      background: cfg.bg,
      border: `1px solid ${cfg.border}`,
    }}>

      {/* Header baris */}
      <div style={{ display: "flex", alignItems: "flex-start", gap: 14, marginBottom: 18 }}>
        <span style={{ fontSize: 36, lineHeight: 1, flexShrink: 0 }}>{cfg.emoji}</span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <p style={{ fontSize: 11, color: "#9ca3af", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 2 }}>
            Hasil Analisis
          </p>
          <p style={{ fontSize: 22, fontWeight: 700, color: cfg.color, fontFamily: "'Sora', sans-serif", marginBottom: 2 }}>
            {cfg.label}
          </p>
          <p style={{ fontSize: 12, color: "#9ca3af" }}>{cfg.desc}</p>
        </div>
        <div style={{ textAlign: "right", flexShrink: 0 }}>
          <p style={{ fontSize: 11, color: "#9ca3af", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 2 }}>
            Confidence
          </p>
          <p style={{ fontSize: 26, fontWeight: 700, color: cfg.color, fontFamily: "'Sora', sans-serif" }}>
            {confidencePct}%
          </p>
        </div>
      </div>

      {/* Probability bars */}
      <div style={{ borderTop: "1px solid rgba(255,255,255,0.08)", paddingTop: 16 }}>
        <p style={{ fontSize: 11, color: "#6b7280", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 12 }}>
          Distribusi Probabilitas
        </p>
        <ProbBar label="Positif" value={result.probabilities?.positive ?? 0} color="#22c55e" />
        <ProbBar label="Netral"  value={result.probabilities?.neutral  ?? 0} color="#f59e0b" />
        <ProbBar label="Negatif" value={result.probabilities?.negative ?? 0} color="#ef4444" />
      </div>

    </div>
  )
}