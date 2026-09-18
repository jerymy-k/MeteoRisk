import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import altair as alt
from data_loader import load_data, _cache_key

# --- Page Config ---
st.set_page_config(
    page_title="MeteoRisk Dashboard",
    page_icon="⛅",
    layout="wide"
)

st.title("MeteoRisk Dashboard")

# --- Load Data ---
df = load_data(_cache_key())

if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])

cols_needed = ['city', 'country', 'date', 'temp_max', 'temp_min', 'temp_score',
               'precip_score', 'wind_score', 'weather_code', 'risk_score', 'risk_level']
data = df[[c for c in cols_needed if c in df.columns]].copy()

# --- Sidebar Filters ---
with st.sidebar:
    st.header("Filters")

    all_cities = sorted(data['city'].dropna().unique())
    selected_cities = st.multiselect("Cities", all_cities, default=all_cities)

    if 'risk_level' in data.columns:
        levels = sorted(data['risk_level'].dropna().unique())
        selected_levels = st.multiselect("Risk Levels", levels, default=levels)
    else:
        selected_levels = []

    if 'date' in data.columns and not data['date'].empty:
        min_d, max_d = data['date'].min().date(), data['date'].max().date()
        date_range = st.date_input("Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    else:
        date_range = None

# --- Apply Filters ---
filtered_df = data[data['city'].isin(selected_cities)].copy()

if selected_levels and 'risk_level' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['risk_level'].isin(selected_levels)]

if date_range and len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['date'].dt.date >= date_range[0]) &
        (filtered_df['date'].dt.date <= date_range[1])
    ]

if filtered_df.empty:
    st.warning("No data matches the current filters. Try widening your selection.")
    st.stop()

# --- Basic KPIs ---
col1, col2, col3 = st.columns(3)
col1.metric("Cities", filtered_df['city'].nunique())
col2.metric("Avg Risk Score", f"{filtered_df['risk_score'].mean():.1f}")
col3.metric("Max Temp (°C)", f"{filtered_df['temp_max'].max():.1f}")

st.markdown("---")

# --- Chart 1: Risk Score Over Time ---
st.subheader("Risk Score Over Time")
line_chart = alt.Chart(filtered_df).mark_line(point=True).encode(
    x='date:T',
    y='risk_score:Q',
    color='city:N',
    tooltip=['city', 'date', 'risk_score', 'risk_level']
).properties(height=300)
st.altair_chart(line_chart, use_container_width=True)

# --- Chart 2: Temperature Range Over Time ---
st.subheader("Temperature Range Over Time")
temp_df = filtered_df.melt(
    id_vars=['date', 'city'],
    value_vars=['temp_max', 'temp_min'],
    var_name='Metric',
    value_name='Temp'
)
temp_chart = alt.Chart(temp_df).mark_line().encode(
    x='date:T',
    y='Temp:Q',
    color='Metric:N',
    strokeDash='city:N',
    tooltip=['city', 'date', 'Metric', 'Temp']
).properties(height=300)
st.altair_chart(temp_chart, use_container_width=True)

# --- Chart 3: Average Risk Component Breakdown ---
st.subheader("Average Risk Component Breakdown")
drivers = filtered_df[['temp_score', 'precip_score', 'wind_score']].mean().reset_index()
drivers.columns = ['Component', 'Score']
bar_chart = alt.Chart(drivers).mark_bar().encode(
    x='Component:N',
    y='Score:Q',
    tooltip=['Component', 'Score']
).properties(height=300)
st.altair_chart(bar_chart, use_container_width=True)

# --- Chart 4: Risk Score by City (Average) ---
st.subheader("Average Risk Score by City")
city_avg = filtered_df.groupby('city')['risk_score'].mean().reset_index()
city_bar = alt.Chart(city_avg).mark_bar().encode(
    x='city:N',
    y='risk_score:Q',
    tooltip=['city', 'risk_score']
).properties(height=300)
st.altair_chart(city_bar, use_container_width=True)

# --- Data Table ---
st.subheader("Raw Data")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)