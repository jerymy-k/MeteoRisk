SELECT c.name, MAX(w.temp_max) as peak_temp
FROM cities c
JOIN weather_data w ON c.id = w.city_id
GROUP BY c.name
ORDER BY peak_temp DESC
LIMIT 10;

select c.name , MAX(w.precipitation_sum) as peak_precipitation
FROM cities c   
JOIN weather_data w ON c.id = w.city_id
group by c.name
order by peak_precipitation desc
limit 10;

select c.name , ROUND(AVG(r.risk_score), 2) as avg_risk_score 
FROM cities c
JOIN weather_data w ON c.id = w.city_id
JOIN risks r ON w.id = r.weather_id
GROUP BY c.name
ORDER BY avg_risk_score DESC
LIMIT 10;

SELECT w.date, MAX(r.risk_score) as max_risk_score
FROM risks r
JOIN weather_data w ON r.weather_id = w.id
GROUP BY w.date
ORDER BY max_risk_score DESC;

select city_name , date , risk_score 
FROM (
    SELECT 
        c.name as city_name, 
        w.date, 
        r.risk_score,
        ROW_NUMBER() OVER (PARTITION BY c.id ORDER BY r.risk_score DESC) as rn
    FROM cities c
    JOIN weather_data w ON c.id = w.city_id
    JOIN risks r ON w.id = r.weather_id

)   ranked
WHERE rn = 1   
ORDER BY risk_score DESC;




