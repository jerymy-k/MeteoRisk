import logging
import pandas as pd

logging.basicConfig(
    level = logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transformation/clean_city.log'),
        logging.StreamHandler()              
    ]
)

logger = logging.getLogger(__name__)

def standardize_columm(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ' , '_')
    )
    return df

def standardize_types(df) :
    df['city'] = df['city'].astype(str).str.strip()
    
    num_col = [
        'lat' , 'lng' , 'population' , 'population_proper'
    ]
    for col in num_col :
        df[col] = pd.to_numeric(df[col] , errors='coerce')
        
    for col in num_col :
        bad = df[col].isnull().sum()
        if bad > 0 :
            logger.warning(f'{bad} rows had invalid values in {col}')
    return df

def detect_duplicates(df) :
    dupes = df.duplicated(subset=['city']).sum()
    if dupes > 0 : 
        logger.warning(f"{dupes} duplicate city rows found - keeping most recent")
        df = df.drop_duplicates(subset=['city'] , keep='last')
    else :
        logger.info('No duplicate city rows found')
    return df
        
def clean_city(csv_path) :
    df = pd.read_csv(csv_path)
    logger.info(f'Loaded {len(df)} rows from {csv_path}')
    
    df = standardize_columm(df)
    df = standardize_types(df)
    df = detect_duplicates(df)
    
    logger.info(f"Standardization complete. dtype : \n {df.dtypes}")
    return df 

if __name__ == '__main__' :
    df = clean_city('./bronze/City/MACity.csv')
    df.to_csv('./silver/city_clean.csv' , index=False)
    print(df.dtypes)
    print(df.head())
    