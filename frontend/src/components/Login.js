import { useState } from "react"

export default function Login({ onLogin }) {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")

    const handleSubmit = async (e) => {
        e.preventDefault()
        const formData = new URLSearchParams()
        formData.append("username", email)
        formData.append("password", password)

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
        console.log("LOGIN RESPONSE:", data)

        if (!data.access_token) {
            console.error("No token received")
            return
        }

        localStorage.setItem("token", data.access_token)

        onLogin()
    }

    return (
        <form onSubmit={handleSubmit}>
            <h2>Login</h2>

            <input
                placeholder="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
            />

            <input
                type="password"
                placeholder="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />

            <button type="submit">Login</button>
        </form>
    )
}