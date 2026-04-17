const API_URL = "http://127.0.0.1:8000";

function getAuthHeaders() {
    const token = localStorage.getItem("token")

    return {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` })
    }
}

export async function getReservations() {
    const res = await fetch(`${API_URL}/reservations`, {
        headers: getAuthHeaders()
    })

    return res.json();
}