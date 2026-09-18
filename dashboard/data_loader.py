import streamlit as st
import pandas as pd
from sqlalchemy.orm import sessionmaker
from database.connection import engine
from models.city import City
from models.weather import WeatherData
from models.risk import Risk


def _cache_key():
    """Returns a value that changes to bust the cache when needed."""
    return pd.Timestamp.now().floor("min")


@st.cache_data(ttl=3600)
def load_data(_key=None):
    Session = sessionmaker(bind=engine)
    with Session() as session:
        query = session.query(
            City.name.label('city'),
            City.country,
            City.latitude,
            City.longitude,
            WeatherData.date,
            WeatherData.temp_max,
            WeatherData.temp_min,
            WeatherData.precipitation_sum,
            WeatherData.precipitation_probability_max,
            WeatherData.windspeed_max,
            WeatherData.windgusts_max,
            WeatherData.weathercode.label('weather_code'),
            Risk.temp_score,
            Risk.precip_score,
            Risk.wind_score,
            Risk.risk_score,
            Risk.risk_level,
        ).join(
            WeatherData, WeatherData.city_id == City.id
        ).join(
            Risk, Risk.weather_id == WeatherData.id
        )

        df = pd.read_sql(query.statement, session.bind)

    return df