
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Spotify Stakeholder Dashboard", page_icon="🎧", layout="wide")

# ================= STYLES =================
st.markdown(
    """
    <style>
    body { background-color: #000; color: white; }
    .stMetric { background-color: #121212; padding: 15px; border-radius: 14px; }
    .insight-box {
        background-color: #0f2f1f;
        border-left: 5px solid #1DB954;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True
)

# ================= DATA =================
@st.cache_data
def load_spotify():
    return pd.read_csv("spotify.csv")

@st.cache_data
def load_campaigns():
    return pd.read_csv("marketing_campaigns.csv")

spotify_df = load_spotify()
campaign_df = load_campaigns()

# numeric safety
num_cols = ["users_before", "users_after", "net_user_gain", "user_growth_pct", "premium_growth_pct"]
for c in num_cols:
    campaign_df[c] = pd.to_numeric(campaign_df[c], errors="coerce")
campaign_df = campaign_df.dropna()

# ================= HEADER =================
logo_col, title_col = st.columns([1, 6])
with logo_col:
    st.image("https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg", width=80)
with title_col:
    st.title("Spotify Stakeholder Dashboard")
    st.caption("Executive-ready insights for content, growth & marketing")

# ================= NAV =================
page = st.sidebar.radio("Navigate", ["🎵 Streaming Performance", "📣 Marketing Campaign Impact"])

# ==================================================
# PAGE 1 — STREAMING PERFORMANCE
# ==================================================
if page == "🎵 Streaming Performance":

    with st.sidebar:
        st.header("🎚 Global Filters")
        region = st.multiselect("Region", spotify_df.region.unique(), spotify_df.region.unique())
        sub = st.multiselect("Subscription", spotify_df.subscription_type.unique(), spotify_df.subscription_type.unique())
        month = st.multiselect("Month", spotify_df.month.unique(), spotify_df.month.unique())

    df = spotify_df[
        (spotify_df.region.isin(region)) &
        (spotify_df.subscription_type.isin(sub)) &
        (spotify_df.month.isin(month))
    ]

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Streams", f"{df.streams.sum():,}")
    k2.metric("Active Listeners", f"{df.active_listeners.sum():,}")
    k3.metric("Top Artist", df.groupby("artist_name").streams.sum().idxmax())
    k4.metric(
        "Premium Share (%)",
        round(df[df.subscription_type=="Premium"].active_listeners.sum() / df.active_listeners.sum() * 100, 1)
    )

    st.divider()

    # VISUAL 1
    st.subheader("Top Artists by Streams")
    artist_limit = st.slider("Number of Artists", 5, 10, 10)
    v1 = (
        df.groupby("artist_name").streams.sum()
        .reset_index().sort_values("streams", ascending=False)
        .head(artist_limit)
    )
    fig1 = px.bar(
        v1, x="streams", y="artist_name", orientation="h",
        color_discrete_sequence=["#1DB954"], text_auto=True
    )
    fig1.update_traces(textposition="outside")
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("<div class='insight-box'>Top artists contribute a large share of total listening.</div>", unsafe_allow_html=True)

    # VISUAL 2 — WORLD MAP (NEW)
    st.subheader("Global Streams Heatmap")
    map_genre = st.selectbox("Select Genre (Map Filter)", sorted(df.genre.unique()))
    map_df = (
        df[df.genre == map_genre]
        .groupby("country").streams.sum()
        .reset_index()
    )

    fig_map = px.choropleth(
        map_df,
        locations="country",
        locationmode="country names",
        color="streams",
        color_continuous_scale="Greens",
        labels={"streams": "Total Streams"},
        title=f"Streaming Intensity by Country — {map_genre}"
    )
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown(
        "<div class='insight-box'>This map highlights where specific genres resonate geographically, "
        "guiding regional marketing and playlist localization.</div>",
        unsafe_allow_html=True
    )

    # VISUAL 3
    st.subheader("Monthly Streaming Trend")
    trend_sub = st.selectbox("Subscription Type", df.subscription_type.unique())
    v3 = df[df.subscription_type == trend_sub].groupby("month").streams.sum().reset_index()
    st.plotly_chart(
        px.line(v3, x="month", y="streams", markers=True,
                color_discrete_sequence=["#1DB954"]),
        use_container_width=True
    )
    st.markdown("<div class='insight-box'>Seasonal peaks inform release and promotion timing.</div>", unsafe_allow_html=True)

    # VISUAL 4
    st.subheader("Free vs Premium Engagement")
    v4 = df.groupby("subscription_type").streams.sum().reset_index()
    st.plotly_chart(
        px.pie(v4, names="subscription_type", values="streams",
               color_discrete_sequence=["#1DB954", "#0A5D2A"]),
        use_container_width=True
    )
    st.markdown("<div class='insight-box'>Premium users generate disproportionate streaming volume.</div>", unsafe_allow_html=True)

# ==================================================
# PAGE 2 — MARKETING CAMPAIGN IMPACT (UNCHANGED)
# ==================================================
else:
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
    k1.metric("Total Net User Gain", f"{cdf.net_user_gain.sum():,}")
    k2.metric("Avg User Growth %", f"{cdf.user_growth_pct.mean():.1f}%")
    k3.metric("Avg Premium Growth %", f"{cdf.premium_growth_pct.mean():.1f}%")

    st.divider()

    st.subheader("Net User Gain by Campaign")
    v1 = cdf.groupby("campaign_name").net_user_gain.sum().reset_index()
    fig1 = px.bar(
        v1, x="campaign_name", y="net_user_gain",
        color="net_user_gain", color_continuous_scale="Greens", text_auto=True
    )
    fig1.update_traces(textposition="outside")
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("<div class='insight-box'>Darker green campaigns deliver higher user growth.</div>", unsafe_allow_html=True)

    st.subheader("User Growth vs Premium Growth (Campaign Comparison)")
    v2 = cdf.groupby("campaign_name")[["user_growth_pct", "premium_growth_pct"]].mean().reset_index()
    fig2 = px.bar(
        v2.melt(id_vars="campaign_name",
                value_vars=["user_growth_pct", "premium_growth_pct"],
                var_name="Metric", value_name="Growth %"),
        x="campaign_name", y="Growth %", color="Metric",
        barmode="group", color_discrete_sequence=["#1DB954", "#0A5D2A"],
        text_auto=".1f"
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("<div class='insight-box'>Compare acquisition vs monetization impact per campaign.</div>", unsafe_allow_html=True)

    st.subheader("User Growth by Target Genre")
    v3 = cdf.groupby("target_genre").net_user_gain.sum().reset_index()
    fig3 = px.bar(
        v3, x="target_genre", y="net_user_gain",
        color="net_user_gain", color_continuous_scale="Greens", text_auto=True
    )
    fig3.update_traces(textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("<div class='insight-box'>Genre-focused campaigns highlight strongest acquisition levers.</div>", unsafe_allow_html=True)

    st.subheader("Premium Conversion Effectiveness (Ranking)")
    v4 = (
        cdf.groupby("campaign_name").premium_growth_pct.mean()
        .reset_index().sort_values("premium_growth_pct", ascending=False)
    )
    fig4 = px.bar(
        v4, x="campaign_name", y="premium_growth_pct",
        color="premium_growth_pct", color_continuous_scale="Greens", text_auto=".1f"
    )
    fig4.update_traces(textposition="outside")
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown("<div class='insight-box'>Ranks campaigns by monetization effectiveness.</div>", unsafe_allow_html=True)
