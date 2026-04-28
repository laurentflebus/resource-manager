import { useState } from "react"
import { useAuth } from "../context/AuthContext"
import { API_URL } from "../services/api"

export default function Login() {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("")
    const [hovered, setHovered] = useState(false)
    const { login } = useAuth()

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError("")

        try {
            const res = await fetch(`${API_URL}/auth/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: new URLSearchParams({
                    username: email,
                    password: password
                })
            })

            const data = await res.json()

            if (!res.ok) {
                setError(data.detail || "Erreur login")
                return
            }

            login(data.access_token)

        } catch (err) {
            setError("Erreur serveur")
        }
    }

    return (
        <div style={{
            height: "100vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "#f3f4f6"
        }}>
            <form
                onSubmit={handleSubmit}
                style={{
                    background: "white",
                    padding: 30,
                    borderRadius: 12,
                    width: 320,
                    boxShadow: "0 10px 30px rgba(0,0,0,0.1)"
                }}
            >
                <h2 style={{ marginBottom: 20 }}>Connexion</h2>

                {error && (
                    <div style={{
                        background: "#fee2e2",
                        color: "#b91c1c",
                        padding: 10,
                        borderRadius: 6,
                        marginBottom: 10,
                        fontSize: 14
                    }}>
                        {error}
                    </div>
                )}

                <input
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    style={{
                        width: "100%",
                        padding: 10,
                        marginBottom: 10,
                        borderRadius: 6,
                        border: "1px solid #ccc"
                    }}
                />

                <input
                    type="password"
                    placeholder="Mot de passe"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={{
                        width: "100%",
                        padding: 10,
                        marginBottom: 20,
                        borderRadius: 6,
                        border: "1px solid #ccc"
                    }}
                />

                <button
                    type="submit"
                    onMouseEnter={() => setHovered(true)}
                    onMouseLeave={() => setHovered(false)}
                    style={{
                        width: "100%",
                        background: hovered ? "#4338ca" : "#4f46e5",
                        color: "white",
                        padding: 10,
                        borderRadius: 6,
                        border: "none",
                        cursor: "pointer",
                        fontWeight: "bold",
                        transition: "background 0.15s"
                    }}
                >
                    Se connecter
                </button>
            </form>
        </div>
    )
}