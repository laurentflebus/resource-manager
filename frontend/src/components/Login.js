import { useState } from "react"

export default function Login({ onLogin }) {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("")

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError("")

        try {
            const res = await fetch("http://127.0.0.1:8000/auth/login", {
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

            localStorage.setItem("token", data.access_token)
            onLogin()

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

                <button onMouseOver={(e) => e.target.style.background = "#4338ca"} onMouseOut={(e) => e.target.style.background = "#4f46e5"}
                    type="submit"
                    style={{
                        width: "100%",
                        background: "#4f46e5",
                        color: "white",
                        padding: 10,
                        borderRadius: 6,
                        border: "none",
                        cursor: "pointer",
                        fontWeight: "bold"
                    }}
                >
                    Se connecter
                </button>
            </form>
        </div>
    )
}