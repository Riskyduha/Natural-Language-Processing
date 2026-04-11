import { useState } from "react"
import ResultCard from "./ResultCard"

const API_BASE = "http://localhost:5000"

export default function PasarPanel({ dark }) {
  const [texts, setTexts]     = useState(["", "", ""])
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState("")

  const card        = dark ? "#1c1c1e" : "#ffffff"
  const border      = dark ? "rgba(255,255,255,0.07)" : "rgba(0,0,0,0.08)"
  const textMain    = dark ? "#f3f4f6" : "#111827"
  const textSub     = dark ? "#9ca3af" : "#6b7280"
  const inputBg     = dark ? "#111113" : "#f9fafb"
  const inputBorder = dark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.12)"

  const updateText = (i, v) => setTexts(prev => prev.map((t, idx) => idx === i ? v : t))

  const handleSubmit = async (e) => {
    e.preventDefault()
    const valid = texts.filter(t => t.trim())
    if (!valid.length) return
    setLoading(true); setError(""); setResults([])
    try {
      const res = await fetch(`${API_BASE}/predict/batch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texts: valid }),
      })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()
      setResults(data.results)
    } catch (e) {
      setError(e.message || "Gagal terhubung ke server.")
    } finally {
      setLoading(false)
    }
  }

  const canSubmit = !loading && texts.some(t => t.trim())

  // Summary dari results
  const summary = results.reduce((acc, r) => {
    acc[r.label] = (acc[r.label] || 0) + 1
    return acc
  }, {})

  return (
    <div style={{
      borderRadius: 16,
      padding: 28,
      background: card,
      border: `1px solid ${border}`,
      boxShadow: dark ? "0 4px 40px rgba(0,0,0,0.35)" : "0 4px 20px rgba(0,0,0,0.07)",
    }}>

      <h2 style={{ fontFamily: "'Sora', 'Segoe UI', sans-serif", fontWeight: 700, fontSize: 22, color: textMain, marginBottom: 6 }}>
        Analisis Pasar
      </h2>
      <p style={{ fontSize: 13, color: textSub, marginBottom: 24 }}>
        Analisis beberapa berita sekaligus untuk membaca tren pasar
      </p>

      <form onSubmit={handleSubmit}>
        {texts.map((t, i) => (
          <div key={i} style={{ marginBottom: 16 }}>
            <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: textSub, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 6 }}>
              Berita #{i + 1}
            </label>
            <textarea
              rows={3}
              value={t}
              onChange={e => updateText(i, e.target.value)}
              placeholder={`Masukkan berita atau komentar #${i + 1}...`}
              style={{
                display: "block",
                width: "100%",
                boxSizing: "border-box",
                padding: "11px 14px",
                borderRadius: 10,
                border: `1px solid ${inputBorder}`,
                background: inputBg,
                color: textMain,
                fontSize: 13,
                fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
                resize: "vertical",
                outline: "none",
                lineHeight: 1.6,
              }}
              onFocus={e => e.target.style.borderColor = "#e05a2b"}
              onBlur={e => e.target.style.borderColor = inputBorder}
            />
          </div>
        ))}

        {error && (
          <div style={{
            marginBottom: 12, padding: "10px 14px", borderRadius: 8,
            background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.25)",
            color: "#f87171", fontSize: 13,
          }}>
            ⚠️ {error}
          </div>
        )}

        <button
          type="submit"
          disabled={!canSubmit}
          style={{
            display: "block",
            width: "100%",
            padding: "13px 0",
            borderRadius: 10,
            border: "none",
            background: canSubmit ? "linear-gradient(135deg, #e05a2b, #c44a1e)" : dark ? "#2a1a12" : "#e5d0c8",
            color: canSubmit ? "#ffffff" : dark ? "#6b3520" : "#a07060",
            fontSize: 14,
            fontWeight: 600,
            fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
            cursor: canSubmit ? "pointer" : "not-allowed",
            boxShadow: canSubmit ? "0 4px 18px rgba(224,90,43,0.35)" : "none",
          }}
        >
          {loading ? "Menganalisis..." : "Analisis Semua"}
        </button>
      </form>

      {/* Results */}
      {results.length > 0 && (
        <div style={{ marginTop: 24 }}>
          {/* Summary boxes */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginBottom: 20 }}>
            {[
              ["positive", "Positif",  "#22c55e"],
              ["neutral",  "Netral",   "#f59e0b"],
              ["negative", "Negatif",  "#ef4444"],
            ].map(([k, lab, col]) => (
              <div key={k} style={{
                borderRadius: 10, padding: "12px 0", textAlign: "center",
                background: `${col}12`, border: `1px solid ${col}30`,
              }}>
                <p style={{ fontSize: 24, fontWeight: 700, color: col, fontFamily: "'Sora', sans-serif" }}>
                  {summary[k] || 0}
                </p>
                <p style={{ fontSize: 12, color: col, marginTop: 2 }}>{lab}</p>
              </div>
            ))}
          </div>

          {results.map((r, i) => (
            <div key={i} style={{ marginBottom: 8 }}>
              <p style={{ fontSize: 11, fontWeight: 600, color: textSub, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4 }}>
                Berita #{i + 1}
              </p>
              <ResultCard result={r} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}