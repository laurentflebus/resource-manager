import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

export default function Navbar() {
    const navigate = useNavigate()
    const { role, logout } = useAuth()

    return (
        <div style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "10px 20px",
            borderBottom: "1px solid #eee",
            background: "white"
        }}>

            {/* LEFT */}
            <div style={{ fontWeight: "bold" }}>
                🗂️ Resource Manager
            </div>

            {/* RIGHT */}
            <div style={{ display: "flex", gap: 15, alignItems: "center" }}>
                <span>👤 {role}</span>

                <button
                    onClick={logout}
                    style={{
                        background: "#ef4444",
                        color: "white",
                        border: "none",
                        padding: "6px 10px",
                        borderRadius: 6,
                        cursor: "pointer"
                    }}
                >
                    Logout
                </button>
            </div>

        </div>
    )
}