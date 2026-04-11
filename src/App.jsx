import { useState } from "react"
import Navbar from "./components/Navbar"
import TabBar from "./components/TabBar"
import SentimenPanel from "./components/SentimenPanel"
import PasarPanel from "./components/PasarPanel"
import MultimodalPanel from "./components/MultimodalPanel"

export default function App() {
  const [dark, setDark] = useState(true)
  const [activeTab, setActiveTab] = useState("sentimen")

  return (
    <div style={{ minHeight: "100vh", background: dark ? "#0f0f11" : "#f1f5f9" }}>

      <Navbar dark={dark} onToggleDark={() => setDark(d => !d)} />

      <div style={{ maxWidth: 860, margin: "0 auto", padding: "32px 20px 60px" }}>

        <TabBar activeTab={activeTab} onTabChange={setActiveTab} dark={dark} />

        {activeTab === "sentimen"   && <SentimenPanel   dark={dark} />}
        {activeTab === "pasar"      && <PasarPanel      dark={dark} />}
        {activeTab === "multimodal" && <MultimodalPanel dark={dark} />}

        {/* Footer */}
        <div style={{
          marginTop: 20,
          borderRadius: 16,
          padding: "20px 24px",
          textAlign: "center",
          background: dark ? "#161618" : "#ffffff",
          border: `1px solid ${dark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.08)"}`,
        }}>
          <p style={{ fontSize: 13, color: dark ? "#9ca3af" : "#6b7280", marginBottom: 6 }}>
            🤖 Platform analisis sentimen AI untuk prediksi tren pasar saham
          </p>
          <p style={{ fontSize: 12, color: dark ? "#4b5563" : "#9ca3af" }}>
            Disclaimer: Hasil analisis bersifat prediktif dan bukan jaminan untuk keputusan investasi
          </p>
        </div>

      </div>
    </div>
  )
}