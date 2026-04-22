import { useEffect, useState } from "react"

export default function AdminDashboard() {

    const [stats, setStats] = useState({
        reservations: 0,
        rooms: 0,
        equipments: 0
    })

    const [reservations, setReservations] = useState([])

    const token = localStorage.getItem("token")

    useEffect(() => {
        fetchStats()
        fetchReservations()
    }, [])

    const fetchStats = async () => {
        try {
            const [reservationsRes, roomsRes, equipmentsRes] = await Promise.all([
                fetch("http://127.0.0.1:8000/reservations", {
                    headers: { Authorization: `Bearer ${token}` }
                }),
                fetch("http://127.0.0.1:8000/rooms", {
                    headers: { Authorization: `Bearer ${token}` }
                }),
                fetch("http://127.0.0.1:8000/equipments", {
                    headers: { Authorization: `Bearer ${token}` }
                })
            ])

            const reservations = await reservationsRes.json()
            const rooms = await roomsRes.json()
            const equipments = await equipmentsRes.json()

            setStats({
                reservations: reservations.length || 0,
                rooms: rooms.length || 0,
                equipments: equipments.length || 0
            })
        } catch (error) {
            console.error("Erreur lors de la récupération des statistiques :", error)
        }

    }


    const fetchReservations = async () => {
        const res = await fetch("http://127.0.0.1:8000/reservations", {
            headers: {
                Authorization: `Bearer ${token}`
            }
        })

        const data = await res.json()
        setReservations(data)
    }

    const handleDelete = async (id) => {
        await fetch(`http://127.0.0.1:8000/reservations/${id}`, {
            method: "DELETE",
            headers: {
                Authorization: `Bearer ${token}`
            }
        })
        fetchStats()
        fetchReservations()
    }

    return (
        <div style={{ padding: 20 }}>
            <h1>🛠️ Admin Dashboard</h1>

            <div style={{ display: "flex", gap: 20, marginTop: 20 }}>
                <Card title="Réservations" value={stats.reservations} color="#4f46e5" />
                <Card title="Salles" value={stats.rooms} color="#16a34a" />
                <Card title="Équipements" value={stats.equipments} color="#f59e0b" />
            </div>

            <h3 style={{ marginTop: 30 }}>Réservations</h3>

            <table style={{
                width: "100%",
                marginTop: 10,
                borderCollapse: "collapse"
            }}>
                <thead>
                    <tr style={{ background: "#f3f4f6" }}>
                        <th>ID</th>
                        <th>Type</th>
                        <th>Nom</th>
                        <th>Début</th>
                        <th>Fin</th>
                        <th>Action</th>
                    </tr>
                </thead>

                <tbody>
                    {reservations.length === 0 ? (
                        <tr>
                            <td
                                colSpan="6"
                                style={{
                                    textAlign: "center",
                                    padding: 20,
                                    color: "#6b7280"
                                }}
                            >
                                📭 Aucune réservation pour le moment
                            </td>
                        </tr>
                    ) : (
                        reservations.map(r => (
                            <tr key={r.id} style={{ textAlign: "center", borderBottom: "1px solid #eee" }}>
                                <td>{r.id}</td>

                                <td>{r.room_id ? "Salle" : "Matériel"}</td>

                                <td>
                                    {r.room_name || r.equipment_name || "—"}
                                </td>

                                <td>{new Date(r.start_time).toLocaleString()}</td>
                                <td>{new Date(r.end_time).toLocaleString()}</td>

                                <td>
                                    <button
                                        onClick={() => handleDelete(r.id)}
                                        style={{
                                            background: "#ef4444",
                                            color: "white",
                                            border: "none",
                                            padding: "5px 8px",
                                            borderRadius: 4,
                                            cursor: "pointer"
                                        }}
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))
                    )}
                </tbody>
            </table>
        </div>
    )
}
function Card({ title, value, color }) {
    return (
        <div style={{
            flex: 1,
            background: color,
            padding: 20,
            borderRadius: 12,
            color: "white",
            textAlign: "center"
        }}>
            <h3>{title}</h3>
            <p style={{ fontSize: 24, fontWeight: "bold" }}>{value}</p>
        </div>
    )
}