/**
 * Tableau de bord administrateur.
 *
 * Affiche :
 *   - Statistiques globales (total réservations, salles, équipements)
 *   - Table paginée des réservations avec navigation page précédente/suivante
 *   - Action de suppression avec confirmation
 *
 * La pagination est gérée côté serveur : chaque changement de page
 * déclenche un nouvel appel à GET /reservations?page=N&page_size=10.
 */

import { useEffect, useState } from "react"
import { useAuth } from "../context/AuthContext"
import { API_URL, apiFetch } from "../services/api"

const PAGE_SIZE = 10

export default function AdminDashboard() {
    const [stats, setStats] = useState({ reservations: 0, rooms: 0, equipments: 0 })
    const [reservations, setReservations] = useState([])
    const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0 })
    const [loading, setLoading] = useState(false)
    const { token } = useAuth()

    const authHeader = { Authorization: `Bearer ${token}` }

    useEffect(() => {
        fetchStats()
        fetchReservations(1)
    }, [])

    /**
     * Charge les statistiques globales (compteurs salles, équipements, total réservations).
     * Utilise le champ `total` de la réponse paginée pour le compteur de réservations.
     */
    const fetchStats = async () => {
        try {
            const [reservationsRes, roomsRes, equipmentsRes] = await Promise.all([
                apiFetch(`${API_URL}/reservations?page=1&page_size=1`, { headers: authHeader }),
                apiFetch(`${API_URL}/rooms`, { headers: authHeader }),
                apiFetch(`${API_URL}/equipments`, { headers: authHeader })
            ])
            const reservationsData = await reservationsRes.json()
            const rooms = await roomsRes.json()
            const equipments = await equipmentsRes.json()

            setStats({
                reservations: reservationsData.total || 0,
                rooms: rooms.length || 0,
                equipments: equipments.length || 0
            })
        } catch (err) {
            console.error("Erreur lors du chargement des statistiques :", err)
        }
    }

    /**
     * Charge une page de réservations depuis l'API.
     * Met à jour la liste et les métadonnées de pagination.
     *
     * @param {number} page - Numéro de page à charger (commence à 1)
     */
    const fetchReservations = async (page) => {
        setLoading(true)
        try {
            const res = await apiFetch(
                `${API_URL}/reservations?page=${page}&page_size=${PAGE_SIZE}`,
                { headers: authHeader }
            )
            const data = await res.json()
            setReservations(data.items || [])
            setPagination({ page: data.page, pages: data.pages, total: data.total })
        } catch (err) {
            console.error("Erreur lors du chargement des réservations :", err)
        } finally {
            setLoading(false)
        }
    }

    const handleDelete = async (id) => {
        if (!window.confirm("Supprimer cette réservation ?")) return
        await apiFetch(`${API_URL}/reservations/${id}`, {
            method: "DELETE",
            headers: authHeader
        })
        // Reste sur la page courante, revient à la page précédente si elle est vide
        const targetPage = reservations.length === 1 && pagination.page > 1
            ? pagination.page - 1
            : pagination.page
        fetchStats()
        fetchReservations(targetPage)
    }

    const handlePageChange = (newPage) => {
        if (newPage < 1 || newPage > pagination.pages) return
        fetchReservations(newPage)
    }

    return (
        <div style={{ padding: 20 }}>
            <h1>🛠️ Admin Dashboard</h1>

            {/* ── Statistiques ─────────────────────────────────────────── */}
            <div style={{ display: "flex", gap: 20, marginTop: 20 }}>
                <Card title="Réservations" value={stats.reservations} color="#4f46e5" />
                <Card title="Salles" value={stats.rooms} color="#16a34a" />
                <Card title="Équipements" value={stats.equipments} color="#f59e0b" />
            </div>

            {/* ── Table des réservations ────────────────────────────────── */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 30 }}>
                <h3 style={{ margin: 0 }}>
                    Réservations
                    <span style={{ fontSize: 13, fontWeight: "normal", color: "#6b7280", marginLeft: 8 }}>
                        ({pagination.total} au total)
                    </span>
                </h3>
            </div>

            <table style={{ width: "100%", marginTop: 10, borderCollapse: "collapse" }}>
                <thead>
                    <tr style={{ background: "#f3f4f6" }}>
                        <th style={thStyle}>ID</th>
                        <th style={thStyle}>Type</th>
                        <th style={thStyle}>Nom</th>
                        <th style={thStyle}>Début</th>
                        <th style={thStyle}>Fin</th>
                        <th style={thStyle}>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {loading ? (
                        <tr>
                            <td colSpan="6" style={emptyCellStyle}>Chargement…</td>
                        </tr>
                    ) : reservations.length === 0 ? (
                        <tr>
                            <td colSpan="6" style={emptyCellStyle}>📭 Aucune réservation</td>
                        </tr>
                    ) : (
                        reservations.map(r => (
                            <tr key={r.id} style={{ textAlign: "center", borderBottom: "1px solid #eee" }}>
                                <td style={tdStyle}>{r.id}</td>
                                <td style={tdStyle}>{r.room_id ? "Salle" : "Matériel"}</td>
                                <td style={tdStyle}>{r.room_name || r.equipment_name || "—"}</td>
                                <td style={tdStyle}>{new Date(r.start_time).toLocaleString("fr-BE")}</td>
                                <td style={tdStyle}>{new Date(r.end_time).toLocaleString("fr-BE")}</td>
                                <td style={tdStyle}>
                                    <button onClick={() => handleDelete(r.id)} style={deleteBtnStyle}>
                                        Supprimer
                                    </button>
                                </td>
                            </tr>
                        ))
                    )}
                </tbody>
            </table>

            {/* ── Pagination ───────────────────────────────────────────── */}
            {pagination.pages > 1 && (
                <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 12, marginTop: 16 }}>
                    <button
                        onClick={() => handlePageChange(pagination.page - 1)}
                        disabled={pagination.page === 1}
                        style={pageBtnStyle(pagination.page === 1)}
                    >
                        ← Précédent
                    </button>

                    <span style={{ fontSize: 13, color: "#6b7280" }}>
                        Page {pagination.page} / {pagination.pages}
                    </span>

                    <button
                        onClick={() => handlePageChange(pagination.page + 1)}
                        disabled={pagination.page === pagination.pages}
                        style={pageBtnStyle(pagination.page === pagination.pages)}
                    >
                        Suivant →
                    </button>
                </div>
            )}
        </div>
    )
}

// ── Styles ────────────────────────────────────────────────────────────────────

function Card({ title, value, color }) {
    return (
        <div style={{ flex: 1, background: color, padding: 20, borderRadius: 12, color: "white", textAlign: "center" }}>
            <h3 style={{ margin: "0 0 8px" }}>{title}</h3>
            <p style={{ fontSize: 28, fontWeight: "bold", margin: 0 }}>{value}</p>
        </div>
    )
}

const thStyle = { padding: "10px 12px", textAlign: "center", fontWeight: 600, fontSize: 13 }
const tdStyle = { padding: "10px 12px", fontSize: 13 }
const emptyCellStyle = { textAlign: "center", padding: 24, color: "#6b7280" }
const deleteBtnStyle = {
    background: "#ef4444", color: "white", border: "none",
    padding: "5px 10px", borderRadius: 4, cursor: "pointer", fontSize: 12
}
const pageBtnStyle = (disabled) => ({
    padding: "6px 14px", borderRadius: 6, border: "1px solid #d1d5db",
    background: disabled ? "#f3f4f6" : "white",
    color: disabled ? "#9ca3af" : "#111",
    cursor: disabled ? "default" : "pointer",
    fontSize: 13
})
