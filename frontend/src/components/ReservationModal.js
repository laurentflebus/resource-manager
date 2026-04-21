import { useState } from "react"

export default function ReservationModal({ isOpen, onClose, onSubmit, start, end }) {
    const [type, setType] = useState("room")
    const [id, setId] = useState("")

    if (!isOpen) return null

    const handleSubmit = () => {
        const payload =
            type === "room"
                ? {
                    room_id: parseInt(id),
                    start_time: start,
                    end_time: end
                }
                : {
                    equipment_id: parseInt(id),
                    start_time: start,
                    end_time: end
                }

        onSubmit(payload)
        onClose()
    }

    return (
        <div style={styles.overlay}>
            <div style={styles.modal}>
                <h2>Créer une réservation</h2>

                <label>Type</label>
                <select value={type} onChange={(e) => setType(e.target.value)}>
                    <option value="room">Salle</option>
                    <option value="equipment">Équipement</option>
                </select>

                <label>ID</label>
                <input
                    value={id}
                    onChange={(e) => setId(e.target.value)}
                    placeholder="Ex: 1"
                />

                <div style={{ marginTop: 20 }}>
                    <button onClick={handleSubmit}>Créer</button>
                    <button onClick={onClose} style={{ marginLeft: 10 }}>
                        Annuler
                    </button>
                </div>
            </div>
        </div>
    )
}

const styles = {
    overlay: {
        position: "fixed",
        top: 0, left: 0, right: 0, bottom: 0,
        background: "rgba(0,0,0,0.5)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center"
    },
    modal: {
        background: "white",
        padding: 20,
        borderRadius: 10,
        width: 300
    }
}