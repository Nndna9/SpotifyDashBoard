
import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Spotify Stakeholder Dashboard",
    page_icon="🎧",
    layout="wide"
)

# ---------------- STYLES & ANIMATIONS ----------------
st.markdown(
    """
    <style>
    body { background-color: #000; color: white; }
    .stMetric {
        background-color: #121212;
        padding: 15px;
        border-radius: 14px;
        transition: transform 0.3s ease;
    }
    .stMetric:hover {
        transform: scale(1.03);
    }
    .fade-in {
        animation: fadeIn 1.2s ease-in;
    }
    .slide-up {
        animation: slideUp 1s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .insight-box {
        background-color: #0f2f1f;
        border-left: 5px solid #1DB954;
        padding: 12px;
        border-radius: 8px;
        margin-top: 5px;
        margin-bottom: 20px;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True
)

# ---------------- DATA LOADERS ----------------
@st.cache_data
def load_spotify():
    return pd.read_csv("spotify.csv")

@st.cache_data
def load_campaigns():
    return pd.read_csv("marketing_campaigns.csv")

spotify_df = load_spotify()
campaign_df = load_campaigns()

# ---------------- NAVIGATION ----------------
page = st.sidebar.radio(
    "Navigate",
    ["🎵 Streaming Performance", "📣 Marketing Campaign Impact"]
)

# =====================================================
# PAGE 1: STREAMING PERFORMANCE (4 VISUALS)
# =====================================================
if page == "🎵 Streaming Performance":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.title("Spotify Global Streaming Performance")
    st.caption("Executive view of content, regions, and user segments")

    # -------- GLOBAL FILTERS --------
    with st.sidebar:
        st.header("🎚 Global Filters")
        region = st.multiselect("Region", spotify_df.region.unique(), spotify_df.region.unique())
        genre = st.multiselect("Genre", spotify_df.genre.unique(), spotify_df.genre.unique())
        sub = st.multiselect("Subscription", spotify_df.subscription_type.unique(), spotify_df.subscription_type.unique())
        month = st.multiselect("Month", spotify_df.month.unique(), spotify_df.month.unique())

    df = spotify_df[
        (spotify_df.region.isin(region)) &
        (spotify_df.genre.isin(genre)) &
        (spotify_df.subscription_type.isin(sub)) &
        (spotify_df.month.isin(month))
    ]

    # -------- KPI ROW --------
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Streams", f"{df.streams.sum():,}")
    k2.metric("Active Listeners", f"{df.active_listeners.sum():,}")
    k3.metric("Top Artist", df.groupby("artist_name").streams.sum().idxmax())
    k4.metric("Premium Share (%)", round(
        df[df.subscription_type=="Premium"].active_listeners.sum() / df.active_listeners.sum() * 100, 1))

    st.divider()

    # -------- VISUAL 1: TOP ARTISTS --------
    st.subheader("Top Artists by Streams")
    artist_limit = st.slider("Select number of artists", 5, 15, 10)
    v1 = (
        df.groupby("artist_name").streams.sum()
        .reset_index().sort_values("streams", ascending=False)
        .head(artist_limit)
    )
    st.plotly_chart(px.bar(v1, x="streams", y="artist_name", orientation="h"), use_container_width=True)
    st.markdown(
        "<div class='insight-box'>🎯 A small set of artists contributes a large share of streams, "
        "indicating concentration risk and superstar dependency.</div>",
        unsafe_allow_html=True
    )

    # -------- VISUAL 2: GENRE x REGION --------
    st.subheader("Genre Share by Region")
    selected_region = st.selectbox("Focus Region (visual filter)", sorted(df.region.unique()))
    v2 = (
        df[df.region == selected_region]
        .groupby("genre").streams.sum().reset_index()
    )
    st.plotly_chart(px.pie(v2, names="genre", values="streams", hole=0.4), use_container_width=True)
    st.markdown(
        "<div class='insight-box'>🌍 Genre dominance varies by region, highlighting where localized playlists "
        "and regional artist investments can outperform global pushes.</div>",
        unsafe_allow_html=True
    )

    # -------- VISUAL 3: MONTHLY TREND --------
    st.subheader("Monthly Streaming Trend")
    trend_sub = st.selectbox("Subscription filter (visual)", df.subscription_type.unique())
    v3 = (
        df[df.subscription_type == trend_sub]
        .groupby("month").streams.sum().reset_index()
    )
    st.plotly_chart(px.line(v3, x="month", y="streams", markers=True), use_container_width=True)
    st.markdown(
        "<div class='insight-box'>📈 Clear peaks and dips suggest seasonality and campaign-driven behavior, "
        "useful for timing releases and promotions.</div>",
        unsafe_allow_html=True
    )

    # -------- VISUAL 4: FREE vs PREMIUM --------
    st.subheader("Free vs Premium Engagement")
    engagement_metric = st.radio("Metric", ["streams", "completion_rate"], horizontal=True)
    v4 = (
        df.groupby("subscription_type")[engagement_metric]
        .mean().reset_index()
    )
    st.plotly_chart(px.bar(v4, x="subscription_type", y=engagement_metric), use_container_width=True)
    st.markdown(
        "<div class='insight-box'>💰 Premium users show stronger engagement signals, "
        "supporting targeted upsell strategies in high-usage markets.</div>",
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# PAGE 2: MARKETING CAMPAIGN IMPACT (4 VISUALS)
# =====================================================
else:
    st.markdown('<div class="slide-up">', unsafe_allow_html=True)
    st.title("Marketing Campaign Impact Analysis")
    st.caption("How campaigns influenced user growth and monetization")

    # -------- GLOBAL CAMPAIGN FILTERS --------
    with st.sidebar:
        st.header("🎯 Campaign Filters")
        camp = st.multiselect("Campaign", campaign_df.campaign_name.unique(), campaign_df.campaign_name.unique())
        region = st.multiselect("Target Region", campaign_df.target_region.unique(), campaign_df.target_region.unique())
        month = st.multiselect("Month", campaign_df.month.unique(), campaign_df.month.unique())

    cdf = campaign_df[
        (campaign_df.campaign_name.isin(camp)) &
        (campaign_df.target_region.isin(region)) &
        (campaign_df.month.isin(month))
    ]

    # -------- KPI ROW --------
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Net User Gain", f"{cdf.net_user_gain.sum():,}")
    k2.metric("Avg User Growth %", f"{cdf.user_growth_pct.mean():.1f}%")
    k3.metric("Avg Premium Growth %", f"{cdf.premium_growth_pct.mean():.1f}%")

    st.divider()

    # -------- VISUAL 1: CAMPAIGN PERFORMANCE --------
    st.subheader("Net User Gain by Campaign")
    st.plotly_chart(px.bar(cdf, x="campaign_name", y="net_user_gain", color="campaign_name"), use_container_width=True)
    st.markdown(
        "<div class='insight-box'>🚀 Not all campaigns succeed equally—this view helps cut underperforming "
        "campaigns and double down on proven winners.</div>",
        unsafe_allow_html=True
    )

    # -------- VISUAL 2: CAMPAIGN TREND --------
    st.subheader("Campaign Impact Over Time")
    v2 = cdf.groupby(["month", "campaign_name"]).net_user_gain.sum().reset_index()
    st.plotly_chart(px.line(v2, x="month", y="net_user_gain", color="campaign_name", markers=True), use_container_width=True)
    st.markdown(
        "<div class='insight-box'>⏳ Sustained uplift across months signals long-term brand impact, "
        "not just short-term spikes.</div>",
        unsafe_allow_html=True
    )

    # -------- VISUAL 3: GENRE FOCUS --------
    st.subheader("User Growth by Target Genre")
    v3 = cdf.groupby("target_genre").net_user_gain.sum().reset_index()
    st.plotly_chart(px.bar(v3, x="target_genre", y="net_user_gain"), use_container_width=True)
    st.markdown(
        "<div class='insight-box'>🎶 Genre-focused campaigns help identify where audience passion converts "
        "most effectively into growth.</div>",
        unsafe_allow_html=True
    )

    # -------- VISUAL 4: PREMIUM UPLIFT --------
    st.subheader("Premium Conversion Impact")
    st.plotly_chart(px.scatter(
        cdf,
        x="user_growth_pct",
        y="premium_growth_pct",
        size="net_user_gain",
        color="campaign_name"
    ), use_container_width=True)
    st.markdown(
        "<div class='insight-box'>💡 Campaigns with high user growth but low premium uplift indicate "
        "missed monetization opportunities.</div>",
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)
