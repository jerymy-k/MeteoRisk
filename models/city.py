from sqlalchemy import  Integer , String , Column , DateTime , Numeric ,func
from sqlalchemy.orm import relationship
from models.base import Base

class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    iso2 = Column(String(2), nullable=False)
    admin_name = Column(String(100), nullable=True)
    latitude = Column(Numeric(9, 6), nullable=False)
    longitude = Column(Numeric(9, 6), nullable=False)
    capital = Column(String(100), nullable=True)
    population = Column(Integer, nullable=True)
    population_proper = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    weather_data = relationship("WeatherData", back_populates="city")