# Resource Manager

Application de réservation de salles et d'équipements.

- **Frontend** : React + FullCalendar (drag-and-drop, JWT auth)
- **Backend** : FastAPI + SQLAlchemy + PostgreSQL
- **Auth** : JWT Bearer token

---

## Structure du projet

```
resource-manager/
├── app/                        # Backend FastAPI
│   ├── main.py                 # Point d'entrée, middlewares, routers
│   ├── database.py             # Connexion SQLAlchemy, get_db()
│   ├── models/                 # Modèles ORM SQLAlchemy
│   │   ├── user.py
│   │   ├── room.py
│   │   ├── equipment.py
│   │   └── reservation.py
│   ├── schemas/                # Schémas Pydantic (validation I/O)
│   │   ├── user.py
│   │   ├── room.py
│   │   └── reservation.py
│   ├── routes/                 # Endpoints REST
│   │   ├── auth_routes.py      # POST /auth/register, /auth/login
│   │   ├── room_routes.py      # GET/POST /rooms
│   │   ├── equipment_routes.py # GET/POST /equipments
│   │   └── reservation_routes.py # CRUD /reservations
│   ├── services/
│   │   └── reservation_service.py  # Logique métier + détection conflits
│   └── utils/
│       └── security.py         # JWT, bcrypt, dépendances auth FastAPI
│
├── frontend/                   # Frontend React
│   ├── public/
│   ├── src/
│   │   ├── index.js            # Point d'entrée React + AuthProvider
│   │   ├── App.js              # Routing principal (react-router-dom)
│   │   ├── context/
│   │   │   └── AuthContext.js  # Contexte auth global (token, role, login/logout)
│   │   ├── hooks/
│   │   │   └── useReservations.js  # Hook : fetch, create, update, delete
│   │   ├── utils/
│   │   │   └── calendarHelpers.js  # Fonctions pures : couleurs, format, conflits
│   │   ├── services/
│   │   │   └── api.js          # API_URL centralisée + helpers fetch
│   │   └── components/
│   │       ├── Layout.js
│   │       ├── Navbar.js
│   │       ├── Sidebar.js
│   │       ├── Login.js
│   │       ├── CalendarView.js     # Calendrier principal
│   │       ├── ReservationModal.js # Modal de création
│   │       └── AdminDashboard.js
│   └── .env.example
│
├── scripts/
│   └── create_admin.py         # Script de création du premier admin
├── requirements.txt
├── .env.example
└── README.md
```

---

## Installation

### Prérequis

- Python 3.11+
- Node.js 18+
- PostgreSQL

### Backend

```bash
# Créer et activer l'environnement virtuel
python -m venv venv
source venv/bin/activate      # Windows : venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec DATABASE_URL, SECRET_KEY, ACCESS_TOKEN_EXPIRE_HOURS

# Appliquer les migrations (crée les tables en base)
alembic upgrade head

# Créer le premier compte admin
python scripts/create_admin.py

# Lancer le serveur
uvicorn app.main:app --reload
# API disponible sur http://localhost:8000
# Swagger UI sur http://localhost:8000/docs
```

### Frontend

```bash
cd frontend

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env si le backend tourne sur un port différent

# Installer les dépendances
npm install

# Lancer le serveur de développement
npm start
# App disponible sur http://localhost:3000
```

---

## Migrations (Alembic)

Les migrations sont versionnées dans `alembic/versions/`. Alembic remplace `Base.metadata.create_all()` — ne jamais utiliser ce dernier en production.

```bash
# Appliquer toutes les migrations en attente
alembic upgrade head

# Revenir à la migration précédente
alembic downgrade -1

# Revenir à l'état vide (supprimer toutes les tables)
alembic downgrade base

# Voir l'historique des migrations
alembic history

# Générer une nouvelle migration après modification d'un modèle
alembic revision --autogenerate -m "description_courte"
```

---

### Backend (`.env`)

| Variable | Description | Exemple |
|---|---|---|
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql://user:pass@localhost:5432/resource_manager` |
| `SECRET_KEY` | Clé secrète pour signer les JWT | Chaîne aléatoire longue |
| `ACCESS_TOKEN_EXPIRE_HOURS` | Durée de validité du token (heures) | `2` |

### Frontend (`frontend/.env`)

| Variable | Description | Exemple |
|---|---|---|
| `REACT_APP_API_URL` | URL de base du backend | `http://localhost:8000` |

---

## Rôles utilisateurs

| Rôle | Accès |
|---|---|
| `user` | Voir le calendrier, créer ses propres réservations |
| `admin` | Tout + modifier/supprimer toutes les réservations, accès au dashboard |

---

## API — Endpoints principaux

| Méthode | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | Non | Créer un compte |
| POST | `/auth/login` | Non | Obtenir un token JWT |
| GET | `/reservations` | Oui | Lister les réservations |
| POST | `/reservations` | Oui | Créer une réservation |
| PUT | `/reservations/{id}` | Admin | Modifier une réservation |
| DELETE | `/reservations/{id}` | Admin | Supprimer une réservation |
| GET | `/rooms` | Oui | Lister les salles |
| GET | `/equipments` | Oui | Lister les équipements |

Documentation complète disponible sur `/docs` (Swagger UI) après démarrage du backend.
