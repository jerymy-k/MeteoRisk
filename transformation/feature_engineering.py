import logging
from pathlib import Path
import pandas as pd
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FILE_PATH = PROJECT_ROOT / "transformation" / "feature_engineering.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(FILE_PATH),
        logging.StreamHandler()
    ],
    force=True
)

logger = logging.getLogger(__name__)

def categorize_temp(df):
    edges = [
        float('-inf'),
        18,
        30,
        38,
        float('inf')
    ]

    categories = [
        'froid',
        'doux',
        'chaud',
        'extreme'
    ]

    df['temp_category'] = pd.cut(
        df['temp_max'],
        bins=edges,
        labels=categories,
        right=False
    )

    return df

def categorize_precipitation(df):
    edges = [
        0,
        1,
        5,
        20,
        50,
        float('inf')
    ]

    categories = [
        'none',
        'light',
        'moderate',
        'heavy',
        'extreme'
    ]

    df['precip_category'] = pd.cut(
        df['precipitation_sum'],
        bins=edges,
        labels=categories,
        right=False
    )

    return df

def categorize_wind(df):
    edges = [
        0,
        20,
        30,
        40,
        50,
        70,
        float('inf')
    ]

    categories = [
        'calm',
        'light',
        'moderate',
        'strong',
        'very_strong',
        'extreme'
    ]

    df['wind_category'] = pd.cut(
        df['windspeed_max'],
        bins=edges,
        labels=categories,
        right=False
    )

    return df

def calculate_temp_score(df):
    edges = [
        float('-inf'),
        10,
        15,
        18,
        30,
        32,
        36,
        38,
        40,
        float('inf')
    ]

    scores = [
        100,
        70,
        40,
        0,
        20,
        40,
        70,
        90,
        100
    ]

    df['temp_score'] = pd.cut(
        df['temp_max'],
        bins=edges,
        labels=scores,
        right=False,
        ordered=False
    ).astype(int)

    return df

def calculate_precip_score(df):
    edges = [
        0,
        1,
        5,
        10,
        20,
        50,
        float('inf')
    ]

    scores = [
        0,
        20,
        40,
        60,
        80,
        100
    ]

    df['precip_score'] = pd.cut(
        df['precipitation_sum'],
        bins=edges,
        labels=scores,
        right=False
    ).astype(int)

    return df

def calculate_wind_score(df):

    wind_edges = [
        0,
        20,
        30,
        40,
        50,
        70,
        float('inf')
    ]

    wind_scores = [
        0,
        20,
        40,
        60,
        80,
        100
    ]

    gust_edges = [
        0,
        30,
        40,
        50,
        60,
        80,
        float('inf')
    ]

    gust_scores = [
        0,
        20,
        40,
        60,
        80,
        100
    ]

    df['windspeed_score'] = pd.cut(
        df['windspeed_max'],
        bins=wind_edges,
        labels=wind_scores,
        right=False
    ).astype(int)

    df['windgust_score'] = pd.cut(
        df['windgusts_max'],
        bins=gust_edges,
        labels=gust_scores,
        right=False
    ).astype(int)

    df['wind_score'] = df[
        ['windspeed_score', 'windgust_score']
    ].max(axis=1)

    return df

def calculate_risk_score(df):


    high_condition = (
        (df['precipitation_sum'] > 20) |
        (df['windgusts_max'] > 50) |
        (df['weathercode'].isin([45, 48]))
    )

    extreme_condition = (
        (df['precipitation_sum'] > 50) |
        (df['windgusts_max'] > 70) |
        (df['weathercode'].isin([95, 96, 99]))
    )

    df['risk_score'] = np.maximum(
        0.30 * df['temp_score'] + 0.40 * df['precip_score'] + 0.30 * df['wind_score'],
        np.where(extreme_condition, 90,
        np.where(high_condition, 60, 0))
    )

    return df

def categorize_risk(df):

    edges = [
        0,
        20,
        40,
        60,
        80,
        101
    ]

    categories = [
        'low',
        'moderate',
        'high',
        'very_high',
        'extreme'
    ]

    df['risk_level'] = pd.cut(
        df['risk_score'],
        bins=edges,
        labels=categories,
        right=False
    )

    return df

if __name__ == '__main__':

    input_file = './silver/joined_city_meteo.csv'
    output_file = './gold/meteo_features.csv'

    logger.info('Loading weather data')

    df = pd.read_csv(input_file)

    logger.info(f'Loaded {len(df)} rows')

    df = categorize_temp(df)
    df = categorize_precipitation(df)
    df = categorize_wind(df)

    df = calculate_temp_score(df)
    df = calculate_precip_score(df)
    df = calculate_wind_score(df)

    df = calculate_risk_score(df)

    df = categorize_risk(df)

    df.to_csv(
        output_file,
        index=False
    )

    logger.info(f'Feature engineering completed')
    logger.info(f'Saved result to {output_file}')

    print(
        df[
            [
                'date',
                'city',
                'temp_max',
                'temp_category',
                'temp_score',
                'precipitation_sum',
                'precip_category',
                'precip_score',
                'windspeed_max',
                'windgusts_max',
                'windspeed_score',
                'windgust_score',
                'wind_score',
                'risk_score',
                'risk_level'
            ]
        ].head(10)
    )