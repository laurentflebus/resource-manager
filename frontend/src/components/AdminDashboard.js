import { useEffect, useState } from "react"

export default function AdminDashboard() {

    const [reservations, setReservations] = useState([])
    const token = localStorage.getItem("token")

    useEffect(() => {
        fetchReservations()
    }, [])

    const fetchReservations = async () => {
        const res = await fetch("http://127.0.0.1:8000/reservations", {
            headers: {
                Authorization: `Bearer ${token}`
            }
        })

        const data = await res.json()
        setReservations(data)
    }

    return (
        <div style={{ padding: 20 }}>
            <h1>🛠️ Admin Dashboard</h1>

            <h3>Réservations</h3>

            <table style={{ width: "100%", marginTop: 20 }}>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Début</th>
                        <th>Fin</th>
                        <th>Type</th>
                    </tr>
                </thead>

                <tbody>
                    {reservations.map(r => (
                        <tr key={r.id}>
                            <td>{r.id}</td>
                            <td>{r.start_time}</td>
                            <td>{r.end_time}</td>
                            <td>{r.room_id ? "Salle" : "Matériel"}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <div style={{ display: "flex", gap: 20 }}>
                <div>📅 {reservations.length}</div>
                <div>🏢 salles</div>
                <div>🧰 équipements</div>
            </div>
        </div>
    )
}