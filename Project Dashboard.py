# 🌍 GLOBAL TEMPERATURE STORY DASHBOARD 
import streamlit as st
import pandas as pd
import altair as alt

# ─── Page Config ────────────────────────────────────────────
st.set_page_config(
    page_title="Global Temperature Change",
    page_icon="🌍",
    layout="wide"
)

# ─── Hero Section ───────────────────────────────────────────
st.markdown(
    """
    <style>
        .hero {
            background-image: url('https://github.com/PReece11/Global-Temp/blob/main/ChatGPT%20Image%20Jul%2030,%202025,%2011_22_32%20AM.png?raw=true'); 
            background-size: cover; 
            padding: 100px 0;
            margin-bottom: 20px;
            color: white;
            text-align: center;
        }
        .description {
            text-align: center;
            line-height: 1.6;
            font-size: 18px;
        }
    </style>
    <div class="hero" role="region" aria-label="Header with Earth image and dashboard title">
        <h1>🌍 Global Temperature Change 🌡️</h1>
        <p>An interactive exploration of monthly and yearly global temperature trends.</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write(
    """
    <div class='description'>
        Explore how <strong>temperature changes over decades</strong> using interactive visualizations. 
        Hover over charts, filter by countries, or analyze seasonal patterns individually.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ─── Sidebar Navigation ─────────────────────────────────────
st.sidebar.title("Navigation")
st.sidebar.caption("🔑 Use keyboard ↑↓ or type to search options.")
page = st.sidebar.radio(
    "Go to:",
    ["Home", "Year-over-Year + Country Trends"],
    index=0
)

# ─── Data Load and Prep ─────────────────────────────────────
@st.cache_data

def load_data():
    df = pd.read_csv("Indicator_3_1_Climate_Indicators_Annual_Mean_Global_Surface_Temperature_577579683071085080.csv")
    year_cols = [c for c in df.columns if c.isdigit()]
    df_long = df.melt(
        id_vars=["Country", "ISO2", "ISO3", "Indicator", "Unit"],
        value_vars=year_cols,
        var_name="Year",
        value_name="TempChange"
    )
    df_long["Year"] = df_long["Year"].astype(int)
    df_long.sort_values(["Country", "Year"], inplace=True)
    return df_long

df_long = load_data()

# ─── Sidebar Filters ────────────────────────────────────────
if page != "Home":
    st.sidebar.header("🔍 Filters")
    countries = ["All"] + sorted(df_long["Country"].unique())
    years = ["All"] + sorted(df_long["Year"].unique())

    selected_country = st.sidebar.selectbox("Country", countries)
    selected_year = st.sidebar.selectbox("Year", years)

    filtered = df_long.copy()
    if selected_country != "All":
        filtered = filtered[filtered["Country"] == selected_country]
    if selected_year != "All":
        filtered = filtered[filtered["Year"] == selected_year]

# ─── Home Page ──────────────────────────────────────────────
if page == "Home":
    st.write("""
    ### About This Dashboard
    Over the past century, the Earth's surface temperature has experienced significant changes due to various natural and anthropogenic factors. This dashboard explores key global temperature trends, anomalies, and projections to provide insights into the ongoing climate challenges.

    **How Gases Affect Temperature**  
    Greenhouse gases, like carbon dioxide (CO2), methane (CH4), and water vapor, trap heat in the Earth's atmosphere. This natural process, called the greenhouse effect, maintains the Earth's habitable temperature. However, excessive emissions from human activities, including burning fossil fuels and deforestation, amplify this effect, leading to global warming and climate changes.

    Explore the visualizations to understand the impacts of these changes and potential mitigation strategies.
    """)

# ─── Year-over-Year + Country Trends ───────────────────────
elif page == "Year-over-Year + Country Trends":
    st.subheader("📈 Year-over-Year Change in Temperature")
    st.info("""
    This line chart shows how much **temperature change fluctuates year-over-year** for a selected country.
    - Helps detect acceleration or deceleration in warming.
    """)

    if selected_country == "All":
        st.warning("Please select a specific country to view Year-over-Year changes.")
    else:
        yoy_data = df_long[df_long["Country"] == selected_country].copy()
        yoy_data["YoY_Change"] = yoy_data["TempChange"].diff()

        line = alt.Chart(yoy_data).mark_line(point=True).encode(
            x=alt.X("Year:O"),
            y=alt.Y("YoY_Change:Q", title="Change from Previous Year (°C)"),
            color=alt.value("#f45b69"),
            tooltip=[
                alt.Tooltip("Year:O", title="Year"),
                alt.Tooltip("YoY_Change:Q", title="Year-over-Year Change (°C)", format=".3f")
            ]
        ).properties(
            width=800,
            height=450,
            title=f"Year-over-Year Temperature Change – {selected_country}"
        )

        st.altair_chart(line, use_container_width=True)

        st.markdown("### 🌡️ Temperature Changes by Year (Scatter Plot)")
        st.info("""
        This scatter plot shows temperature deviations from baseline values for selected countries over time.
        - **Purple = cooler**, **yellow = warmer** (colorblind-friendly).
        - Click a country to highlight trends; hover to view details.
        """)

        alt.data_transformers.disable_max_rows()
        sel_country = alt.selection_point(fields=["Country"], empty="all")

        scatter = (
            alt.Chart(yoy_data)
            .mark_circle(size=60)
            .encode(
                x=alt.X("Year:O", title="Year"),
                y=alt.Y("TempChange:Q", title="Temperature Change (°C)"),
                color=alt.Color(
                    "TempChange:Q",
                    scale=alt.Scale(scheme="plasma", domainMid=0),
                    legend=alt.Legend(title="Temp Change (°C)")
                ),
                opacity=alt.condition(sel_country, alt.value(1), alt.value(0.15)),
                tooltip=[
                    alt.Tooltip("Country:N", title="Country"),
                    alt.Tooltip("Year:O", title="Year"),
                    alt.Tooltip("TempChange:Q", title="Temperature Change (°C)")
                ]
            )
            .add_params(sel_country)
            .properties(
                height=500,
                width=800,
                title=f"Temperature Change Over Time – {selected_country}"
            )
        )

        st.altair_chart(scatter, use_container_width=True)

# ─── Footer ────────────────────────────────────────────────
st.markdown("---")
st.write(
    """
    <div style="text-align: center;" role="contentinfo" aria-label="Footer">
        Brought to you by <strong>Harrison, Paula and Roydan</strong>. 
        Advocates for official climate change.
    </div>
    """,
    unsafe_allow_html=True
)
