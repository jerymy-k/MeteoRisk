from sqlalchemy import Integer , String , Column , ForeignKey , DateTime , Numeric , func
from sqlalchemy.orm import relationship
from models.base import Base

class Risk(Base):
    __tablename__ = 'risks'

    id = Column(Integer, primary_key=True)
    weather_id = Column(Integer, ForeignKey('weather_data.id'), nullable=False)
    temp_score = Column(Numeric(5, 2), nullable=True)
    precip_score = Column(Numeric(5, 2), nullable=True)
    wind_score = Column(Numeric(5, 2), nullable=True)
    risk_score = Column(Numeric(5, 2), nullable=True)
    risk_level = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    weather_data = relationship("WeatherData", back_populates="risk")

    