import { useNavigate, useLocation } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

const navBtnStyle = (active) => ({
    width: "100%",
    padding: 10,
    marginBottom: 10,
    background: active ? "#4338ca" : "#4f46e5",
    color: "white",
    border: "none",
    borderRadius: 8,
    cursor: "pointer",
    fontWeight: active ? "bold" : "normal"
})

export default function Sidebar() {
    const navigate = useNavigate()
    const location = useLocation()
    const { role } = useAuth()

    return (
        <div style={{
            width: 260,
            borderRight: "1px solid #eee",
            padding: 15,
            background: "#fafafa"
        }}>
            <button
                onClick={() => navigate("/")}
                style={navBtnStyle(location.pathname === "/")}
            >
                🗓️ Calendrier
            </button>

            {role === "admin" && (
                <button
                    onClick={() => navigate("/admin")}
                    style={navBtnStyle(location.pathname === "/admin")}
                >
                    ⚙️ Admin
                </button>
            )}
        </div>
    )
}