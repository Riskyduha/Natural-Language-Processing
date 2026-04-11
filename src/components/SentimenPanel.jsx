import { useState } from "react"
import ResultCard from "./ResultCard"

const API_BASE = "http://localhost:5000"

export default function SentimenPanel({ dark }) {
  const [text, setText]     = useState("")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]   = useState("")

  const card       = dark ? "#1c1c1e" : "#ffffff"
  const border     = dark ? "rgba(255,255,255,0.07)" : "rgba(0,0,0,0.08)"
  const textMain   = dark ? "#f3f4f6" : "#111827"
  const textSub    = dark ? "#9ca3af" : "#6b7280"
  const inputBg    = dark ? "#111113" : "#f9fafb"
  const inputBorder = dark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.12)"

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!text.trim()) return
    setLoading(true); setError(""); setResult(null)
    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      setResult(await res.json())
    } catch (e) {
      setError(e.message || "Gagal terhubung ke server. Pastikan backend berjalan di port 5000.")
    } finally {
      setLoading(false)
    }
  }

  const canSubmit = !loading && text.trim().length > 0

  return (
    <div style={{
      borderRadius: 16,
      padding: 28,
      background: card,
      border: `1px solid ${border}`,
      boxShadow: dark ? "0 4px 40px rgba(0,0,0,0.35)" : "0 4px 20px rgba(0,0,0,0.07)",
    }}>

      {/* Judul */}
      <h2 style={{ fontFamily: "'Sora', 'Segoe UI', sans-serif", fontWeight: 700, fontSize: 22, color: textMain, marginBottom: 6 }}>
        Analisis Sentimen
      </h2>
      <p style={{ fontSize: 13, color: textSub, marginBottom: 24 }}>
        Analisis sentimen teks berita atau komentar saham secara real-time
      </p>

      <form onSubmit={handleSubmit}>
        {/* Label */}
        <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: textMain, marginBottom: 8 }}>
          Berita / Teks
        </label>

        {/* Textarea */}
        <textarea
          rows={6}
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder="Masukkan teks berita atau komentar saham..."
          style={{
            display: "block",
            width: "100%",
            boxSizing: "border-box",
            padding: "12px 14px",
            borderRadius: 10,
            border: `1px solid ${inputBorder}`,
            background: inputBg,
            color: textMain,
            fontSize: 14,
            fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
            resize: "vertical",
            outline: "none",
            lineHeight: 1.6,
          }}
          onFocus={e => e.target.style.borderColor = "#e05a2b"}
          onBlur={e => e.target.style.borderColor = inputBorder}
        />

        {/* Error */}
        {error && (
          <div style={{
            marginTop: 10,
            padding: "10px 14px",
            borderRadius: 8,
            background: "rgba(239,68,68,0.1)",
            border: "1px solid rgba(239,68,68,0.25)",
            color: "#f87171",
            fontSize: 13,
          }}>
            ⚠️ {error}
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={!canSubmit}
          style={{
            display: "block",
            width: "100%",
            marginTop: 14,
            padding: "13px 0",
            borderRadius: 10,
            border: "none",
            background: canSubmit
              ? "linear-gradient(135deg, #e05a2b, #c44a1e)"
              : dark ? "#2a1a12" : "#e5d0c8",
            color: canSubmit ? "#ffffff" : dark ? "#6b3520" : "#a07060",
            fontSize: 14,
            fontWeight: 600,
            fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
            cursor: canSubmit ? "pointer" : "not-allowed",
            boxShadow: canSubmit ? "0 4px 18px rgba(224,90,43,0.35)" : "none",
            transition: "all 0.2s",
          }}
        >
          {loading ? "Menganalisis..." : "Analisis"}
        </button>
      </form>

      {result && <ResultCard result={result} />}
    </div>
  )
}