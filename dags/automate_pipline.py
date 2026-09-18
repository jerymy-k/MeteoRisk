from datetime import datetime
import os
import pandas as pd
from pathlib import Path
import subprocess
import sys
from airflow import DAG # ignore : this is a DAG file, not a script
from airflow.operators.python import PythonOperator # same 

from extraction.extract_villes import extract_villes
from extraction.extract_meteo import extract_meteo, save_forecast
from transformation.clean_city import clean_city
from transformation.clean_meteo import clean_meteo
from transformation.join_silver import join_silver
from transformation.feature_engineering import (
    categorize_temp,
    categorize_precipitation,
    categorize_wind,
    calculate_temp_score,
    calculate_precip_score,
    calculate_wind_score,
    calculate_risk_score,
    categorize_risk,
)

def task_extract_meteo():
    villes_path = Path(__file__).resolve().parents[1] / "bronze" / "City" / "MACity.csv"
    villes = pd.read_csv(villes_path)
    df = extract_meteo(villes)
    os.makedirs('./bronze/Meteo', exist_ok=True)
    path_to_save = Path(__file__).resolve().parents[1] / "bronze" / "Meteo" / "meteo_forecast.csv"
    save_forecast(df, path_to_save)


def task_clean_city():
    city_path = Path(__file__).resolve().parents[1] / "bronze" / "City" / "MACity.csv"
    df = clean_city(city_path)
    os.makedirs('./silver', exist_ok=True)
    path_to_save = Path(__file__).resolve().parents[1] / "silver" / "city_clean.csv"
    df.to_csv(path_to_save, index=False)


def task_clean_meteo():
    meteo_path = Path(__file__).resolve().parents[1] / "bronze" / "Meteo" / "meteo_forecast.csv"
    df = clean_meteo(meteo_path)
    os.makedirs('./silver', exist_ok=True)
    path_to_save = Path(__file__).resolve().parents[1] / "silver" / "meteo_clean.csv"
    df.to_csv(path_to_save, index=False)


def task_join_silver():
    os.makedirs('./silver', exist_ok=True)
    silver_city_path = Path(__file__).resolve().parents[1] / "silver" / "city_clean.csv"
    silver_meteo_path = Path(__file__).resolve().parents[1] / "silver" / "meteo_clean.csv"
    df = join_silver(silver_city_path, silver_meteo_path)
    path_to_save = Path(__file__).resolve().parents[1] / "silver" / "joined_city_meteo.csv"
    df.to_csv(path_to_save, index=False)


def task_feature_engineering():
    os.makedirs('./gold', exist_ok=True)
    joined_path = Path(__file__).resolve().parents[1] / "silver" / "joined_city_meteo.csv"
    df = pd.read_csv(joined_path)
    df = categorize_temp(df)
    df = categorize_precipitation(df)
    df = categorize_wind(df)
    df = calculate_temp_score(df)
    df = calculate_precip_score(df)
    df = calculate_wind_score(df)
    df = calculate_risk_score(df)
    df = categorize_risk(df)
    os.makedirs('./gold', exist_ok=True)
    path_to_save = Path(__file__).resolve().parents[1] / "gold" / "meteo_features.csv"
    df.to_csv(path_to_save, index=False)


def task_load_to_db():

    path_to_script = Path("/opt/airflow/MeteoRisk/load/load_to_db.py")
    subprocess.run([sys.executable, str(path_to_script)], check=True)

default_args = {
    'owner': 'meteorisk',
    'retries': 2,
}

with DAG(
    dag_id='meteorisk_pipeline',
    default_args=default_args,
    schedule_interval='0 6 * * *',
    start_date=datetime(2026, 9, 1),
    catchup=False,
    tags=['meteorisk'],
) as dag:

    t1 = PythonOperator(task_id='extract_meteo', python_callable=task_extract_meteo)
    t2 = PythonOperator(task_id='clean_city', python_callable=task_clean_city)
    t3 = PythonOperator(task_id='clean_meteo', python_callable=task_clean_meteo)
    t4 = PythonOperator(task_id='join_silver', python_callable=task_join_silver)
    t5 = PythonOperator(task_id='feature_engineering', python_callable=task_feature_engineering)
    t6 = PythonOperator(task_id='load_to_db', python_callable=task_load_to_db)

    t1 >> t2 >> t3 >> t4 >> t5 >> t6
