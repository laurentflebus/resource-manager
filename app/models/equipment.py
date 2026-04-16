from sqlalchemy import Column, Integer, String
from app.database import Base

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    name= Column(String, nullable=False)
    quantity = Column(Integer, default=1)
