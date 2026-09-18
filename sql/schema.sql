CREATE TABLE IF NOT EXISTS cities (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(100)    NOT NULL,
    country             VARCHAR(100)    NOT NULL,
    iso2                VARCHAR(2)      NOT NULL,
    admin_name          VARCHAR(100),
    latitude            NUMERIC(9, 6)   NOT NULL,
    longitude           NUMERIC(9, 6)   NOT NULL,
    capital             VARCHAR(100),
    population          INTEGER,
    population_proper   INTEGER,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS weather_data (
    id                              SERIAL PRIMARY KEY,
    city_id                         INTEGER NOT NULL REFERENCES cities(id),
    date                            TIMESTAMP NOT NULL,
    temp_max                        NUMERIC(5, 2),
    temp_min                        NUMERIC(5, 2),
    precipitation_sum               NUMERIC(5, 2),
    precipitation_probability_max   NUMERIC(5, 2),
    windspeed_max                   NUMERIC(5, 2),
    windgusts_max                   NUMERIC(5, 2),
    weathercode                     INTEGER,
    created_at                      TIMESTAMP DEFAULT NOW(),
    updated_at                      TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_city_date UNIQUE (city_id, date)  -- prevents duplicate forecasts on pipeline re-runs
);

CREATE TABLE IF NOT EXISTS risks (
    id          SERIAL PRIMARY KEY,
    weather_id  INTEGER NOT NULL REFERENCES weather_data(id),
    temp_score  NUMERIC(5, 2),
    precip_score NUMERIC(5, 2),
    wind_score  NUMERIC(5, 2),
    risk_score  NUMERIC(5, 2),
    risk_level  VARCHAR(20),
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_weather_city_id ON weather_data(city_id);
CREATE INDEX IF NOT EXISTS idx_weather_date ON weather_data(date);
CREATE INDEX IF NOT EXISTS idx_risks_weather_id ON risks(weather_id);
CREATE INDEX IF NOT EXISTS idx_risks_risk_level ON risks(risk_level);