import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import { useEffect, useState } from "react"
import { getReservations } from "../services/api"

export default function CalendarView() {
    const [events, setEvents] = useState([])

    useEffect(() => {
        getReservations().then(data => {
            console.log("RAW DATA:", data)
            const formatted = data.map(r => ({
                title: r.room_id
                    ? `🏢 Salle ${r.room_id}`
                    : `🧰 Matériel ${r.equipment_id}`,
                start: r.start_time,
                end: r.end_time
            }))
            setEvents(formatted)
        })
    }, [])

    return (
        <FullCalendar
            plugins={[dayGridPlugin, timeGridPlugin]}
            initialView="timeGridWeek"
            events={events}
        />
    )
}