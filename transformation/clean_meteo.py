import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transformation/clean_meteo.log'),
        logging.StreamHandler()
    ],
    force=True
)
logger = logging.getLogger(__name__)


def standardize_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_')
    )
    return df


def standardize_types(df):
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['city'] = df['city'].astype(str).str.strip()

    numeric_cols = [
        'temp_max', 'temp_min', 'precipitation_sum',
        'precipitation_probability_max', 'windspeed_max',
        'windgusts_max', 'weathercode', 'lat', 'lng'
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    bad_dates = df['date'].isnull().sum()
    if bad_dates > 0:
        logger.warning(f"{bad_dates} rows had invalid dates")

    for col in numeric_cols:
        bad = df[col].isnull().sum()
        if bad > 0:
            logger.warning(f"{bad} rows had invalid values in {col}")

    return df

def detect_duplicates(df):
    dupes = df.duplicated(subset=['city', 'date']).sum()
    if dupes > 0:
        logger.warning(f"{dupes} duplicate city+date rows found — keeping most recent")
        df = df.drop_duplicates(subset=['city', 'date'], keep='last')
    else:
        logger.info("No duplicate city+date rows found")
    return df

def clean_meteo(csv_path):
    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(df)} rows from {csv_path}")

    df = standardize_columns(df)
    df = standardize_types(df)
    df = detect_duplicates(df)

    logger.info(f"Standardization complete. dtypes:\n{df.dtypes}")              
    return df

if __name__ == "__main__":
    df = clean_meteo('./bronze/Meteo/meteo_forecast.csv')
    df.to_csv('./silver/meteo_clean.csv', index=False)
    print(df.dtypes)
    print(df.head())