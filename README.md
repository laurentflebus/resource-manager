# 📦 Resource Manager API

API backend développée avec **FastAPI** permettant de gérer :

* 🏢 des salles
* 🧰 des équipements
* 📅 des réservations avec gestion des conflits

---

## 🚀 Fonctionnalités

* CRUD salles
* CRUD équipements (avec quantité disponible)
* Réservation de salle ou matériel
* Vérification des conflits :

  * ❌ double réservation de salle
  * ❌ dépassement du stock d’équipements

---

## 🛠️ Stack technique

* FastAPI
* SQLAlchemy
* PostgreSQL
* Uvicorn

---

## ⚙️ Installation

```bash
git clone https://github.com/ton-username/resource-manager.git
cd resource-manager
python -m venv venv
source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

---

## 🗄️ Configuration DB

Créer une base PostgreSQL :

```sql
CREATE DATABASE resource_db;
```

Configurer dans `database.py` :

```python
DATABASE_URL = "postgresql://user:password@localhost:5432/resource_db"
```

---

## ▶️ Lancer le projet

```bash
uvicorn app.main:app --reload
```

---

## 📚 Documentation API

Swagger disponible ici :

```
http://127.0.0.1:8000/docs
```

---

## 🧪 Tests à effectuer

### 🏢 Salle

* créer une réservation
* tenter un doublon → doit échouer

### 🧰 Équipement

* créer équipement (quantity = 2)
* faire 2 réservations → OK
* faire 3e réservation → ❌ refus

---

## 📦 Endpoints principaux

### Rooms

* GET /rooms
* POST /rooms

### Equipments

* GET /equipments
* POST /equipments

### Reservations

* GET /reservations
* POST /reservations

---

## 🧠 Logique métier

* Une réservation doit contenir :

  * soit une salle
  * soit un équipement
* Vérification des conflits via :

  * intervalle de temps
  * quantité disponible

---

## 🏁 Version

**v1.0** — MVP stable

---

## 👨‍💻 Auteur

Projet réalisé dans le cadre de la formation Odoo.
