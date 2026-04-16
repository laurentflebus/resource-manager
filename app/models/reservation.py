from sqlalchemy import Column, Integer, DateTime, ForeignKey
from app.database import Base

class Reservation(Base):

    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=True)

    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)

    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=True)

    start_time = Column(DateTime, nullable=False)

    end_time = Column(DateTime, nullable=False)
