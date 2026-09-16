from sqlalchemy import  Integer , Column , ForeignKey , DateTime , Numeric , func , UniqueConstraint
from sqlalchemy.orm import relationship 
from models.base import Base

class WeatherData(Base):
    __tablename__ = 'weather_data'

    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    temp_max = Column(Numeric(5, 2), nullable=True)
    temp_min = Column(Numeric(5, 2), nullable=True)
    precipitation_sum = Column(Numeric(5, 2), nullable=True)
    precipitation_probability_max = Column(Numeric(5, 2), nullable=True)
    windspeed_max = Column(Numeric(5, 2), nullable=True)
    windgusts_max = Column(Numeric(5, 2), nullable=True)
    weathercode = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    city = relationship("City", back_populates="weather_data")
    risk = relationship("Risk", back_populates="weather_data", uselist=False)
    __table_args__ = (UniqueConstraint(city_id, date),)