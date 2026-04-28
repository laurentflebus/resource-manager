/**
 * Contexte d'authentification global.
 *
 * Fournit à toute l'application :
 *   - token     : JWT Bearer stocké en localStorage
 *   - role      : rôle de l'utilisateur ('user' | 'admin'), lu depuis le JWT
 *   - isLoggedIn: booléen de session active
 *   - login()   : appelé après un login réussi — stocke le token et décode le rôle
 *   - logout()  : efface la session et redirige vers le formulaire de connexion
 *
 * Le rôle est toujours lu depuis le payload JWT décodé, jamais depuis
 * localStorage directement, pour éviter la falsification côté client.
 *
 * Usage :
 *   const { token, role, isLoggedIn, login, logout } = useAuth()
 */

import { createContext, useContext, useState, useEffect } from "react"
import { setLogoutHandler } from "../services/api"

const AuthContext = createContext(null)

/**
 * Décode la partie payload d'un token JWT (base64url → objet JS).
 * Retourne null si le token est malformé.
 * @param {string} token
 * @returns {object|null}
 */
function decodeToken(token) {
    try {
        return JSON.parse(atob(token.split(".")[1]))
    } catch {
        return null
    }
}

/**
 * Lit le token en localStorage au démarrage de l'app.
 * Si le token est expiré, nettoie le localStorage et retourne un état déconnecté.
 * @returns {{ token: string|null, role: string|null, isLoggedIn: boolean }}
 */
function getInitialAuth() {
    const token = localStorage.getItem("token")
    if (!token) return { token: null, role: null, isLoggedIn: false }

    const payload = decodeToken(token)
    if (!payload || payload.exp * 1000 < Date.now()) {
        localStorage.removeItem("token")
        return { token: null, role: null, isLoggedIn: false }
    }

    return { token, role: payload.role, isLoggedIn: true }
}

/**
 * Provider à placer au plus haut de l'arbre React (dans index.js).
 * Initialise l'état d'auth depuis localStorage et expose les actions.
 */
export function AuthProvider({ children }) {
    const [auth, setAuth] = useState(getInitialAuth)

    /**
     * Enregistre logout comme handler global dans api.js dès le montage.
     * Permet à apiFetch d'appeler logout() sans dépendance circulaire.
     */
    useEffect(() => {
        setLogoutHandler(logout)
    }, [])

    /**
     * Enregistre un token JWT reçu après login.
     * Décode le rôle depuis le payload et met à jour l'état global.
     * @param {string} token - JWT Bearer reçu de l'API
     */
    const login = (token) => {
        const payload = decodeToken(token)
        if (!payload) return

        localStorage.setItem("token", token)
        setAuth({ token, role: payload.role, isLoggedIn: true })
    }

    /**
     * Déconnecte l'utilisateur : efface le localStorage et réinitialise l'état.
     * Appelée automatiquement par apiFetch en cas de réponse 401.
     */
    const logout = () => {
        localStorage.removeItem("token")
        setAuth({ token: null, role: null, isLoggedIn: false })
    }

    return (
        <AuthContext.Provider value={{ ...auth, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

/**
 * Hook personnalisé pour accéder au contexte d'auth depuis n'importe quel composant.
 * Lève une erreur si utilisé hors d'un AuthProvider.
 * @returns {{ token, role, isLoggedIn, login, logout }}
 */
export function useAuth() {
    const ctx = useContext(AuthContext)
    if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>")
    return ctx
}
