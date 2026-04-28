import { useState } from "react"

const overlayStyle = {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.5)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 9999
}

const cardStyle = {
    background: "white",
    padding: 24,
    borderRadius: 12,
    width: 350,
    boxShadow: "0 20px 40px rgba(0,0,0,0.2)"
}

const inputStyle = {
    width: "100%",
    padding: 9,
    marginBottom: 10,
    borderRadius: 6,
    border: "1px solid #d1d5db",
    boxSizing: "border-box"
}

const btnStyle = (color = "#4f46e5") => ({
    width: "100%",
    background: color,
    color: "white",
    padding: 10,
    borderRadius: 6,
    border: "none",
    cursor: "pointer",
    fontWeight: 500,
    marginTop: 4
})

export default function ReservationModal({ selection, rooms, equipment, onConfirm, onClose }) {
    const [type, setType] = useState("room")
    const [resourceId, setResourceId] = useState("")
    const [errorMsg, setErrorMsg] = useState("")

    const formatDate = (d) =>
        d ? new Date(d).toLocaleString("fr-BE", { dateStyle: "short", timeStyle: "short" }) : "—"

    const handleConfirm = async () => {
        if (!resourceId) {
            setErrorMsg("Veuillez sélectionner une ressource.")
            return
        }
        setErrorMsg("")
        const result = await onConfirm({ type, resourceId, start: selection.start, end: selection.end })
        if (result && !result.ok) {
            setErrorMsg(result.message)
        }
    }

    return (
        <div style={overlayStyle} onClick={onClose}>
            <div style={cardStyle} onClick={(e) => e.stopPropagation()}>

                <h3 style={{ marginBottom: 8 }}>Nouvelle réservation</h3>

                <div style={{ fontSize: 12, color: "#6b7280", marginBottom: 14 }}>
                    {formatDate(selection?.start)} → {formatDate(selection?.end)}
                </div>

                {errorMsg && (
                    <div style={{
                        background: "#fee2e2", color: "#b91c1c",
                        padding: "8px 10px", borderRadius: 6,
                        fontSize: 13, marginBottom: 10
                    }}>
                        {errorMsg}
                    </div>
                )}

                <select
                    value={type}
                    onChange={(e) => { setType(e.target.value); setResourceId("") }}
                    style={inputStyle}
                >
                    <option value="room">Salle</option>
                    <option value="equipment">Équipement</option>
                </select>

                <select
                    value={resourceId}
                    onChange={(e) => setResourceId(e.target.value)}
                    style={inputStyle}
                >
                    <option value="">Choisir {type === "room" ? "une salle" : "un équipement"}</option>
                    {(type === "room" ? rooms : equipment).map(item => (
                        <option key={item.id} value={item.id}>{item.name}</option>
                    ))}
                </select>

                <button onClick={handleConfirm} style={btnStyle()}>Créer</button>
                <button onClick={onClose} style={btnStyle("#6b7280")}>Annuler</button>

            </div>
        </div>
    )
}
