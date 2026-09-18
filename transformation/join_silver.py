import logging
from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FILE_PATH = PROJECT_ROOT / "transformation" / "join_silver.log"

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

def join_silver(city_path , meteo_path ) :
    df_city = pd.read_csv(city_path)
    df_meteo = pd.read_csv(meteo_path)
    df_city = df_city.drop(columns=['lat', 'lng'])
    logger.info(f"Loaded {len(df_city)} villes, {len(df_meteo)} meteo rows")

    df = df_meteo.merge(
        df_city , 
        on='city' , 
        how='left',
    )
    
    unmatched = df[df['admin_name'].isnull()]['city'].unique() if 'admin_name' in df.columns else []
    if len(unmatched) > 0 :
        logger.warning(f"{len(unmatched)} cities in meteo not matched to villes: {list(unmatched)}")
    else :
        logger.info("All meteo cities matched to villes data")
    logger.info(f"Joined dataset shape: {df.shape}")
    return df 

if __name__ == "__main__" :
    df = join_silver('./silver/city_clean.csv' , './silver/meteo_clean.csv')
    df.to_csv('./silver/joined_city_meteo.csv' , index=False)
    print(df.head())

    