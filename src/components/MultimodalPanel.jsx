export default function MultimodalPanel({ dark }) {
  const card   = dark ? "#1c1c1e" : "#ffffff"
  const border = dark ? "rgba(255,255,255,0.07)" : "rgba(0,0,0,0.08)"
  const textMain = dark ? "#f3f4f6" : "#111827"
  const textSub  = dark ? "#9ca3af" : "#6b7280"

  return (
    <div style={{
      borderRadius: 16,
      padding: 28,
      background: card,
      border: `1px solid ${border}`,
      boxShadow: dark ? "0 4px 40px rgba(0,0,0,0.35)" : "0 4px 20px rgba(0,0,0,0.07)",
    }}>
      <h2 style={{ fontFamily: "'Sora', 'Segoe UI', sans-serif", fontWeight: 700, fontSize: 22, color: textMain, marginBottom: 6 }}>
        Multimodal
      </h2>
      <p style={{ fontSize: 13, color: textSub, marginBottom: 0 }}>
        Analisis dari berbagai sumber data sekaligus
      </p>

      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "60px 0", gap: 14 }}>
        <div style={{
          width: 56, height: 56, borderRadius: 14,
          background: "rgba(224,90,43,0.1)",
          border: "1px solid rgba(224,90,43,0.25)",
          display: "flex", alignItems: "center", justifyContent: "center",
        }}>
          <svg viewBox="0 0 24 24" fill="none" stroke="#e05a2b" strokeWidth="2" width="24" height="24">
            <rect x="3"  y="3"  width="7" height="7" rx="1"/>
            <rect x="14" y="3"  width="7" height="7" rx="1"/>
            <rect x="3"  y="14" width="7" height="7" rx="1"/>
            <rect x="14" y="14" width="7" height="7" rx="1"/>
          </svg>
        </div>
        <p style={{ fontWeight: 600, fontSize: 15, color: textMain, fontFamily: "'Sora', sans-serif" }}>
          Segera Hadir
        </p>
        <p style={{ fontSize: 13, color: textSub, textAlign: "center", maxWidth: 280 }}>
          Fitur analisis multimodal (teks + gambar + data numerik) sedang dalam pengembangan.
        </p>
      </div>
    </div>
  )
}