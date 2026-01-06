
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Spotify Stakeholder Dashboard",
    page_icon="🎧",
    layout="wide"
)

# ---------- STYLE ----------
st.markdown(
    """
    <style>
    body { background-color: #000; color: white; }
    .stMetric { background-color: #121212; padding: 15px; border-radius: 12px; }
    .fade-in {
        animation: fadeIn 1.5s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True
)

@st.cache_data
def load_spotify():
    return pd.read_csv("spotify.csv")

@st.cache_data
def load_campaigns():
    return pd.read_csv("marketing_campaigns.csv")

spotify_df = load_spotify()
campaign_df = load_campaigns()

# ---------- NAV ----------
page = st.sidebar.radio("Navigate", ["🎵 Streaming Performance", "📣 Marketing Campaign Impact"])

# =========================================================
# PAGE 1: STREAMING PERFORMANCE
# =========================================================
if page == "🎵 Streaming Performance":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.title("Spotify Global Listener & Content Performance")
    st.caption("Stakeholder View – What’s performing, where, and for whom")

    with st.sidebar:
        st.header("🎚 Global Filters")
        region = st.multiselect("Region", spotify_df.region.unique(), default=spotify_df.region.unique())
        genre = st.multiselect("Genre", spotify_df.genre.unique(), default=spotify_df.genre.unique())
        sub = st.multiselect("Subscription", spotify_df.subscription_type.unique(), default=spotify_df.subscription_type.unique())
        month = st.multiselect("Month", spotify_df.month.unique(), default=spotify_df.month.unique())

    df = spotify_df[
        (spotify_df.region.isin(region)) &
        (spotify_df.genre.isin(genre)) &
        (spotify_df.subscription_type.isin(sub)) &
        (spotify_df.month.isin(month))
    ]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Streams", f"{df.streams.sum():,}")
    col2.metric("Active Listeners", f"{df.active_listeners.sum():,}")
    col3.metric("Top Artist", df.groupby("artist_name").streams.sum().idxmax())
    col4.metric("Premium Share (%)", round(
        df[df.subscription_type=="Premium"].active_listeners.sum() / df.active_listeners.sum() * 100, 1))

    st.subheader("Top Artists by Streams")
    artist_df = df.groupby("artist_name").streams.sum().reset_index().sort_values("streams", ascending=False).head(10)
    st.plotly_chart(px.bar(artist_df, x="streams", y="artist_name", orientation="h"), use_container_width=True)

    st.subheader("Monthly Streaming Trend")
    trend = df.groupby("month").streams.sum().reset_index()
    st.plotly_chart(px.line(trend, x="month", y="streams", markers=True), use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# PAGE 2: MARKETING CAMPAIGNS
# =========================================================
else:
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.title("📣 Marketing Campaign Impact Analysis")
    st.caption("How campaigns influenced user growth & Premium adoption")

    with st.sidebar:
        st.header("🎯 Campaign Filters")
        camp = st.multiselect("Campaign", campaign_df.campaign_name.unique(), default=campaign_df.campaign_name.unique())
        region = st.multiselect("Target Region", campaign_df.target_region.unique(), default=campaign_df.target_region.unique())

    cdf = campaign_df[
        (campaign_df.campaign_name.isin(camp)) &
        (campaign_df.target_region.isin(region))
    ]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Net User Gain", f"{cdf.net_user_gain.sum():,}")
    col2.metric("Avg User Growth %", f"{cdf.user_growth_pct.mean():.1f}%")
    col3.metric("Avg Premium Growth %", f"{cdf.premium_growth_pct.mean():.1f}%")

    st.subheader("User Growth by Campaign")
    st.plotly_chart(
        px.bar(cdf, x="campaign_name", y="net_user_gain", color="campaign_name"),
        use_container_width=True
    )

    st.subheader("Campaign Trend Over Time")
    trend2 = cdf.groupby(["month", "campaign_name"]).net_user_gain.sum().reset_index()
    st.plotly_chart(
        px.line(trend2, x="month", y="net_user_gain", color="campaign_name", markers=True),
        use_container_width=True
    )

    st.caption("Insight: Not all campaigns succeed — some show marginal or negative uplift, guiding smarter future investments.")
    st.markdown('</div>', unsafe_allow_html=True)

