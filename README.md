# MeteoRisk

Pipeline de données météo pour anticiper les perturbations de livraison dans les villes marocaines.

## Contexte

Une entreprise de livraison a besoin d'anticiper les risques météorologiques (fortes précipitations, vents, températures extrêmes) sur les prochains jours afin d'adapter l'organisation des livraisons. Ce projet construit un pipeline Bronze → Silver → Gold automatisé avec Airflow, qui calcule un score de risque météo par ville et par jour, exposé via un dashboard Streamlit.

## Sources de données

- **SimpleMaps** — CSV des villes marocaines et leurs coordonnées (`bronze/City/MACity.csv`)
- **Open-Meteo** — API de prévisions quotidiennes : températures max/min, précipitations et probabilité, vitesse et rafales de vent, weather code (`bronze/Meteo/meteo_forecast.csv`)

## Architecture

```
Open-Meteo API ─┐
                 ├─► Bronze (raw CSV) ─► Silver (cleaned + joined) ─► Gold (features + risk score) ─► PostgreSQL ─► Streamlit
SimpleMaps CSV ──┘
```

Orchestré par un DAG Airflow (`dags/automate_pipline.py`) exécuté quotidiennement (`0 6 * * *`), avec 2 retries par tâche.

```
extraction/        → récupération des données brutes (villes + météo)
transformation/     → nettoyage, jointure, feature engineering
database/           → connexion SQLAlchemy + création du schéma
models/             → modèles ORM (City, WeatherData, Risk)
load/               → chargement final vers PostgreSQL
dashboard/          → application Streamlit
dags/               → DAG Airflow
sql/                → script de création de schéma + requêtes d'analyse
```

## Modèle de données

Trois tables : `cities` → `weather_data` → `risks` (voir `sql/schema.sql` et `docs/uml_diagram.md`).

Une contrainte `UNIQUE(city_id, date)` sur `weather_data` évite les doublons lors des ré-exécutions du pipeline : si une prévision pour une ville/date existe déjà, elle est mise à jour plutôt que dupliquée.

## Weather Risk Score — justification

Le score de risque (0–100) est calculé en deux temps dans `transformation/feature_engineering.py`.

### 1. Scores par composante

**Température** (`temp_score`) — basé sur `temp_max`, en Celsius. Les seuils reflètent le fait que le risque n'est pas linéaire : un froid modéré ou une chaleur modérée sont peu risqués, mais les extrêmes (grand froid < 10°C, canicule > 38°C) sont pénalisés fortement.

| temp_max (°C) | score |
|---|---|
| < 10 | 100 |
| 10–15 | 70 |
| 15–18 | 40 |
| 18–30 | 0 (zone confortable) |
| 30–32 | 20 |
| 32–36 | 40 |
| 36–38 | 70 |
| 38–40 | 90 |
| > 40 | 100 |

**Précipitations** (`precip_score`) — basé sur `precipitation_sum` (mm), échelle croissante simple car plus il pleut, plus le risque de perturbation (routes, retards) augmente linéairement par palier :

| precipitation_sum (mm) | score |
|---|---|
| 0–1 | 0 |
| 1–5 | 20 |
| 5–10 | 40 |
| 10–20 | 60 |
| 20–50 | 80 |
| > 50 | 100 |

**Vent** (`wind_score`) — le maximum entre le score de vitesse moyenne (`windspeed_max`) et le score de rafales (`windgusts_max`), car les rafales isolées peuvent être plus dangereuses que la vitesse moyenne (ex. deux-roues, structures légères).

### 2. Score final

```python
risk_score = max(
    0.30 * temp_score + 0.40 * precip_score + 0.30 * wind_score,
    90 if extreme_condition else 60 if high_condition else 0
)
```

- **Pondération** : les précipitations pèsent le plus (40%) car c'est le facteur le plus directement perturbateur pour une flotte de livraison (routes inondées, visibilité). Température et vent sont pondérés égal (30% chacun).
- **Plancher (`max` avec conditions extrêmes)** : certaines conditions sont dangereuses même si la moyenne pondérée reste modérée — par exemple un `weathercode` d'orage (95, 96, 99) ou des rafales > 70 km/h forcent le score à au moins 90, même si température et précipitations sont normales ce jour-là.
  - `high_condition` : précipitations > 20mm OU rafales > 50 km/h OU brouillard (weathercode 45/48) → score plancher 60
  - `extreme_condition` : précipitations > 50mm OU rafales > 70 km/h OU orage (weathercode 95/96/99) → score plancher 90

### 3. Catégorisation finale (`risk_level`)

| risk_score | niveau |
|---|---|
| 0–20 | low |
| 20–40 | moderate |
| 40–60 | high |
| 60–80 | very_high |
| 80–100 | extreme |

## Installation et exécution

### Prérequis
- Docker Desktop

### Démarrage

```bash
docker compose up --build
```

Cela démarre trois services :
- **PostgreSQL** (`postgres_MR`) — port `5432`
- **Airflow** (webserver + scheduler) — port `8080`
- **Streamlit** (dashboard) — port `8501`

### Accès
- Airflow UI : http://localhost:8080 (user/password définis dans `docker-compose.yml`)
- Dashboard : http://localhost:8501

### Déclencher le pipeline
Dans l'UI Airflow, activer et déclencher le DAG `meteorisk_pipeline`. Il exécute dans l'ordre :
`extract_meteo → clean_city → clean_meteo → join_silver → feature_engineering → load_to_db`

### Requêtes SQL d'analyse
Voir `sql/analysis_queries.sql` — 6 requêtes répondant aux questions métier (villes les plus chaudes, précipitations les plus fortes, risque moyen le plus élevé, périodes à risque maximal, pic de risque par ville, résumé global).

## Dashboard

Le dashboard Streamlit (`dashboard/app.py`) permet de filtrer par ville, niveau de risque et plage de dates, et affiche :
- Évolution du risk score dans le temps par ville
- Plage de températures dans le temps
- Répartition moyenne des composantes du risque
- Risque moyen par ville
- Table de données brute filtrable

*(Captures d'écran à ajouter ici)*

## Gestion des erreurs

- Extraction : gestion des timeouts et erreurs HTTP lors des appels à l'API Open-Meteo
- Airflow : `retries: 2` par tâche par défaut
- Base de données : contrainte d'unicité `(city_id, date)` empêchant les doublons lors des ré-exécutions
