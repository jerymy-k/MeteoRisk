# MeteoRisk — Data Model (UML / ER Diagram)

This diagram renders automatically on GitHub. It can also be pasted into [mermaid.live](https://mermaid.live) to export as PNG/SVG.

## Class Diagram (SQLAlchemy ORM)

```mermaid
classDiagram
    class City {
        +int id
        +str name
        +str country
        +str iso2
        +str admin_name
        +Decimal latitude
        +Decimal longitude
        +str capital
        +int population
        +int population_proper
        +datetime created_at
        +datetime updated_at
        +weather_data : List~WeatherData~
    }

    class WeatherData {
        +int id
        +int city_id
        +datetime date
        +Decimal temp_max
        +Decimal temp_min
        +Decimal precipitation_sum
        +Decimal precipitation_probability_max
        +Decimal windspeed_max
        +Decimal windgusts_max
        +int weathercode
        +datetime created_at
        +datetime updated_at
        +city : City
        +risk : Risk
    }

    class Risk {
        +int id
        +int weather_id
        +Decimal temp_score
        +Decimal precip_score
        +Decimal wind_score
        +Decimal risk_score
        +str risk_level
        +datetime created_at
        +datetime updated_at
        +weather_data : WeatherData
    }

    City "1" --> "many" WeatherData : has
    WeatherData "1" --> "1" Risk : has
```

## Notes

- `weather_data.(city_id, date)` has a **UNIQUE constraint** to prevent duplicate forecasts when the pipeline re-runs and updates an existing forecast for the same city/day instead.
- `risks.weather_id` is a 1-to-1 relationship with `weather_data` — each forecast row gets exactly one risk assessment.