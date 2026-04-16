from pydantic import BaseModel
from datetime import datetime



class ReservationBase(BaseModel):
    room_id: int | None = None
    equipment_id: int | None = None
    start_time: datetime
    end_time: datetime

class ReservationCreate(ReservationBase):
    pass

class ReservationResponse(ReservationBase):
    id: int

    class Config:
        from_attributes = True