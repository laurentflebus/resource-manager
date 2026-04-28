/**
 * Hook personnalisé — gestion des réservations.
 *
 * Encapsule tous les appels API liés aux réservations :
 *   - Chargement initial des salles et équipements (fetchMeta)
 *   - Chargement des réservations formatées pour FullCalendar (fetchReservations)
 *   - Création, suppression, mise à jour d'une réservation
 *
 * Les réservations sont formatées via formatReservation() (calendarHelpers)
 * et exposées prêtes à l'emploi pour FullCalendar.
 *
 * Usage :
 *   const { events, rooms, equipment, loading, error,
 *           createReservation, deleteReservation, updateReservation } = useReservations()
 */

import { useState, useEffect } from "react"
import { useAuth } from "../context/AuthContext"
import { API_URL, apiFetch } from "../services/api"
import { formatReservation } from "../utils/calendarHelpers"

export function useReservations() {
    const [events, setEvents] = useState([])
    const [rooms, setRooms] = useState([])
    const [equipment, setEquipment] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    const { token } = useAuth()
    const authHeader = { Authorization: `Bearer ${token}` }

    // Charge les méta-données au montage du composant
    useEffect(() => {
        fetchMeta()
    }, [])

    // Charge les réservations dès que salles et équipements sont disponibles
    // (nécessaire pour le formatage des titres et couleurs)
    useEffect(() => {
        if (rooms.length > 0 && equipment.length > 0) {
            fetchReservations()
        }
    }, [rooms, equipment])

    /**
     * Charge les salles et équipements en parallèle.
     * Ces données sont nécessaires pour résoudre les noms dans formatReservation.
     */
    const fetchMeta = async () => {
        try {
            const [r1, r2] = await Promise.all([
                apiFetch(`${API_URL}/rooms`, { headers: authHeader }),
                apiFetch(`${API_URL}/equipments`, { headers: authHeader })
            ])
            setRooms(await r1.json())
            setEquipment(await r2.json())
        } catch (err) {
            setError("Impossible de charger les salles et équipements")
            console.error(err)
        }
    }

    /**
     * Charge une page de réservations et les formate pour FullCalendar.
     * Lit le champ `items` de la réponse paginée retournée par l'API.
     *
     * @param {number} page      - Numéro de page (défaut : 1)
     * @param {number} pageSize  - Éléments par page (défaut : 100 pour charger tout le calendrier)
     */
    const fetchReservations = async (page = 1, pageSize = 100) => {
        setLoading(true)
        try {
            const res = await apiFetch(
                `${API_URL}/reservations?page=${page}&page_size=${pageSize}`,
                { headers: authHeader }
            )
            const data = await res.json()

            if (!data.items || !Array.isArray(data.items)) {
                setError("Réponse inattendue du serveur")
                return
            }

            setEvents(data.items.map(r => formatReservation(r, rooms, equipment)))
            setError(null)
        } catch (err) {
            setError("Impossible de charger les réservations")
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    /**
     * Crée une nouvelle réservation après validation locale des dates.
     *
     * @param {{ type: 'room'|'equipment', resourceId: number, start: Date, end: Date }} params
     * @returns {{ ok: boolean, message?: string }}
     */
    const createReservation = async ({ type, resourceId, start, end }) => {
        if (start < new Date()) {
            return { ok: false, message: "⛔ Impossible de créer une réservation dans le passé" }
        }
        if (end <= start) {
            return { ok: false, message: "⛔ La date de fin doit être après la date de début" }
        }

        const payload = type === "room"
            ? { room_id: Number(resourceId), start_time: start, end_time: end }
            : { equipment_id: Number(resourceId), start_time: start, end_time: end }

        const res = await apiFetch(`${API_URL}/reservations`, {
            method: "POST",
            headers: { "Content-Type": "application/json", ...authHeader },
            body: JSON.stringify(payload)
        })

        if (!res.ok) {
            const err = await res.json()
            return { ok: false, message: err.detail || "Erreur lors de la création" }
        }

        await fetchReservations()
        return { ok: true }
    }

    /**
     * Supprime une réservation par son id et rafraîchit la liste.
     * @param {number} id
     */
    const deleteReservation = async (id) => {
        await apiFetch(`${API_URL}/reservations/${id}`, {
            method: "DELETE",
            headers: authHeader
        })
        await fetchReservations()
    }

    /**
     * Met à jour les dates d'une réservation (drag-and-drop / resize).
     * Retourne false si l'API signale un conflit, true sinon.
     *
     * @param {number} id
     * @param {{ start: Date, end: Date }} param
     * @returns {boolean}
     */
    const updateReservation = async (id, { start, end }) => {
        const res = await apiFetch(`${API_URL}/reservations/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json", ...authHeader },
            body: JSON.stringify({
                start_time: start.toISOString(),
                end_time: end.toISOString()
            })
        })
        if (!res.ok) return false
        await fetchReservations()
        return true
    }

    return {
        events,
        rooms,
        equipment,
        loading,
        error,
        createReservation,
        deleteReservation,
        updateReservation,
        refresh: fetchReservations
    }
}
