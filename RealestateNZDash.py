import pandas as pd
import plotly.express as px
import streamlit as st
import openpyxl

# Set the page config
st.set_page_config(
    page_title='RealEstateNZ Dashboard by TeamsByDesign',
    page_icon=":bar_chart:",
    layout="wide"
)

# Hide GitHub button, header, and footer
st.markdown(
    """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK {
        display: none;
    }
    
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# Add custom CSS to set background and sidebar colors
st.markdown(
    """
    <style>
    .main {
        background-color: #f7f9fc !important;
    }
    .css-1d391kg {
        background-color: #f7f9fc !important;
    }
    .css-18e3th9 {
        background-color: #1A4DA7 !important;  /* Sidebar background color */
        color: black !important;  /* Sidebar text color */
    }
    .st-b4 {
        color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load data from Excel
df = pd.read_excel(
    io='RealestateNZ.xlsx',
    engine='openpyxl',
    sheet_name='Data',
    usecols='A:P',
    nrows=19806,
)

# Ensure Property Listing Date is in datetime format
df["Property Listed Date"] = pd.to_datetime(df["Property Listed Date"])

# Ensure the Rent column is numeric
df["Rent"] = pd.to_numeric(df["Rent"], errors='coerce')

# Sidebar filters
st.sidebar.header("Please Filter Here:")
region = st.sidebar.multiselect(
    "Select the Region:",
    options=df["Region"].unique(),
)

suburb = st.sidebar.multiselect(
    "Select the Suburb:",
    options=df["Suburb"].unique(),
)

# Filter for Property Listing Date
listing_date = st.sidebar.date_input(
    "Select Listing Date Range:",
    value=(df["Property Listed Date"].min(), df["Property Listed Date"].max()),
    min_value=df["Property Listed Date"].min(),
    max_value=df["Property Listed Date"].max()
)

# Handle empty selections
if not region:
    region = df["Region"].unique()
if not suburb:
    suburb = df["Suburb"].unique()

# Filter the DataFrame
df_selection = df[
    (df["Region"].isin(region)) &
    (df["Suburb"].isin(suburb)) &
    (df["Property Listed Date"].between(pd.to_datetime(listing_date[0]), pd.to_datetime(listing_date[1])))
]

# Title and subtitle with style and icons
st.markdown(
    """
    <h1 style='text-align: center; color: #1A4DA7;'>
        Real Estate NZ Dashboard <img src="https://img.icons8.com/color/48/000000/bar-chart.png" alt="bar chart icon"/>
    </h1>
    """,
    unsafe_allow_html=True
)

# Count the number of properties scraped
property_count = len(df_selection)

# Calculate the average rent, ignoring NaN values
average_rent = df_selection["Rent"].mean()

# Display the property count and average rent in cards
st.markdown(
    f"""
    <div style='display: flex; justify-content: space-around;'>
        <div style='background-color: #1A4DA7; padding: 10px; border-radius: 10px; text-align: center; flex: 1; margin: 10px; color: white;'>
            <h2 style='color: white;'>Number of Properties Scraped</h2>
            <p style='font-size: 24px; color: white;'><b>{property_count}</b></p>
        </div>
        <div style='background-color: #F46C3F; padding: 10px; border-radius: 10px; text-align: center; flex: 1; margin: 10px; color: white;'>
            <h2 style='color: white;'>Average Rent</h2>
            <p style='font-size: 24px; color: white;'><b>${average_rent:.2f}</b></p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Style configuration for Plotly charts
plotly_template = "plotly_white"
plot_bgcolor = 'rgba(0,0,0,0)'
axis_style = dict(showgrid=False, color='black')

# Creating a bar chart for Average Rent by Region
average_rent_by_region = (
    df_selection.groupby(by=["Region"]).mean(numeric_only=True)[["Rent"]].sort_values(by="Rent")
)

fig_average_rent = px.bar(
    average_rent_by_region.reset_index(),  # Reset index to use columns in px.bar
    x="Region",
    y="Rent",
    title="Average Rent by Region",
    color_discrete_sequence=["#1A4DA7"],  # Set a single color for the bars (blue)
    template=plotly_template,
    text=average_rent_by_region["Rent"].round(0).astype(int).apply(lambda x: f"${x}")  # Add text to the bars with dollar sign
)

fig_average_rent.update_traces(
    texttemplate='%{text}', 
    textposition='inside',  # Position the text inside the bars
    textfont=dict(color='white')  # Text color
)

fig_average_rent.update_layout(
    plot_bgcolor=plot_bgcolor,
    xaxis=axis_style,
    yaxis=axis_style,
    title={
        'text': "<b>Average Rent by Region</b>",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'family': 'Arial, sans-serif', 'size': 16, 'color': 'black'}  # Adjust title font to black
    },
    font=dict(
        family="Arial, sans-serif",
        size=12,
        color="black"  # Adjust font color
    )
)

# Create a bar chart for Average Days on Market by Region
average_days_on_market = (
    df_selection.groupby(by=["Region"]).mean(numeric_only=True)[["Days in the Market"]].sort_values(by="Days in the Market")
)

# Fill NaN values with 0 before converting to integers
average_days_on_market["Days in the Market"].fillna(0, inplace=True)

fig_days_on_market = px.bar(
    average_days_on_market.reset_index(),  # Reset index to use columns in px.bar
    x="Days in the Market",
    y="Region",
    orientation="h",
    title="Average Days on Market by Region",
    template=plotly_template,
    text=average_days_on_market["Days in the Market"].round(0).astype(int),  # Add text to the bars with no decimal places
    color_discrete_sequence=['#F46C3F']  # Set bar color to hex code F46C3F (orange)
)

fig_days_on_market.update_traces(
    texttemplate='%{text}', 
    textposition='inside',  # Position the text inside the bars
    textfont=dict(
        family="Arial, sans-serif",  # Font family
        size=14,  # Font size
        color='white'  # Font color
    )
)

fig_days_on_market.update_layout(
    plot_bgcolor=plot_bgcolor,
    xaxis=axis_style,
    yaxis=axis_style,
    title={
        'text': "<b>Average Days on Market by Region</b>",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'family': 'Arial, sans-serif', 'size': 16, 'color': 'black'}  # Adjust title font to black
    },
    font=dict(
        family="Arial, sans-serif",
        size=12,
        color="black"  # Adjust font color to black
    ),
    width=1000,  # Set the width to 1000 pixels
    height=600,  # Set the height to 600 pixels
    showlegend=False  # Remove the legend
)
# Display the bar charts and line chart
st.plotly_chart(fig_average_rent)
st.plotly_chart(fig_days_on_market)

# Create a line chart for Listing Volume
listing_volume = df_selection["Property Listed Date"].value_counts().sort_index()

# Slider for date range, positioned below the Listing Volume chart
start_date, end_date = st.slider(
    "Select a date range for Property Listed Date:",
    min_value=df_selection["Property Listed Date"].min().date(),
    max_value=df_selection["Property Listed Date"].max().date(),
    value=(df_selection["Property Listed Date"].min().date(), df_selection["Property Listed Date"].max().date()),
    format="MMMM YYYY"
)

# Filter data based on the selected date range from the slider
listing_volume_filtered = listing_volume[
    (listing_volume.index >= pd.to_datetime(start_date)) &
    (listing_volume.index <= pd.to_datetime(end_date))
]

# Create the updated line chart based on the filtered date range
fig_listing_volume = px.line(
    x=listing_volume_filtered.index,
    y=listing_volume_filtered.values,
    title="Property Listing Volume",
    labels={"x": "Date", "y": "Volume"},  # Change the axis labels here
    template=plotly_template,
)

fig_listing_volume.update_traces(
    line=dict(color="#1A4DA7")  # Line color
)

fig_listing_volume.update_layout(
    plot_bgcolor=plot_bgcolor,
    xaxis=axis_style,
    yaxis=axis_style,
    title={
        'text': "<b>Property Listing Volume</b>",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'family': 'Arial, sans-serif', 'size': 16, 'color': 'black'}  # Adjust title font to black
    },
    font=dict(
        family="Arial, sans-serif",
        size=12,
        color="black"  # Adjust font color to black
    )
)


st.plotly_chart(fig_listing_volume)
