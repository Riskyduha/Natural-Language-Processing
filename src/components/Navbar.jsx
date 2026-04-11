export default function Navbar({ dark, onToggleDark }) {
  return (
    <nav style={{
      background: dark ? "#161618" : "#ffffff",
      borderBottom: `1px solid ${dark ? "rgba(255,255,255,0.07)" : "rgba(0,0,0,0.08)"}`,
      position: "sticky",
      top: 0,
      zIndex: 100,
    }}>
      <div style={{
        maxWidth: 860,
        margin: "0 auto",
        padding: "0 20px",
        height: 60,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
      }}>

        {/* Logo + Title */}
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 36, height: 36,
            borderRadius: 9,
            background: "linear-gradient(135deg, #e05a2b, #c44a1e)",
            display: "flex", alignItems: "center", justifyContent: "center",
            boxShadow: "0 4px 12px rgba(224,90,43,0.4)",
            flexShrink: 0,
          }}>
            {/* Bar chart icon */}
            <svg viewBox="0 0 24 24" fill="white" width="18" height="18">
              <rect x="3"  y="12" width="4" height="9" rx="1"/>
              <rect x="10" y="7"  width="4" height="14" rx="1"/>
              <rect x="17" y="3"  width="4" height="18" rx="1"/>
            </svg>
          </div>
          <div>
            <div style={{
              fontFamily: "'Sora', 'Segoe UI', sans-serif",
              fontWeight: 700,
              fontSize: 15,
              color: dark ? "#f3f4f6" : "#111827",
              lineHeight: 1.3,
            }}>
              Analisis Sentimen
            </div>
            <div style={{ fontSize: 11, color: dark ? "#9ca3af" : "#6b7280", lineHeight: 1 }}>
              Prediksi Pasar AI
            </div>
          </div>
        </div>

        {/* Toggle dark/light */}
        <button
          onClick={onToggleDark}
          style={{
            background: "none", border: "none", cursor: "pointer",
            color: dark ? "#f59e0b" : "#6b7280",
            padding: 8, borderRadius: 8,
            display: "flex", alignItems: "center", justifyContent: "center",
          }}
          title={dark ? "Light mode" : "Dark mode"}
        >
          {dark ? (
            /* Sun */
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20">
              <circle cx="12" cy="12" r="5"/>
              <line x1="12" y1="1"  x2="12" y2="3"/>
              <line x1="12" y1="21" x2="12" y2="23"/>
              <line x1="4.22" y1="4.22"   x2="5.64" y2="5.64"/>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
              <line x1="1"  y1="12" x2="3"  y2="12"/>
              <line x1="21" y1="12" x2="23" y2="12"/>
              <line x1="4.22" y1="19.78"  x2="5.64" y2="18.36"/>
              <line x1="18.36" y1="5.64"  x2="19.78" y2="4.22"/>
            </svg>
          ) : (
            /* Moon */
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
          )}
        </button>

      </div>
    </nav>
  )
}