/**
 * Composant principal — vue calendrier des réservations.
 *
 * Responsabilités :
 *   - Affichage du calendrier FullCalendar avec les réservations formatées
 *   - Sélection d'une plage horaire → ouverture de ReservationModal
 *   - Drag-and-drop / resize → mise à jour via useReservations
 *   - Clic sur un événement → suppression (admin uniquement)
 *   - Tooltip au survol d'un événement
 *   - Filtre visuel par type de ressource (salles / équipements / tout)
 *
 * La logique métier (fetch, create, delete, update) est entièrement
 * déléguée au hook useReservations. Ce composant ne gère que l'UI.
 */

import FullCalendar from "@fullcalendar/react"
import dayGridPlugin from "@fullcalendar/daygrid"
import timeGridPlugin from "@fullcalendar/timegrid"
import interactionPlugin from "@fullcalendar/interaction"
import { useState } from "react"
import { useAuth } from "../context/AuthContext"
import { useReservations } from "../hooks/useReservations"
import { hasConflict } from "../utils/calendarHelpers"
import ReservationModal from "./ReservationModal"

export default function CalendarView() {
    const [modalOpen, setModalOpen] = useState(false)
    const [selection, setSelection] = useState(null)
    const [filter, setFilter] = useState("all")

    const { role } = useAuth()
    const {
        events,
        rooms,
        equipment,
        loading,
        error,
        createReservation,
        deleteReservation,
        updateReservation
    } = useReservations()

    // ── Filtre côté client ───────────────────────────────────────────────────
    const filteredEvents = filter === "all"
        ? events
        : events.filter(e => e.extendedProps.type === filter)

    // ── Handlers FullCalendar ────────────────────────────────────────────────

    /** Ouvre la modal de création quand l'utilisateur sélectionne une plage. */
    const handleSelect = (info) => {
        setSelection(info)
        setModalOpen(true)
    }

    /** Relaye la création au hook et ferme la modal si succès. */
    const handleCreate = async (params) => {
        const result = await createReservation(params)
        if (result.ok) setModalOpen(false)
        return result
    }

    /**
     * Appelé après un drag-and-drop ou un resize.
     * Vérifie d'abord le conflit côté client, puis appelle l'API.
     * Appelle info.revert() si l'API refuse la mise à jour.
     */
    const handleEventDrop = async (info) => {
        if (hasConflict(info.event, events)) {
            alert("⚠️ Conflit de réservation détecté")
            info.revert()
            return
        }
        const ok = await updateReservation(info.event.id, {
            start: info.event.start,
            end: info.event.end
        })
        if (!ok) info.revert()
    }

    /**
     * Clic sur un événement — suppression après confirmation.
     * Ignoré si l'utilisateur n'est pas admin.
     */
    const handleEventClick = (info) => {
        if (role !== "admin") return
        if (window.confirm("Supprimer cette réservation ?")) {
            deleteReservation(info.event.id)
        }
    }

    // ── Tooltip ──────────────────────────────────────────────────────────────

    /**
     * Monte un tooltip DOM natif sur chaque événement du calendrier.
     * Le tooltip est attaché à info.el._tooltip pour pouvoir le supprimer
     * proprement dans handleEventWillUnmount.
     */
    const handleEventDidMount = (info) => {
        info.el.style.cursor = role === "admin" ? "pointer" : "default"

        const tooltip = document.createElement("div")
        tooltip.innerHTML = `<strong>${info.event.title}</strong><br/>📍 ${info.event.extendedProps.location}`
        Object.assign(tooltip.style, {
            position: "absolute",
            background: "#111",
            color: "#fff",
            padding: "6px 10px",
            borderRadius: "6px",
            fontSize: "12px",
            display: "none",
            zIndex: 9999,
            pointerEvents: "none"
        })
        document.body.appendChild(tooltip)
        info.el._tooltip = tooltip

        info.el.addEventListener("mouseenter", (e) => {
            tooltip.style.display = "block"
            tooltip.style.left = e.pageX + 12 + "px"
            tooltip.style.top = e.pageY + 12 + "px"
        })
        info.el.addEventListener("mousemove", (e) => {
            tooltip.style.left = e.pageX + 12 + "px"
            tooltip.style.top = e.pageY + 12 + "px"
        })
        info.el.addEventListener("mouseleave", () => {
            tooltip.style.display = "none"
        })
    }

    /** Supprime le tooltip DOM quand FullCalendar démonte un événement. */
    const handleEventWillUnmount = (info) => {
        info.el._tooltip?.remove()
    }

    // ── Rendu ────────────────────────────────────────────────────────────────
    return (
        <div style={{ height: "100%", display: "flex", flexDirection: "column", padding: 20 }}>

            {/* Barre de filtre + indicateurs d'état */}
            <div style={{ marginBottom: 10 }}>
                <select value={filter} onChange={(e) => setFilter(e.target.value)}>
                    <option value="all">Tout</option>
                    <option value="room">Salles</option>
                    <option value="equipment">Équipements</option>
                </select>
                {loading && (
                    <span style={{ marginLeft: 12, fontSize: 13, color: "#6b7280" }}>
                        Chargement…
                    </span>
                )}
                {error && (
                    <span style={{ marginLeft: 12, fontSize: 13, color: "#ef4444" }}>
                        {error}
                    </span>
                )}
            </div>

            <FullCalendar
                plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
                initialView="timeGridWeek"
                headerToolbar={{
                    left: "prev,next today",
                    center: "title",
                    right: "dayGridMonth,timeGridWeek,timeGridDay"
                }}
                height="100%"
                selectable={true}
                select={handleSelect}
                selectAllow={(info) => info.start.getTime() >= Date.now()}
                events={filteredEvents}
                nowIndicator={true}
                slotMinTime="08:00:00"
                slotMaxTime="20:00:00"
                editable={role === "admin"}
                eventStartEditable={role === "admin"}
                eventDurationEditable={role === "admin"}
                eventDrop={handleEventDrop}
                eventResize={handleEventDrop}
                eventChange={() => {}}
                eventClick={handleEventClick}
                eventDidMount={handleEventDidMount}
                eventWillUnmount={handleEventWillUnmount}
            />

            {modalOpen && (
                <ReservationModal
                    selection={selection}
                    rooms={rooms}
                    equipment={equipment}
                    onConfirm={handleCreate}
                    onClose={() => setModalOpen(false)}
                />
            )}

        </div>
    )
}
