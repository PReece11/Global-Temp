# ───────────────────────────────────────────────────────────
#  🌍  GLOBAL TEMPERATURE STORY DASHBOARD  (Streamlit + Altair)
# ───────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import altair as alt

# ─── Page set‑up ────────────────────────────────────────────
st.set_page_config(page_title="Global Temperature Dashboard",
                   page_icon="🌍",
                   layout="wide")

st.title("🌍 Global Temperature Story  🌡️")

# ─── Hero-style Introduction Box ─────────────────────────────
st.markdown("""
<div style='background-color:#f0f8ff;padding:20px;border-radius:10px;'>
<h3>📘 About This Dashboard</h3>
<p>
This interactive dashboard explores long-term climate change trends through global surface temperature records, greenhouse gas contributions, and the differences between developed and developing nations.
</p>
</div>
""", unsafe_allow_html=True)

# ─── Quick Stats Summary (static for now) ────────────────────
st.markdown("""
<div style='display:flex;justify-content:space-around;margin:20px 0;font-weight:bold;font-size:1.1em;'>
    <div style='color:#e74c3c;'>🌡️ Global Avg Temp ↑<br><span style='font-size:1.5em;'>+1.1°C</span></div>
    <div style='color:#2980b9;'>🌊 Sea Level Rise<br><span style='font-size:1.5em;'>+100 mm</span></div>
    <div style='color:#27ae60;'>🟢 CO₂ Level<br><span style='font-size:1.5em;'>419 ppm</span></div>
</div>
""", unsafe_allow_html=True)

# ─── Data load & reshape ───────────────────────────────────
df = pd.read_csv("Indicator_3_1_Climate_Indicators_Annual_Mean_Global_Surface_Temperature_577579683071085080.csv")
year_cols = [c for c in df.columns if c.isdigit()]
df_long = df.melt(
    id_vars=["Country", "ISO2", "ISO3", "Indicator", "Unit"],
    value_vars=year_cols,
    var_name="Year",
    value_name="TempChange"
)
df_long["Year"] = df_long["Year"].astype(int)

# ─── Development Status Mapping ────────────────────────────
developed_iso3 = ["USA", "CAN", "GBR", "DEU", "FRA", "JPN",
                  "AUS", "NZL", "NOR", "SWE", "CHE"]
df_long["DevStatus"] = df_long["ISO3"].apply(lambda x: "Developed" if x in developed_iso3 else "Developing")

# ─── Sidebar Filters ───────────────────────────────────────
all_countries = ["All"] + sorted(df_long["Country"].unique())
year_min, year_max = int(df_long["Year"].min()), int(df_long["Year"].max())

with st.sidebar.expander("📊 Filters", expanded=True):
    chart_country = st.selectbox("Country", all_countries, key="chart_country")
    year_range = st.slider("Select Year Range",
                           min_value=year_min,
                           max_value=year_max,
                           value=(year_min, year_max),
                           step=1,
                           key="year_slider")

# ─── Filter Data ────────────────────────────────────────────
filtered_chart = df_long[
    (df_long["Year"] >= year_range[0]) & (df_long["Year"] <= year_range[1])
].copy()

if chart_country != "All":
    filtered_chart = filtered_chart[filtered_chart["Country"] == chart_country]

# ─── Altair Transformer ─────────────────────────────────────
alt.data_transformers.disable_max_rows()

# ─── Scatter Plot by Country ───────────────────────────────
sample = filtered_chart.groupby("Country")["TempChange"].mean().reset_index().rename(columns={"TempChange": "Avg_Change"})
if len(sample) > 100:
    sample = sample.sample(100, random_state=42)

scatter = (
    alt.Chart(sample)
    .mark_circle(size=100)
    .encode(
        x=alt.X("Avg_Change:Q", title="Simulated Avg Temp Change (°C)", scale=alt.Scale(zero=False)),
        y=alt.Y("Country:N", sort='-x', title=None),
        color=alt.condition(
            "datum.Avg_Change > 1.5", alt.value("#d62728"),
            alt.condition("datum.Avg_Change < 0.5", alt.value("#1f77b4"), alt.value("#999999"))
        ),
        tooltip=["Country:N", "Avg_Change:Q"]
    )
    .properties(
        width=800,
        height=600,
        title="Distribution of Simulated Country-Level Temperature Change"
    )
)

st.altair_chart(scatter, use_container_width=True)

# ─── Data Tab Preview ──────────────────────────────────────
st.markdown("### 📋 Explore the Filtered Dataset")
st.dataframe(filtered_chart)

st.download_button(
    label="📥 Download Filtered Temperature Data",
    data=filtered_chart.to_csv(index=False),
    file_name='filtered_temp_data.csv',
    mime='text/csv'
)

# ─── Footer ─────────────────────────────────────────────────
st.markdown("""
---
<small>Data sources: World Bank, Our World in Data | Layout inspired by <a href='https://science.nasa.gov/climate-change/' target='_blank'>NASA Climate Change</a>.</small>
""", unsafe_allow_html=True)
