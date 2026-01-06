
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Spotify Stakeholder Dashboard",
    page_icon="🎧",
    layout="wide"
)

st.markdown(
    """
    <style>
    body { background-color: #000; color: white; }
    .stMetric {
        background-color: #121212;
        padding: 15px;
        border-radius: 14px;
    }
    .fade-in { animation: fadeIn 1s ease-in; }
    .insight-box {
        background-color: #0f2f1f;
        border-left: 5px solid #1DB954;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-size: 14px;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
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

# -------- NUMERIC SAFETY --------
num_cols = ["users_before", "users_after", "net_user_gain", "user_growth_pct", "premium_growth_pct"]
for c in num_cols:
    campaign_df[c] = pd.to_numeric(campaign_df[c], errors="coerce")

campaign_df = campaign_df.dropna(subset=["user_growth_pct", "premium_growth_pct", "net_user_gain"])

# CREATE SAFE SIZE COLUMN (NO NEGATIVES)
campaign_df["abs_user_gain"] = campaign_df["net_user_gain"].abs() + 10

# -------- HEADER --------
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg",
        width=80
    )
with col_title:
    st.title("Spotify Stakeholder Dashboard")
    st.caption("Executive-ready insights for content, growth & marketing")

page = st.sidebar.radio(
    "Navigate",
    ["🎵 Streaming Performance", "📣 Marketing Campaign Impact"]
)

# ================= PAGE 1 =================
if page == "🎵 Streaming Performance":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)

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

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Streams", f"{df.streams.sum():,}")
    k2.metric("Active Listeners", f"{df.active_listeners.sum():,}")
    k3.metric("Top Artist", df.groupby("artist_name").streams.sum().idxmax())
    k4.metric(
        "Premium Share (%)",
        round(df[df.subscription_type=="Premium"].active_listeners.sum() / df.active_listeners.sum() * 100, 1)
    )

    st.divider()

    st.subheader("Top Artists by Streams")
    artist_limit = st.slider("Select number of artists", 5, 10, 10)
    v1 = (
        df.groupby("artist_name").streams.sum()
        .reset_index().sort_values("streams", ascending=False)
        .head(artist_limit)
    )
    st.plotly_chart(px.bar(v1, x="streams", y="artist_name", orientation="h",
                           color_discrete_sequence=["#1DB954"]), use_container_width=True)
    st.markdown("<div class='insight-box'>Streaming volume is concentrated among a few top artists.</div>", unsafe_allow_html=True)

    st.subheader("Genre Share by Region")
    focus_region = st.selectbox("Focus Region", sorted(df.region.unique()))
    v2 = df[df.region == focus_region].groupby("genre").streams.sum().reset_index()
    st.plotly_chart(px.pie(v2, names="genre", values="streams", hole=0.45,
                           color_discrete_sequence=px.colors.sequential.Greens), use_container_width=True)
    st.markdown("<div class='insight-box'>Regional genre dominance highlights localization opportunities.</div>", unsafe_allow_html=True)

    st.subheader("Monthly Streaming Trend")
    trend_sub = st.selectbox("Subscription Filter", df.subscription_type.unique())
    v3 = df[df.subscription_type == trend_sub].groupby("month").streams.sum().reset_index()
    st.plotly_chart(px.line(v3, x="month", y="streams", markers=True,
                            color_discrete_sequence=["#1DB954"]), use_container_width=True)
    st.markdown("<div class='insight-box'>Seasonal peaks guide release timing.</div>", unsafe_allow_html=True)

    st.subheader("Free vs Premium Engagement")
    v4 = df.groupby("subscription_type").streams.sum().reset_index()
    st.plotly_chart(px.pie(v4, names="subscription_type", values="streams",
                           color_discrete_sequence=["#1DB954", "#0A5D2A"]), use_container_width=True)
    st.markdown("<div class='insight-box'>Premium users drive a disproportionate share of streams.</div>", unsafe_allow_html=True)

# ================= PAGE 2 =================
else:
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)

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

    k1, k2, k3 = st.columns(3)
    k1.metric("Net User Gain", f"{cdf.net_user_gain.sum():,}")
    k2.metric("Avg User Growth %", f"{cdf.user_growth_pct.mean():.1f}%")
    k3.metric("Avg Premium Growth %", f"{cdf.premium_growth_pct.mean():.1f}%")

    st.divider()

    st.subheader("Net User Gain by Campaign")
    st.plotly_chart(px.bar(cdf, x="campaign_name", y="net_user_gain",
                           color_discrete_sequence=["#1DB954"]), use_container_width=True)
    st.markdown("<div class='insight-box'>Clear differentiation between winning and weak campaigns.</div>", unsafe_allow_html=True)

    st.subheader("Campaign Impact Over Time")
    trend = cdf.groupby(["month", "campaign_name"]).net_user_gain.sum().reset_index()
    st.plotly_chart(px.line(trend, x="month", y="net_user_gain", color="campaign_name"),
                    use_container_width=True)
    st.markdown("<div class='insight-box'>Sustained uplift matters more than short-lived spikes.</div>", unsafe_allow_html=True)

    st.subheader("User Growth by Target Genre")
    v3 = cdf.groupby("target_genre").net_user_gain.sum().reset_index()
    st.plotly_chart(px.bar(v3, x="target_genre", y="net_user_gain",
                           color_discrete_sequence=["#1DB954"]), use_container_width=True)
    st.markdown("<div class='insight-box'>Genre-led campaigns show strongest acquisition levers.</div>", unsafe_allow_html=True)

    st.subheader("Premium Conversion Impact")
    st.plotly_chart(
        px.scatter(
            cdf,
            x="user_growth_pct",
            y="premium_growth_pct",
            size="abs_user_gain",
            color="user_growth_pct",
            color_continuous_scale="Greens"
        ),
        use_container_width=True
    )
    st.markdown("<div class='insight-box'>High growth without premium uplift signals monetization gaps.</div>", unsafe_allow_html=True)
