/**
 * Couche service — configuration et helpers pour les appels API.
 *
 * Ce fichier est la seule source de vérité pour l'URL du backend.
 * Elle est lue depuis la variable d'environnement REACT_APP_API_URL
 * (définie dans frontend/.env), avec http://127.0.0.1:8000 en fallback
 * pour le développement local.
 *
 * Exports :
 *   API_URL         URL de base de l'API FastAPI
 *   getAuthHeaders  Construit les headers HTTP avec le token Bearer
 *   setLogoutHandler Enregistre le callback logout depuis AuthContext
 *   apiFetch        Wrapper fetch avec interception automatique du 401
 */

/** URL de base de l'API — configurable via REACT_APP_API_URL dans .env */
export const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000"

/**
 * Référence au callback logout fourni par AuthContext.
 * Initialisée via setLogoutHandler() au montage de AuthProvider.
 * Permet à apiFetch de déclencher une déconnexion sans dépendance circulaire.
 */
let _logoutHandler = null

/**
 * Enregistre la fonction logout de AuthContext.
 * À appeler une seule fois dans AuthProvider au montage.
 *
 * @param {Function} fn - Fonction logout de useAuth()
 */
export function setLogoutHandler(fn) {
    _logoutHandler = fn
}

/**
 * Construit les headers HTTP standards pour les appels API authentifiés.
 * Si aucun token n'est fourni, le header Authorization est omis.
 *
 * @param {string|null} token - JWT Bearer token
 * @returns {object} Headers HTTP
 */
export function getAuthHeaders(token) {
    return {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` })
    }
}

/**
 * Wrapper autour de fetch avec interception automatique du 401.
 *
 * Si l'API retourne un 401 (token expiré ou invalide), apiFetch :
 *   1. Appelle logout() pour nettoyer la session
 *   2. Lance une erreur pour interrompre le flux appelant
 *
 * Pour tous les autres statuts, le comportement est identique à fetch natif.
 * Les appelants n'ont pas besoin de gérer le cas 401 individuellement.
 *
 * @param {string} url      - URL complète de la requête
 * @param {object} options  - Options fetch (method, headers, body...)
 * @returns {Promise<Response>}
 * @throws {Error} Si le serveur retourne un 401
 */
export async function apiFetch(url, options = {}) {
    const res = await fetch(url, options)

    if (res.status === 401) {
        if (_logoutHandler) {
            _logoutHandler()
        }
        throw new Error("Session expirée — veuillez vous reconnecter.")
    }

    return res
}
