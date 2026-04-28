/**
 * Fonctions utilitaires pour le calendrier FullCalendar.
 *
 * Ce module est sans état (fonctions pures) — aucun import React.
 * Il peut être testé unitairement de façon isolée.
 *
 * Exports :
 *   getEventColor()       Couleur d'un événement selon le type et l'id de ressource
 *   formatEventTitle()    Titre affiché sur l'événement dans le calendrier
 *   formatReservation()   Transforme une réservation API en objet FullCalendar
 *   hasConflict()         Détecte un chevauchement côté client (avant appel API)
 */

/** Palette de couleurs pour les salles (teintes indigo) */
const ROOM_COLORS = ["#4f46e5", "#6366f1", "#818cf8"]

/** Palette de couleurs pour les équipements (teintes vert) */
const EQUIPMENT_COLORS = ["#16a34a", "#22c55e", "#4ade80"]

/**
 * Retourne une couleur déterministe pour une ressource donnée.
 * La couleur est choisie par modulo sur la palette — même ressource = même couleur.
 *
 * @param {'room'|'equipment'} type - Type de ressource
 * @param {number} id               - Identifiant de la ressource
 * @returns {string}                  Couleur CSS hexadécimale
 */
export function getEventColor(type, id) {
    const palette = type === "room" ? ROOM_COLORS : EQUIPMENT_COLORS
    return palette[id % palette.length]
}

/**
 * Construit le titre affiché sur un événement du calendrier.
 * Inclut une icône, le nom de la ressource et (pour les salles) l'emplacement.
 *
 * @param {object}   r         - Objet réservation brut de l'API
 * @param {object[]} rooms     - Liste des salles chargées
 * @param {object[]} equipment - Liste des équipements chargés
 * @returns {string}
 */
export function formatEventTitle(r, rooms, equipment) {
    if (r.room_id) {
        const room = rooms.find(x => Number(x.id) === Number(r.room_id))
        const name = room?.name ?? r.room_name ?? "Salle inconnue"
        const location = room?.location ?? "?"
        return `🏢 ${name} - ${location}`
    }
    const equip = equipment.find(x => Number(x.id) === Number(r.equipment_id))
    const name = equip?.name ?? r.equipment_name ?? "Matériel inconnu"
    return `🧰 ${name}`
}

/**
 * Convertit une réservation API en objet événement FullCalendar.
 *
 * L'objet retourné est directement utilisable dans la prop `events` de <FullCalendar>.
 * Les données métier (type, resourceId, location) sont stockées dans extendedProps
 * pour être accessibles dans les callbacks FullCalendar (eventClick, eventDrop...).
 *
 * @param {object}   r         - Réservation brute retournée par l'API
 * @param {object[]} rooms     - Liste des salles
 * @param {object[]} equipment - Liste des équipements
 * @returns {object} Événement FullCalendar
 */
export function formatReservation(r, rooms, equipment) {
    const type = r.room_id ? "room" : "equipment"
    const resourceId = r.room_id || r.equipment_id
    const room = rooms.find(x => Number(x.id) === Number(r.room_id))

    return {
        id: r.id,
        title: formatEventTitle(r, rooms, equipment),
        start: r.start_time,
        end: r.end_time,
        backgroundColor: getEventColor(type, resourceId),
        extendedProps: {
            type,
            resourceId,
            location: room?.location || "—"
        }
    }
}

/**
 * Vérifie côté client si un événement est en conflit avec d'autres événements existants.
 * Utilisé après un drag-and-drop pour détecter les chevauchements avant l'appel API.
 *
 * Deux événements sont en conflit s'ils portent sur la même ressource (même type + même id)
 * et que leurs plages horaires se chevauchent.
 *
 * @param {object}   event     - Événement FullCalendar déplacé (avec start, end, extendedProps)
 * @param {object[]} allEvents - Tous les événements actuellement affichés
 * @returns {boolean} True si un conflit est détecté
 */
export function hasConflict(event, allEvents) {
    return allEvents.some(e =>
        String(e.id) !== String(event.id) &&
        e.extendedProps.type === event.extendedProps.type &&
        e.extendedProps.resourceId === event.extendedProps.resourceId &&
        new Date(event.start) < new Date(e.end) &&
        new Date(event.end) > new Date(e.start)
    )
}
