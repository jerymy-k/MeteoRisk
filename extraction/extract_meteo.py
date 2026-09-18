import logging 
import pandas as pd 
import time 
import requests
from extraction.extract_villes import extract_villes
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FILE_PATH = PROJECT_ROOT / "extraction" / "extract_meteo.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' , 
    handlers=[
        logging.FileHandler(FILE_PATH),
        logging.StreamHandler()
    ],
    force=True
)
logger = logging.getLogger(__name__)
apiOpenMeteo = "https://api.open-meteo.com/v1/forecast"
dailyVars = "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,windspeed_10m_max,windgusts_10m_max,weathercode"
def fetch_city(lat , lon , forecast_days = 7 , retries=5 , timeout=10 ):
    params = {
        'latitude': lat,
        'longitude': lon,
        'forecast_days': forecast_days,
        'daily': dailyVars,
        'timezone': 'auto',
    }
    for retrie in range(1 , retries+1) :
        try :
            response = requests.get(apiOpenMeteo , params=params , timeout=timeout)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Data fetched with success for lat={lat} , lon={lon} ")
            return data 
        except requests.exceptions.Timeout :    
            logger.warning(f"Time out on attempt {retrie} for lat= {lat} , lon={lon} ")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for lat={lat} , lon={lon} : {e}")
            return None 
        except requests.exceptions.RequestException as e :
            logger.error(f"Request failed for lat={lat} , lon={lon} : {e} ")
            return None 
        time.sleep(min(2 ** retrie, 30))
    logger.error(f"All retries failed for lat={lat} , lon={lon}")
    return None 

def extract_meteo(villes, forecast_days=7):
    all_records = []
    failed_records = []

    rename_map = {
        'time': 'date',
        'temperature_2m_max': 'temp_max',
        'temperature_2m_min': 'temp_min',
        'windspeed_10m_max': 'windspeed_max',
        'windgusts_10m_max': 'windgusts_max',
    }

    for _, row in villes.iterrows():
        city = row['city']
        lat, lng = row['lat'], row['lng']
        data = fetch_city(lat, lng, forecast_days=forecast_days)

        if data is None or 'daily' not in data:
            logger.error(f"No valid forecast data for {city}")
            failed_records.append(city)
            continue

        df_city = pd.DataFrame(data['daily']).rename(columns=rename_map)
        df_city['city'] = city
        df_city['lat'] = lat
        df_city['lng'] = lng
        all_records.append(df_city)

    if failed_records:
        logger.warning(f"{len(failed_records)} cities failed: {failed_records}")

    if not all_records:
        logger.error("No weather data was extracted for any city")
        return pd.DataFrame()

    df = pd.concat(all_records, ignore_index=True)
    logger.info(f"Extracted forecast for {df['city'].nunique()} cities, {len(df)} rows total")
    return df
        
def save_forecast(df, output_file):
    if df.empty:
        logger.warning("No data to save")
        return

    if os.path.exists(output_file):
        old_df = pd.read_csv(output_file)

        combined = pd.concat([old_df, df], ignore_index=True)

        combined = combined.drop_duplicates(
            subset=['city', 'date'],
            keep='last'
        )

        combined.to_csv(output_file, index=False)
    else:
        df.to_csv(output_file, index=False)

    logger.info(f"Forecast saved to {output_file}")


if __name__ == '__main__':
    villes = extract_villes('./bronze/City/MACity.csv')

    df = extract_meteo(villes)

    os.makedirs('./bronze/Meteo', exist_ok=True)

    save_forecast(
        df,
        './bronze/Meteo/meteo_forecast.csv'
    )

    print(df.head())