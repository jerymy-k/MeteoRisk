import pandas as pd
from sqlalchemy.orm import sessionmaker
from database.connection import engine
from models.city import City
from models.weather import WeatherData
from models.risk import Risk

Session = sessionmaker(bind=engine)
session = Session()

df = pd.read_csv('./gold/meteo_features.csv')

for _, row in df.iterrows():
    city = session.query(City).filter_by(name=row['city']).first()
    if not city:
        city = City(
            name=row['city'],
            country=row['country'],
            iso2=row['iso2'],
            latitude=row['lat'],
            longitude=row['lng']
        )
        session.add(city)
        session.flush()

    weather = session.query(WeatherData).filter_by(
        city_id=city.id,
        date=row['date']
    ).first()

    if weather:
        continue

    weather = WeatherData(
        city_id=city.id,
        date=row['date'],
        temp_max=row['temp_max'],
        temp_min=row['temp_min'],
        precipitation_sum=row['precipitation_sum'],
        precipitation_probability_max=row['precipitation_probability_max'],
        windspeed_max=row['windspeed_max'],
        windgusts_max=row['windgusts_max'],
        weathercode=row['weathercode'],
    )
    session.add(weather)
    session.flush()

    risk = Risk(
        weather_id=weather.id,
        temp_score=row['temp_score'],
        precip_score=row['precip_score'],
        wind_score=row['wind_score'],
        risk_score=row['risk_score'],
        risk_level=row['risk_level'],
    )
    session.add(risk)

session.commit()
session.close()
