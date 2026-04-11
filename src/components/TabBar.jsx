const TABS = [
  {
    id: "sentimen", label: "Sentimen",
    icon: (
      <svg viewBox="0 0 24 24" fill="currentColor" width="15" height="15">
        <rect x="3" y="12" width="4" height="9" rx="1"/>
        <rect x="10" y="7" width="4" height="14" rx="1"/>
        <rect x="17" y="3" width="4" height="18" rx="1"/>
      </svg>
    ),
  },
  {
    id: "pasar", label: "Pasar",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" width="15" height="15">
        <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
        <polyline points="16 7 22 7 22 13"/>
      </svg>
    ),
  },
  {
    id: "multimodal", label: "Multimodal",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="15" height="15">
        <rect x="3"  y="3"  width="7" height="7" rx="1"/>
        <rect x="14" y="3"  width="7" height="7" rx="1"/>
        <rect x="3"  y="14" width="7" height="7" rx="1"/>
        <rect x="14" y="14" width="7" height="7" rx="1"/>
      </svg>
    ),
  },
]

export default function TabBar({ activeTab, onTabChange, dark }) {
  return (
    <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
      {TABS.map(tab => {
        const active = activeTab === tab.id
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "8px 16px",
              borderRadius: 10,
              border: active ? "none" : `1px solid ${dark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.12)"}`,
              background: active
                ? "linear-gradient(135deg, #e05a2b, #c44a1e)"
                : dark ? "#1c1c1e" : "#ffffff",
              color: active ? "#ffffff" : dark ? "#9ca3af" : "#6b7280",
              fontSize: 13,
              fontWeight: 600,
              fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
              cursor: "pointer",
              boxShadow: active ? "0 4px 14px rgba(224,90,43,0.35)" : "none",
              transition: "all 0.2s ease",
              whiteSpace: "nowrap",
            }}
          >
            {tab.icon}
            {tab.label}
          </button>
        )
      })}
    </div>
  )
}