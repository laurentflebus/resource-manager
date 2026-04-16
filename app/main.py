from fastapi import FastAPI
from app.database import engine, Base
from app.models import *
from app.routes import room_routes, reservation_routes

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(room_routes.router)
app.include_router(reservation_routes.router)

@app.get("/")
def root():
    return {"message": "API Resource Manager running 🚀"}

# 👇 TEST DB (temporaire)
try:
    connection = engine.connect()
    print("✅ DB connectée")
    connection.close()
except Exception as e:
    print("❌ Erreur DB:", e)