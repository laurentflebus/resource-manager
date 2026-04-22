import { useNavigate } from "react-router-dom"

export default function Sidebar() {

    const navigate = useNavigate()
    const role = localStorage.getItem("role")

    return (
        <div style={{
            width: 260,
            borderRight: "1px solid #eee",
            padding: 15,
            background: "#fafafa"
        }}>
            <button
                onClick={() => navigate("/")}
                style={{
                    width: "100%",
                    padding: 10,
                    marginBottom: 10,
                    background: "#4f46e5",
                    color: "white",
                    border: "none",
                    borderRadius: 8,
                    cursor: "pointer"
                }}
            >
                🗓️ Calendrier
            </button>
            {role === "admin" && (
                <button
                    onClick={() => navigate("/admin")}
                    style={{
                        width: "100%",
                        padding: 10,
                        marginBottom: 20,
                        background: "#111827",
                        color: "white",
                        border: "none",
                        borderRadius: 8,
                        cursor: "pointer"
                    }}
                >
                    ⚙️ Admin
                </button>
            )}
            <button style={{
                width: "100%",
                padding: 10,
                background: "#16a34a",
                color: "white",
                border: "none",
                borderRadius: 8,
                marginBottom: 20,
                cursor: "pointer"
            }}>
                ➕ Nouvelle réservation
            </button>

            {/* FILTERS */}
            <div>
                <h4>Filtres</h4>

                <select style={{ width: "100%", marginBottom: 10 }}>
                    <option>Toutes les salles</option>
                </select>

                <select style={{ width: "100%" }}>
                    <option>Tout le matériel</option>
                </select>
            </div>
        </div>
    )
}