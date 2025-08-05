# 🌍 GLOBAL TEMPERATURE STORY DASHBOARD 
import streamlit as st
import pandas as pd
import altair as alt

# ─── Page Config ────────────────────────────────────
st.set_page_config(
    page_title="Global Temperature Change",
    page_icon="🌍",
    layout="wide"
)

# ─── Hero Section ─────────────────────────
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
        <p>An interactive exploration of global temperature trends.</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write(
    """
    <div class='description'>
        Explore how <strong>temperature changes over decades</strong> using interactive visualizations. 
        Hover over charts, filter by countries, or analyze warming gases individually.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ─── Sidebar Navigation ────────────────────────────
st.sidebar.title("Navigation")
st.sidebar.caption("""
🔑 Use keyboard ↑↓ or type to search options. 
Use this menu to switch between sections of the dashboard:
- **Home**: Overview of global temperature trends
- **Explore Trends**: Yearly patterns, variability, and status comparisons
- **Warming Gases**: Contributions by greenhouse gases and sources
- **Global Warming Contribution**: Trends in how developed vs. developing countries have contributed to global warming.
- **Chat Assistant**: Ask questions like "Which country warmed fastest in 1998?"

🌓 **Note**: This dashboard is best viewed in **dark mode** for optimal readability and contrast.
""")
page = st.sidebar.radio(
    "Go to:",
    ["Home", "Explore Trends", "Warming Gases", "Global Warming Contribution", "Chat Assistant"],  
    index=0
)
# ─── Ensuring all the nations are consistant across all df ─────────────────
# loading all df that will be used in the dashboard
df_gas = pd.read_csv('global-warming-by-gas-and-source.csv')
df_contribution = pd.read_csv('contributions-global-temp-change.csv')
df_monthly = pd.read_csv("df_monthly_long.csv")
df_indicator = pd.read_csv("Indicator_3_1_Climate_Indicators_Annual_Mean_Global_Surface_Temperature_577579683071085080.csv")

# Creating lists of nations
df_gas_list = list(df_gas['Entity'].unique())
df_contribution_list = list(df_contribution['Entity'].unique())
df_monthly_list = list(df_monthly['Entity'].unique())
df_indicator_list = list(df_indicator['Country'].unique())

list_of_all_countries = [nation for nation in df_gas_list if nation in df_contribution_list and nation in df_contribution_list and nation in df_monthly_list and nation in df_indicator_list]


# ─── Data Load and Prep ─────────────────
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

    # Add DevStatus 
    developed_iso3 = ["USA", "CAN", "GBR", "DEU", "FRA", "JPN", "AUS", "NZL", "NOR", "SWE", "CHE"]
    df_long["DevStatus"] = df_long["ISO3"].apply(lambda x: "Developed" if x in developed_iso3 else "Developing")

    return df_long

df_long = load_data()

# ─── Warming Gases Page ───────
@st.cache_data
def prepare_gas_data(df2, dev_year_range, chart_country):
   
    # Filter the DataFrame based on the selected year range
    df2_filtered = df2[
        (df2["Year"] >= dev_year_range[0]) &
        (df2["Year"] <= dev_year_range[1])
    ].copy()

    # Function to get gas data for a specific entity
    def gas_data(entity):
        name = "World" if entity == "All" else entity
        return df2_filtered[df2_filtered["Entity"] == name].drop(columns=["Code"]).copy()

    # Define a mapping for gases and their sources
    gas_mapping = {
        "nitrous oxide": {
            "fossil fuels": "N2O_FF&I",
            "default": "N2O_AgLU"
        },
        "methane": {
            "fossil fuels": "CH4_FF&I",
            "default": "CH4_AgLU"
        },
        "fossil fuels": "CO2_FF&I",
        "default": "CO2_AgLU"
    }

    # Shorten column names using the mapping
    gas_cols = [c for c in df2.columns if c.startswith("Change in")]
    
    # Creating mapping labels
    shortened_columns = {
        col: (
            "N₂O (Fossil Fuels & Industry)" if "nitrous oxide" in col and "fossil fuels" in col else
            "N₂O (Agriculture & Land Use)" if "nitrous oxide" in col else
            "CH₄ (Fossil Fuels & Industry)" if "methane" in col and "fossil fuels" in col else
            "CH₄ (Agriculture & Land Use)" if "methane" in col else
            "CO₂ (Fossil Fuels & Industry)" if "fossil fuels" in col else 
            "CO₂ (Agriculture & Land Use)"
        )
        for col in gas_cols
    }

    # Get the gas data and rename columns
    gas_df = gas_data(chart_country)

    gas_df = gas_df.rename(columns=shortened_columns)

    # Melt the DataFrame for visualization
    gas_long = gas_df.melt(
        id_vars="Year",
        value_vars=list(shortened_columns.values()),
        var_name="series",
        value_name="Temp Change"
    )

    return gas_long 

# Monthly average temperature data
@ st.cache_data
def load_monthly_data():
    df_monthly = pd.read_csv("df_monthly_long.csv")
    df_monthly['Date'] = pd.to_datetime(df_monthly[['Year', 'Month']].assign(DAY=1)) # Adding a date column for better plotting
    df_monthly.rename(columns={'Mean_Temp':'Monthly Average Temperature (°C)',}, inplace=True)

    # Creating new yearly averages column
    yearly_averages = df_monthly.groupby(['Year','Entity'])["Monthly Average Temperature (°C)"].agg('mean').reset_index().rename(columns={"Monthly Average Temperature (°C)": "Yearly Average Temperature (°C)"})
    
    # Merging
    df_monthly = pd.merge(df_monthly, yearly_averages, on=['Year','Entity'], how='left')

    return df_monthly

@st.cache_data
def load_contribution_df():
    df_contribution = pd.read_csv('contributions-global-temp-change.csv')
    df_overview = df_contribution[df_contribution['Entity'].isin(['OECD (Jones et al.)', 'Least developed countries (Jones et al.)'])]
    df_overview = df_overview[(df_overview['Year']>= 1961) & (df_overview['Year']<= 2024)]
    # Creating line chart of individual OECD Nations
    oecd_list = [
        "Australia", "Austria", "Belgium", "Canada", "Chile", "Colombia", "Costa Rica",
        "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Germany", "Greece",
        "Hungary", "Iceland", "Ireland", "Israel", "Italy", "Japan", "Latvia", "Lithuania",
        "Luxembourg", "Mexico", "Netherlands", "New Zealand", "Norway", "Poland", "Portugal",
        "Slovakia", "Slovenia", "South Korea", "Spain", "Sweden", "Switzerland", "Turkey",
        "United Kingdom", "United States"]



    ldc_countries = [
        # Africa (32)
        "Angola", "Benin", "Burkina Faso", "Burundi", "Central African Republic", "Chad",
        "Comoros", "Democratic Republic of the Congo", "Djibouti", "Eritrea", "Ethiopia",
        "Gambia", "Guinea", "Guinea-Bissau", "Lesotho", "Liberia", "Madagascar", "Malawi",
        "Mali", "Mauritania", "Mozambique", "Niger", "Rwanda", "Senegal", "Sierra Leone",
        "Somalia", "South Sudan", "Sudan", "Togo", "Uganda", "United Republic of Tanzania", "Zambia",

        # Asia (8)
        "Afghanistan", "Bangladesh", "Cambodia", "Lao People’s Democratic Republic",
        "Myanmar", "Nepal", "Timor-Leste", "Yemen",

        # Pacific (3)
        "Kiribati", "Solomon Islands", "Tuvalu",

        # Caribbean (1)
        "Haiti"]
        ######
    # Creating a LDC df
    df_contribution_lcd = df_contribution[df_contribution['Entity'].isin(ldc_countries)]
    df_contribution_lcd = df_contribution_lcd[(df_contribution_lcd['Year'] >= 1961) & (df_contribution_lcd['Year'] <= 2024)]
        
    # Groupby to get top 10
    group = df_contribution_lcd.groupby('Entity')['Share of contribution to global warming'].mean().sort_values(ascending=False)

    # Top 10 countries
    top_10_countries_LDC = group.reset_index().iloc[:10]

    # Creating a list of top 10
    top_10_countries_LDC = list(top_10_countries_LDC['Entity'].unique())

    # Filtering the df again
    df_contribution_lcd = df_contribution_lcd[df_contribution_lcd['Entity'].isin(top_10_countries_LDC)]

    ######
        
    # Creating a OECD df
    df_contribution_oecd = df_contribution[df_contribution['Entity'].isin(oecd_list)]
    df_contribution_oecd = df_contribution_oecd[(df_contribution_oecd['Year'] >= 1961) & (df_contribution_oecd['Year'] <= 2024)]
        
    # Groupby to get top 10
    group = df_contribution_oecd.groupby('Entity')['Share of contribution to global warming'].mean().sort_values(ascending=False)

    # Top 10 countries
    top_10_countries = group.reset_index().iloc[:10]

    # Creating a list of top 10
    top_10_countries_list = list(top_10_countries['Entity'].unique())

    # Filtering OECD df to get top 10
    df_contribution_oecd = df_contribution_oecd[df_contribution_oecd['Entity'].isin(top_10_countries_list)]

    # Return df
    return df_overview, df_contribution_lcd, df_contribution_oecd




# ─── Home Page ───────────────────────────── 
if page == "Home":
    st.write("""
    ### About This Dashboard
    Over the past century, the Earth's surface temperature has experienced significant changes due to various natural and anthropogenic factors. This dashboard explores key global temperature trends, anomalies, and projections to provide insights into the ongoing climate challenges.

    **How Gases Affect Temperature**  
    Greenhouse gases such as carbon dioxide (CO₂), methane (CH₄), and nitrous oxide (N₂O) trap heat in the Earth's atmosphere. This natural process, called the **greenhouse effect**, maintains the Earth's habitable temperature. However, excessive emissions from human activities, including burning fossil fuels and deforestation, amplify this effect, leading to global warming and climate change. 

    Head to the sidebar to explore our visualizations and learn more about the impacts of these changes and potential mitigation strategies.
    """)
    
# ─── Explore Trends Page Tabs ─────────────────────────────
if page == "Explore Trends":
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Year-over-Year", "🌡️ Scatter Plot", "🔻 Variability", "🌍 Country Status"])

    # ─── Sidebar Filters ───────────────    
    st.sidebar.header("🔍 Filters")
    countries = ["All"] + sorted(list_of_all_countries)
    years = sorted(df_long["Year"].unique())  # Keep years available if needed

    selected_country = st.sidebar.selectbox("Country", countries)
    
    year_min, year_max = int(df_long["Year"].min()), int(df_long["Year"].max())
    dev_year_range = st.sidebar.slider("Year Range",
                               min_value=year_min,
                               max_value=year_max,
                               value=(year_min, year_max),
                               step=1,
                               key="dev_year_range")  # Optional: keep if you want to filter by year

    # Filter the DataFrame based on selected country and year
    filtered = df_long.copy()



    # ─── Tab 1: Year-over-Year Changes ─────────────────────
    with tab1:
        
        st.subheader("📈 Historical Year-over-Year Temperature Changes")
        
        st.write("""
        **Explore the interactive visualization below!** 

        - **Hover** over the data points in both the line and scatter plots to see detailed information about the **Year**, **Temperature Change (°C)**, and **Country**.
        - **Select** specific countries in the scatter plot to highlight their temperature trends. The line chart will update to show the year-over-year changes for the selected country.
        - **Analyze** the relationship between year-over-year changes (line) and overall temperature trends (scatter points) to identify patterns and anomalies.
        - Use **zoom and pan** features with the **"🔍 Filters"** sidebar to focus on specific time periods for a more detailed examination.
        - To return to viewing all countries, simply **deselect** any highlighted points in the scatter plot.

        Enjoy exploring the temperature trends!
        """)

        # Sample Countries Helper
        def get_sample_countries(df, n=10, min_years=20):
            country_counts = (
                df.dropna(subset=["TempChange"])
                .groupby("Country")["Year"]
                .count()
                .reset_index(name="count")
            )
            top_countries = country_counts[country_counts["count"] >= min_years].sort_values("count", ascending=False).head(n)
            return top_countries["Country"].tolist()

        if selected_country == "All":
            # Filering years range
            df_long = df_long[(df_long["Year"] >= dev_year_range[0]) & (df_long["Year"] <= dev_year_range[1])]

            # Creating a selecting interaction
            sel_country = alt.selection_point(on='pointerover', fields=["Country"], nearest=True, empty="all")

            # Get sample countries for visualization
            sample_countries = get_sample_countries(df_long)
            yoy_data = df_long[df_long["Country"].isin(sample_countries)].copy()
            yoy_data["YoY_Change"] = yoy_data.groupby("Country")["TempChange"].diff()
            scatter_data = df_long[df_long["Country"].isin(sample_countries)]

            # Create line chart for year-over-year changes

            base = alt.Chart(yoy_data).encode(
                x=alt.X("Year:O"),
                y=alt.Y("YoY_Change:Q", title="Change from Previous Year (°C)"),
            ).add_params(sel_country)

            select_plot = base.mark_circle().encode(
                opacity = alt.value(0),
                tooltip=['Year', 'Country', 'YoY_Change']
            )

            line_plot= base.mark_line().encode(
                color='Country:N',
                opacity=alt.condition(sel_country, alt.value(1), alt.value(0.15)),
                tooltip=['Year', 'Country', 'YoY_Change']
            ).add_params(sel_country).properties(title="Year-over-Year Change – Sample Countries", height=350, width=800)

            chart = alt.layer(select_plot + line_plot)


            # line = alt.Chart(yoy_data).mark_line(point=True).encode(
            #     x=alt.X("Year:O"),
            #     y=alt.Y("YoY_Change:Q", title="Change from Previous Year (°C)"),
            #     color="Country:N",
            #     opacity=alt.condition(sel_country, alt.value(1), alt.value(0.15)),
            #     tooltip=["Year", "Country", "YoY_Change"]
            # ).add_params(sel_country).properties(title="Year-over-Year Change – Sample Countries", height=350, width=800)

        else:
            df_long = df_long[(df_long["Year"] >= dev_year_range[0]) & (df_long["Year"] <= dev_year_range[1])]
            
            # Creating a selecting interaction
            sel_country = alt.selection_point(on='pointerover', fields=["Country"], nearest=True, empty="all")

            # Filter data for the selected country
            yoy_data = df_long[df_long["Country"] == selected_country].copy()
            yoy_data["YoY_Change"] = yoy_data["TempChange"].diff()
            scatter_data = df_long[df_long["Country"] == selected_country]

            # Create line chart for year-over-year changes
            chart = alt.Chart(yoy_data).mark_line(point=True).encode(
                x=alt.X("Year:O"),
                y=alt.Y("YoY_Change:Q", title="Change from Previous Year (°C)"),
                color=alt.value("#f45b69"),
                opacity= alt.condition(sel_country, alt.value(1), alt.value(0.15)),
                tooltip=["Year", "YoY_Change"]
            ).add_params(sel_country).properties(title=f"Year-over-Year Change – {selected_country}", height=350, width=800)

        sel_country = alt.selection_point(fields=["Country"], empty="all")

        # Removing scatter plot for now
        # scatter = alt.Chart(scatter_data).mark_circle(size=60).encode(
        #     x=alt.X("Year:O", title="Year"),
        #     y=alt.Y("TempChange:Q", title="Temperature Change (°C)"),
        #     color=alt.Color("TempChange:Q", scale=alt.Scale(scheme="reds")),
        #     opacity=alt.condition(sel_country, alt.value(1), alt.value(0.15)),
        #     tooltip=["Country", "Year", "TempChange"]
        # ).add_params(sel_country).properties(title="Raw Temperature Change", height=350, width=800)

        st.altair_chart(chart)


    # ─── Tab 2: Temperature Scatter Plot ───────────────────
    with tab2:
        st.subheader("🌡️ Temperature Change Scatter Plot by Country")

        st.write("""
        This scatter plot shows the **actual annual temperature change** for each country over time.
        Use the interactive legend and selection tool to highlight a country and explore its data.
        """)

        if selected_country == "All":
            scatter_data_2 = df_long[df_long["Country"].isin(df_long["Country"].unique()[:10])]
        else:
            scatter_data_2 = df_long[df_long["Country"] == selected_country]

        
        sel_country_2 = alt.selection_point(on='pointerover', fields=["Country"], nearest=True, empty="all")

        scatter_chart = alt.Chart(scatter_data_2).mark_circle(size=60).encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("TempChange:Q", title="Temperature Change (°C)"),
            color=alt.Color("TempChange:Q" if selected_country == "All" else "TempChange:Q", 
                            scale=alt.Scale(scheme="viridis")),
            opacity=alt.condition(sel_country_2, alt.value(1), alt.value(0.15)),
            tooltip=["Country", "Year", "TempChange"]
        ).add_params(sel_country_2).properties(
            width=800,
            height=450,
            title="Annual Temperature Change by Country",autosize=alt.AutoSizeParams(
            type='fit-x',
            contains='padding',
            resize=True
        ))

        st.altair_chart(scatter_chart, use_container_width=True)

        # Creating monthly temperature chart

        # Load monthly data
        df_monthly = load_monthly_data()

        # Filter monthly data based on selected country
        if selected_country == "All":
            df_monthly = df_monthly[df_monthly["Entity"]== 'World']
            name = selected_country
        else:
            df_monthly = df_monthly[df_monthly["Entity"] == selected_country]
            name = selected_country
        # Create a selection for year range
        df_monthly = df_monthly[(df_monthly["Year"] >= dev_year_range[0]) & (df_monthly["Year"] <= dev_year_range[1])]

        # Creating an interactive selection for year
        sel_year = alt.selection_point(on='pointerover', fields=['Year'], nearest=True, empty=True)
       
        base = alt.Chart(df_monthly).encode(
             x=alt.X("Month_named:N", 
            sort=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], title='Month'), #axis=alt.Axis(labelAngle=0)),
            y="Monthly Average Temperature (°C):Q")
    
        points = base.mark_circle().encode(
            opacity=alt.value(0),
            tooltip=["Year", "Monthly Average Temperature (°C)"]
        ).add_params(
            sel_year
        )
        lines = base.mark_line().encode(
            color=alt.Color("Yearly Average Temperature (°C)",scale=alt.Scale(scheme='viridis'), legend=alt.Legend(title="Yearly Average Temperature(°C)")),
            opacity=alt.condition(sel_year, alt.value(1), alt.value(0.20)),
            tooltip=["Year", "Monthly Average Temperature (°C)"]
        ).properties(
            width=750, height=400
        ).interactive()

        
        monthly_line = alt.layer(points + lines).properties(autosize=alt.AutoSizeParams(
            type='fit-x',
            contains='padding',
            resize=True))

        #st.subheader("Explore how how the average monthly temperature have gotten :yellow[hotter] in recent years")
        st.markdown(
        "<span style='font-size:24px; font-weight:600;'>Explore how the average monthly temperature has gotten <span style='color:gold;'>hotter</span> in recent years</span>",
        unsafe_allow_html=True)


        st.write('This is the average temperature of the air measured two meters above the ground, encompassing land, sea, and in-land water surfaces.')

        st.altair_chart(monthly_line,use_container_width=True)

# ─── Tab 3: Variability Analysis ───────────────────────
    with tab3:
        st.subheader("🔻 Countries with Decreasing Temperature Variability")
        st.info("""
        This chart compares the **standard deviation of temperature change** before and after 1993.
        A **negative delta** indicates more stable climate conditions.
        """)

        early = df_long[df_long["Year"] <= 1992].groupby("Country")["TempChange"].std().reset_index(name="Std_Early")
        late = df_long[df_long["Year"] >= 1993].groupby("Country")["TempChange"].std().reset_index(name="Std_Late")
        std_comp = early.merge(late, on="Country")
        std_comp["Delta_Std"] = std_comp["Std_Late"] - std_comp["Std_Early"]
        decreasing = std_comp[std_comp["Delta_Std"] < 0].sort_values("Delta_Std")

        # Change to horizontal bar chart with ADA-compliant colors
        bar = alt.Chart(decreasing).mark_bar().encode(
            x=alt.X("Delta_Std:Q", title="∆ Std Dev (1993–2024 − 1961–1992)"),
            y=alt.Y("Country:N", sort=alt.SortField('Delta_Std:Q', order='descending')),
            color=alt.Color("Delta_Std:Q", scale=alt.Scale(scheme="bluegreen"), legend=alt.Legend(title="Delta Std Dev")),
            tooltip=["Country", "Std_Early", "Std_Late", "Delta_Std"]
        ).properties(
            height=600,  # Adjusted height for better visibility
            width=900,   # Adjusted width for better layout
            title="Top Countries with Decreasing Yearly Temperature Variability"
        )

        # Add annotations for Delta_Std values
        text = bar.mark_text(
            align='right',
            baseline='middle',
            dx=-5,
            color='white' # Adjusts the position of the text
        ).encode(
            x=alt.X("Delta_Std:Q"),
            y=alt.Y("Country:N", sort=alt.SortField('Delta_Std:Q', order='descending')),
            text=alt.Text("Delta_Std:Q", format=".2f")  # Format the text to show two decimal places
        )

        # Combine bar and text layers
        chart = alt.layer(bar,text).properties(
            width=900,
            height=600
        )

        # Add reference line at zero
        reference_line = alt.Chart(decreasing).mark_rule(color='red').encode(
            x='0:Q'
        )

        # Combine everything
        final_chart = alt.layer(chart, reference_line).properties(
            title="Top Countries with Decreasing Yearly Temperature Variability"
        )

        st.altair_chart(final_chart, use_container_width=True)

    # ─── Tab 4: Developed vs Developing Comparison ─────────
    with tab4:
        st.subheader("🌍 Developed vs Developing: Temperature Comparison")
        
        st.write("""
        Developed countries, often referred to as "high-income" nations, typically have advanced technological infrastructure,
        high standards of living, and robust economies. Examples include the United States, Germany, and Japan.

        Developing countries face challenges like limited access to education, healthcare, and infrastructure.
        Examples include India, Nigeria, and Bangladesh.
        """)

        dev_sel = alt.selection_multi(fields=["DevStatus"], bind="legend")
        dev_avg = df_long.groupby(["Year", "DevStatus"])["TempChange"].mean().reset_index()

        line_chart = alt.Chart(dev_avg).mark_line(point=True).encode(
            x=alt.X("Year:O"),
            y=alt.Y("TempChange:Q", title="Avg Temp Change (°C)"),
            color=alt.Color("DevStatus:N", scale=alt.Scale(domain=["Developed", "Developing"], range=["#2ca02c", "#ff7f0e"])),
            opacity=alt.condition(dev_sel, alt.value(1.0), alt.value(0.15)),
            tooltip=["Year", "DevStatus", "TempChange"]
        ).add_params(dev_sel).properties(
            title="Average Temp Change by Economic Status",
            width=750,
            height=400
        )

        st.altair_chart(line_chart, use_container_width=True)

        df_long["YearGroup"] = (df_long["Year"] // 5) * 5
        dev_bar = df_long.groupby(["YearGroup", "DevStatus"])["TempChange"].mean().reset_index()

        bar_chart = alt.Chart(dev_bar).mark_bar().encode(
            x=alt.X("YearGroup:O", title="5-Year Group"),
            y=alt.Y("TempChange:Q", title="Avg Temp Change (°C)"),
            color=alt.Color("DevStatus:N", scale=alt.Scale(domain=["Developed", "Developing"], range=["#2ca02c", "#ff7f0e"])),
            opacity=alt.condition(dev_sel, alt.value(1.0), alt.value(0.25)),
            tooltip=["YearGroup", "DevStatus", "TempChange"]
        ).add_params(dev_sel).properties(
            title="5-Year Avg Temp Change by Development Status",
            width=750,
            height=400
        )

        st.altair_chart(bar_chart, use_container_width=True)

# ─── Warming Gases Page ─────────────────────────────────────
if page == "Warming Gases":
    
    # Load gas data
    df_gas = pd.read_csv('global-warming-by-gas-and-source.csv')
    # ─── Sidebar Filters ───────────────    
    st.sidebar.header("🔍 Filters")
    countries = ["All"] + sorted(df_gas["Entity"].unique())
    # years = sorted(df_gas["Year"].unique())  # Keep years available if needed

    year_min, year_max = int(1961), int(df_gas["Year"].max())

    selected_country = st.sidebar.selectbox("Country", list_of_all_countries)
    dev_year_range = st.sidebar.slider("Year Range",
                               min_value=year_min,
                               max_value=year_max,
                               value=(year_min, year_max),
                               step=1,
                               key="dev_year_range")  # Optional: keep if you want to filter by year

    # Filter the DataFrame based on selected country and year
    filtered = df_long.copy()  
    
    st.subheader("🔥 Warming Contributions by Gas and Source")
    st.info("""
    This area chart shows **the warming impact of major greenhouse gases and emission sources over time**.
    Click the legend to **highlight or filter** different contributors.
    """)

    # Set a default year range and country
    year_range = (dev_year_range[0], dev_year_range[1])
    chart_country = selected_country if 'selected_country' in locals() else "All"
    
    gas_long = prepare_gas_data(df_gas, year_range, chart_country)

    gas_long['Legend'] = gas_long['series']

    # Interactive selection logic
    selection = alt.selection_point(fields=['Legend'])
    condition = alt.condition(selection, 'Legend:N', alt.ColorValue('lightgray'))


    # Area chart showing contribution by gas
    area = alt.Chart(gas_long).mark_area(opacity=0.7).encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Temp Change:Q", title="Temperature Change (°C)"),
        color=condition,
        order="Legend:N",
        tooltip=['Year:O', 'Legend:N', 'Temp Change:Q']
    ).add_params(selection).properties(
        width=900,
        height=500,
        title="Warming Contributions by Gas Type and Emission Source"
    )

    # Explanation and chart rendering
    st.markdown("""
    #### How do different gases and sources contribute to global warming?
    This area chart visualizes how different greenhouse gases contribute to global warming over time.
    
    - The leading gases are carbon dioxide (CO₂), methane (CH₄), and nitrous oxide (N₂O).
    - The main sources are fossil fuels and industry (FF&I), and agriculture and land use (AgLU).
    - You can interact with the chart legend to isolate specific gases or sources.
    - The most prevalent contributor to global warming is **carbon dioxide** from **fossil fuels and industry**.
    - Solutions include transitioning to renewable energy, electrification of transportation, and adopting energy-efficient technologies.
    """)

    st.altair_chart(area, use_container_width=True)

# ─── Roydan to add Content ───────────────────────────────────
if page == "Global Warming Contribution":
    st.title("Global Warming Contribution")
    st.markdown("""
    #### How do developed and developing nations contribute to global warming?
    - The visualization below illustrates a group or nation's share of global mean surface temperature change as a result of its cumulative emission of three gases - carbon dioxide, methane, and nitrous oxide.
    - **Select** the **"Detailed"** radio button to zoom and filter on the biggest offenders.
    - **Zoom and select a time period via interaction** to analyse temporal changes in global mean surface temperature.
                """)
    # Decided not to have this feature
    # # Creating slider
    # year_min, year_max = int(1961), int(2024)
    # dev_year_range = st.sidebar.slider("Year Range",
    #                            min_value=year_min,
    #                            max_value=year_max,
    #                            value=(year_min, year_max),
    #                            step=1,
    #                            key="dev_year_range")

     # Loading data
    df_overview, df_contribution_lcd, df_contribution_oecd = load_contribution_df()
    
    # Creating nations list
    countries =list(df_overview['Entity'].unique())
    
    brush_new = alt.selection_interval(encodings=['x'],resolve='global')
    conditonal = alt.condition(brush_new, alt.value(1.0),alt.value(0.25))
    
    # Creating radio button for chart
    radio = st.radio("Select Chart", ('Overview','Detailed'))

    if radio == 'Overview':
        # Creating an area line chart    
        Background = alt.Chart(df_overview).mark_area().encode(
        x='Year:O',
        y='Share of contribution to global warming:Q',
        #opacity = conditonal,
        color='Entity')

        # background + selected
        chart = Background #+ highlight
        st.subheader("Contributions to the change in global mean surface temperature - Developing Versus Developed")
        st.altair_chart(chart, use_container_width=True)
        st.caption("Organization for economic cooperation and development (OECD) is a international organization composed of 38 member nations that collaborate to develope economic and social policies.")
        st.caption("Least developed nations(LDC) are 43 economies recognized by the United Nations as facing the most structural impediments to sustainable developement.")
    elif radio == 'Detailed':
        brush_new = alt.selection_interval(encodings=['x'],resolve='global')
        conditonal = alt.condition(brush_new, alt.value(1.0),alt.value(0.25))
        # Creating chart
        background_OECD = alt.Chart(df_contribution_oecd, title='Contributions to the change in global mean surface temperature- OECD Nations').mark_line().encode(
            x=alt.X('Year:O'),
            y=alt.Y('Share of contribution to global warming:Q'),
            #color=alt.Color('Entity:N'),
            opacity=conditonal,
            color=alt.condition(brush_new, 'Entity:N', alt.ColorValue('gray')),
            tooltip=['Entity:N','Share of contribution to global warming:Q','Year']
        ).properties(width=500,height=300).add_params(brush_new).interactive()
        
        # Creating a highlight chart
        highlight_OECD = alt.Chart(df_contribution_oecd).mark_line().encode(
            x=alt.X('Year:O'),
            y=alt.Y('Share of contribution to global warming:Q'),
            color=alt.Color('Entity:N'),
        
            tooltip=['Entity:N','Share of contribution to global warming:Q','Year']
        ).transform_filter(brush_new)


         # Creating chart
        background_LDC = alt.Chart(df_contribution_lcd, title='Contributions to the change in global mean surface temperature- LDC Nations').mark_line().encode(
            x=alt.X('Year:O'),
            y=alt.Y('Share of contribution to global warming:Q'),
            #color=alt.Color('Entity:N'),
            opacity=conditonal,
            color=alt.condition(brush_new, alt.Color('Entity:N', scale=alt.Scale(scheme='category10')), alt.ColorValue('gray')),
            tooltip=['Entity:N','Share of contribution to global warming:Q','Year']
        ).properties(width=500,height=300).add_params(brush_new).interactive()
        
        # Creating a highlight chart
        highlight_LDC = alt.Chart(df_contribution_lcd).mark_line().encode(
            x=alt.X('Year:O'),
            y=alt.Y('Share of contribution to global warming:Q'),
            color=alt.Color('Entity:N', scale=alt.Scale(scheme='category10')),
        
            tooltip=['Entity:N','Share of contribution to global warming:Q','Year']
        ).interactive().transform_filter(brush_new)
        
        # combining the two charts
        st.subheader("Contributions to the change in global mean surface temperature - Developing Versus Developed")
        chart_OECD = background_OECD + highlight_OECD
        chart_LDC = background_LDC + highlight_LDC
        chart = alt.hconcat(chart_LDC,chart_OECD).resolve_scale(color='independent',y='shared')

        st.altair_chart(chart)
        st.altair_chart(alt.vconcat(alt.hconcat(chart_LDC,chart_OECD)).resolve_scale(color='independent'))
       




     



# ─── Chat Assistant Page ────────────────────────────────
if page == "Chat Assistant":
    st.subheader("🧠 ClimateBot Assistant")
    st.markdown("""
    Ask **ClimateBot** about:
    - 📈 Temperature trends over time
    - 🌡️ Country-level comparisons
    - 🔻 Variability and climate stability

    For example:
    - “Which country had the highest temp change in 1998?”
    - “What does decreased variability mean?”
    - “Compare developing vs developed warming patterns”
    """)
    # def ask_climatebot(prompt):
    # response = openai.ChatCompletion.create(
    #     model="gpt-4",  # or "gpt-3.5-turbo"
    #     messages=[
    #         {"role": "system", "content": "You are ClimateBot, an expert in climate change, data storytelling, and global temperature trends. Be helpful and cite charts when possible."},
    #         {"role": "user", "content": prompt}
    #     ],
    #     temperature=0.7
    # )
    # return response['choices'][0]['message']['content']


    # Set up chat interface
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hi, I'm ClimateBot! Ask me about global temperatures 🌍"}
        ]

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask your question here...")
    if prompt:
        st.chat_message("user").markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Hard-coded Q&A for demonstration
        response = ""
        q = prompt.lower()

        if "highest temp" in q and "country" in q:
            response = "The country with the highest recorded temperature change in 1998 was likely a high-latitude nation like Russia or Canada, but exact values depend on the dataset."
        elif "variability" in q:
            response = (
                "Variability refers to how much temperatures fluctuate year to year. "
                "Less variability means more climate stability, which can affect ecosystems and planning."
            )
        elif "developed" in q and "developing" in q:
            response = (
                "Developed countries often show earlier increases due to industrialization. "
                "Developing countries are now experiencing steeper rises due to economic growth and emissions."
            )
        else:
            response = "Great question! Try asking about a specific year, country, or trend type. I'm still learning! 🤖"

        st.chat_message("assistant").markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

# ─── Footer ────────────────────────────────────────────────
st.markdown("---")
st.write(
    """
    <div style="text-align: center; font-size: 15px;" role="contentinfo" aria-label="Footer information">
        🌐 Created by <strong>Harrison, Paula, and Roydan</strong> • Advocates for climate transparency and data science  
        <br/>
        Built with ❤️ using <a href="https://streamlit.io" target="_blank">Streamlit</a> and <a href="https://altair-viz.github.io" target="_blank">Altair</a>
    </div>
    """,
    unsafe_allow_html=True
)
