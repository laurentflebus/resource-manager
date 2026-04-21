import FullCalendar from "@fullcalendar/react"
import dayGridPlugin from "@fullcalendar/daygrid"
import timeGridPlugin from "@fullcalendar/timegrid"
import interactionPlugin from "@fullcalendar/interaction"
import { useEffect, useState } from "react"

export default function CalendarView() {


    // ================= STATE =================
    const [events, setEvents] = useState([])
    const [modalOpen, setModalOpen] = useState(false)
    const [selection, setSelection] = useState(null)

    const [type, setType] = useState("room")
    const [id, setId] = useState("")
    const [filter, setFilter] = useState("all")

    const [rooms, setRooms] = useState([])
    const [equipment, setEquipment] = useState([])

    const token = localStorage.getItem("token")

    // ================= FETCH RESERVATIONS =================
    useEffect(() => {
        if (rooms.length && equipment.length) {
            fetchReservations()
        }
    }, [rooms, equipment])
    const fetchReservations = async () => {
        const res = await fetch("http://127.0.0.1:8000/reservations", {
            headers: {
                Authorization: `Bearer ${token}`
            }
        })

        const data = await res.json()

        if (!Array.isArray(data)) {
            console.error("API error:", data)
            return
        }

        const formatted = data.map(r => {

            const room = rooms.find(x => x.id === r.room_id)
            const equip = equipment.find(x => x.id === r.equipment_id)

            const getColor = (type, id) => {
                if (type === "room") {
                    const colors = ["#4f46e5", "#6366f1", "#818cf8"]
                    return colors[id % colors.length]
                } else {
                    const colors = ["#16a34a", "#22c55e", "#4ade80"]
                    return colors[id % colors.length]
                }
            }

            return {
                id: r.id,

                title: r.room_id
                    ? `🏢 ${room?.name || "Salle"} - ${room?.location || "?"}`
                    : `🧰 ${equip?.name || "Matériel"}`,

                start: r.start_time,
                end: r.end_time,

                backgroundColor: getColor(
                    r.room_id ? "room" : "equipment",
                    r.room_id || r.equipment_id
                ),

                extendedProps: {
                    type: r.room_id ? "room" : "equipment",
                    location: room?.location || "—"
                }
            }
        })

        setEvents(formatted)
    }

    // ================= FETCH ROOMS + EQUIPMENT =================
    const fetchMeta = async () => {
        try {
            const [r1, r2] = await Promise.all([
                fetch("http://127.0.0.1:8000/rooms", {
                    headers: { Authorization: `Bearer ${token}` }
                }),
                fetch("http://127.0.0.1:8000/equipments", {
                    headers: { Authorization: `Bearer ${token}` }
                })
            ])

            setRooms(await r1.json())
            setEquipment(await r2.json())
        } catch (err) {
            console.error(err)
        }
    }

    // ================= CREATE RESERVATION =================
    const handleCreate = async () => {

        if (!selection || !id) return

        const payload =
            type === "room"
                ? {
                    room_id: Number(id),
                    start_time: selection.start,
                    end_time: selection.end
                }
                : {
                    equipment_id: Number(id),
                    start_time: selection.start,
                    end_time: selection.end
                }

        await fetch("http://127.0.0.1:8000/reservations", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        })

        setModalOpen(false)
        setId("")
        fetchReservations()
    }

    // ================= SELECT SLOT =================
    const handleSelect = (info) => {
        setSelection(info)
        setModalOpen(true)
    }

    // ================= INIT =================
    useEffect(() => {
        fetchReservations()
        fetchMeta()
    }, [])

    // ================= FILTERED EVENTS =================
    const filteredEvents =
        filter === "all"
            ? events
            : events.filter(e => e.extendedProps.type === filter)

    // ================= RENDER =================
    return (
        <div style={{ padding: 20 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10 }}>

                <h1>Calendrier</h1>

                <button
                    onClick={() => {
                        localStorage.removeItem("token")
                        window.location.reload()
                    }}
                    style={{
                        background: "#ef4444",
                        color: "white",
                        border: "none",
                        padding: "6px 12px",
                        borderRadius: "6px",
                        cursor: "pointer"
                    }}
                >
                    Logout
                </button>

            </div>

            {/* FILTER */}
            <div style={{ marginBottom: 10 }}>
                <select
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                >
                    <option value="all">Tout</option>
                    <option value="room">Salles</option>
                    <option value="equipment">Équipements</option>
                </select>
            </div>

            {/* CALENDAR */}
            <FullCalendar
                plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
                initialView="timeGridWeek"
                selectable={true}
                select={handleSelect}
                events={filteredEvents}

                nowIndicator={true}
                slotMinTime="08:00:00"
                slotMaxTime="20:00:00"
                eventDidMount={(info) => {
                    const tooltip = document.createElement("div")

                    tooltip.innerHTML = `<strong>${info.event.title}</strong><br/>📍 ${info.event.extendedProps.location}`
                    tooltip.style.position = "absolute"
                    tooltip.style.background = "#111"
                    tooltip.style.color = "#fff"
                    tooltip.style.padding = "6px 10px"
                    tooltip.style.borderRadius = "6px"
                    tooltip.style.fontSize = "12px"
                    tooltip.style.display = "none"
                    tooltip.style.zIndex = 9999

                    document.body.appendChild(tooltip)

                    info.el.addEventListener("mouseenter", (e) => {
                        tooltip.style.display = "block"
                        tooltip.style.left = e.pageX + 10 + "px"
                        tooltip.style.top = e.pageY + 10 + "px"
                    })

                    info.el.addEventListener("mouseleave", () => {
                        tooltip.style.display = "none"
                    })
                }}
            />

            {/* ================= MODAL ================= */}
            {modalOpen && (
                <div
                    onClick={() => setModalOpen(false)}
                    style={{
                        position: "fixed",
                        inset: 0,
                        background: "rgba(0,0,0,0.5)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        zIndex: 9999
                    }}
                >
                    <div
                        onClick={(e) => e.stopPropagation()}
                        style={{
                            background: "white",
                            padding: 24,
                            borderRadius: 12,
                            width: 350
                        }}
                    >

                        <h3 style={{ marginBottom: 10 }}>
                            Nouvelle réservation
                        </h3>

                        <div style={{ fontSize: 12, marginBottom: 10 }}>
                            {selection?.start?.toString()} → {selection?.end?.toString()}
                        </div>

                        {/* TYPE */}
                        <select
                            value={type}
                            onChange={(e) => setType(e.target.value)}
                            style={{ width: "100%", marginBottom: 10 }}
                        >
                            <option value="room">Salle</option>
                            <option value="equipment">Équipement</option>
                        </select>

                        {/* DYNAMIC SELECT */}
                        {type === "room" ? (
                            <select
                                value={id}
                                onChange={(e) => setId(e.target.value)}
                                style={{ width: "100%", marginBottom: 10 }}
                            >
                                <option value="">Choisir salle</option>
                                {(rooms || []).map(r => (
                                    <option key={r.id} value={r.id}>
                                        {r.name}
                                    </option>
                                ))}
                            </select>
                        ) : (
                            <select
                                value={id}
                                onChange={(e) => setId(e.target.value)}
                                style={{ width: "100%", marginBottom: 10 }}
                            >
                                <option value="">Choisir équipement</option>
                                {(equipment || []).map(e => (
                                    <option key={e.id} value={e.id}>
                                        {e.name}
                                    </option>
                                ))}
                            </select>
                        )}

                        <button
                            onClick={handleCreate}
                            style={{
                                width: "100%",
                                background: "#4f46e5",
                                color: "white",
                                padding: 10,
                                borderRadius: 6,
                                border: "none"
                            }}
                        >
                            Créer
                        </button>

                        <button
                            onClick={() => setModalOpen(false)}
                            style={{
                                width: "100%",
                                marginTop: 10
                            }}
                        >
                            Annuler
                        </button>

                    </div>
                </div>
            )}

        </div>
    )
}