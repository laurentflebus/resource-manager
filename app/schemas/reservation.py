from pydantic import BaseModel
from datetime import datetime
from typing import Optional



class ReservationBase(BaseModel):
    room_id: int | None = None
    equipment_id: int | None = None
    start_time: datetime
    end_time: datetime

class ReservationCreate(ReservationBase):
    pass

class ReservationUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    room_id: Optional[int] = None
    equipment_id: Optional[int] = None

class ReservationResponse(ReservationBase):
    id: int

    class Config:
        from_attributes = True