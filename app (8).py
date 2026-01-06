
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Spotify Stakeholder Dashboard",
    page_icon="🎧",
    layout="wide"
)

# Spotify Theme
st.markdown(
    """
    <style>
    body {
        background-color: #000000;
        color: white;
    }
    .stMetric {
        background-color: #121212;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True
)

@st.cache_data
def load_data():
    return pd.read_csv("spotify.csv")

df = load_data()

st.title("🎵 Spotify Global Listener & Content Performance")
st.caption("Stakeholder View – What’s performing, where, and for whom")

# ---------------- GLOBAL FILTERS ----------------
with st.sidebar:
    st.header("🎚 Global Filters")
    region = st.multiselect("Region", df["region"].unique(), default=df["region"].unique())
    genre = st.multiselect("Genre", df["genre"].unique(), default=df["genre"].unique())
    subscription = st.multiselect(
        "Subscription Type",
        df["subscription_type"].unique(),
        default=df["subscription_type"].unique()
    )
    month = st.multiselect("Month", df["month"].unique(), default=df["month"].unique())

filtered_df = df[
    (df["region"].isin(region)) &
    (df["genre"].isin(genre)) &
    (df["subscription_type"].isin(subscription)) &
    (df["month"].isin(month))
]

# ---------------- KPI CARDS ----------------
total_streams = filtered_df["streams"].sum()
active_users = filtered_df["active_listeners"].sum()
top_artist = (
    filtered_df.groupby("artist_name")["streams"]
    .sum().idxmax()
    if not filtered_df.empty else "N/A"
)
premium_share = (
    filtered_df[filtered_df["subscription_type"] == "Premium"]["active_listeners"].sum()
    / active_users * 100 if active_users > 0 else 0
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Streams", f"{total_streams:,}")
col2.metric("Active Listeners", f"{active_users:,}")
col3.metric("Top Artist", top_artist)
col4.metric("Premium Listener Share", f"{premium_share:.1f}%")

st.divider()

# ---------------- VISUAL 1: TOP ARTISTS ----------------
st.subheader("Top 10 Artists by Streams")
artist_df = (
    filtered_df.groupby("artist_name")["streams"]
    .sum().reset_index()
    .sort_values("streams", ascending=False)
    .head(10)
)

fig1 = px.bar(
    artist_df,
    x="streams",
    y="artist_name",
    orientation="h",
    color="streams",
    title="Top Artists (Global Filter Applied)"
)
st.plotly_chart(fig1, use_container_width=True)

st.caption("Insight: A small number of artists account for a disproportionately large share of total streams.")

# ---------------- VISUAL 2: GENRE BY REGION ----------------
st.subheader("Streams by Genre & Region")

genre_region = (
    filtered_df.groupby(["region", "genre"])["streams"]
    .sum().reset_index()
)

fig2 = px.bar(
    genre_region,
    x="region",
    y="streams",
    color="genre",
    title="Genre Contribution by Region",
    barmode="stack"
)
st.plotly_chart(fig2, use_container_width=True)

st.caption("Insight: Genre preferences vary strongly by region, indicating localization opportunities.")

# ---------------- VISUAL 3: MONTHLY TREND ----------------
st.subheader("Monthly Streaming Trend")

trend_df = (
    filtered_df.groupby("month")["streams"]
    .sum().reset_index()
)

fig3 = px.line(
    trend_df,
    x="month",
    y="streams",
    markers=True,
    title="Monthly Streaming Trend"
)
st.plotly_chart(fig3, use_container_width=True)

st.caption("Insight: Noticeable peaks and dips suggest seasonality and campaign-driven spikes.")

# ---------------- VISUAL 4: FREE VS PREMIUM ----------------
st.subheader("Free vs Premium Streams by Genre")

# Local filter (visual-specific)
selected_genre = st.selectbox(
    "Select Genre (Visual Filter)",
    filtered_df["genre"].unique()
)

fp_df = (
    filtered_df[filtered_df["genre"] == selected_genre]
    .groupby(["subscription_type"])["streams"]
    .sum().reset_index()
)

fig4 = px.bar(
    fp_df,
    x="subscription_type",
    y="streams",
    color="subscription_type",
    title=f"Free vs Premium – {selected_genre}"
)
st.plotly_chart(fig4, use_container_width=True)

st.caption("Insight: Premium users consistently generate higher streams per listener in most genres.")

