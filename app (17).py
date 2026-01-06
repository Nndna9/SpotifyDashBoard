
import streamlit as st
import pandas as pd
import plotly.express as px

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Spotify Stakeholder Dashboard",
    page_icon="🎧",
    layout="wide"
)

# ================= STYLES =================
st.markdown(
    """
    <style>
    body { background-color: #000; color: white; }
    .stMetric {
        background-color: #121212;
        padding: 15px;
        border-radius: 14px;
    }
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

# ================= HEADER =================
logo_col, title_col = st.columns([1, 6])
with logo_col:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg",
        width=80
    )
with title_col:
    st.title("Spotify Stakeholder Dashboard")
    st.caption("Executive-ready insights for content, growth & marketing")

# ================= NAV =================
page = st.sidebar.radio(
    "Navigate",
    ["🎵 Streaming Performance", "📣 Marketing Campaign Impact"]
)

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

    # ================= KPIs =================
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Streams", f"{df.streams.sum():,}")
    k2.metric("Active Listeners", f"{df.active_listeners.sum():,}")
    k3.metric("Top Artist", df.groupby("artist_name").streams.sum().idxmax())
    k4.metric(
        "Premium Share (%)",
        round(df[df.subscription_type=="Premium"].active_listeners.sum() / df.active_listeners.sum() * 100, 1)
    )

    st.divider()

    # ================= VISUAL 1 =================
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
    st.markdown("<div class='insight-box'>A small set of artists drives a majority of global streams.</div>", unsafe_allow_html=True)

    # ================= VISUAL 2 — ELITE MAP =================
    st.subheader("Global Streams Heatmap (Genre Focus)")

    col1, col2 = st.columns(2)
    with col1:
        map_genre = st.selectbox("Genre", sorted(df.genre.unique()))
    with col2:
        zoom_region = st.selectbox(
            "Zoom Region",
            ["World", "North America", "Europe", "LATAM", "APAC", "MENA"]
        )

    map_df = (
        df[df.genre == map_genre]
        .groupby(["country", "region"])["streams"]
        .sum().reset_index()
    )

    # Tooltip classification
    q75 = map_df.streams.quantile(0.75)
    q40 = map_df.streams.quantile(0.40)

    def classify(x):
        if x >= q75:
            return f"High {map_genre} adoption market"
        elif x >= q40:
            return f"Moderate {map_genre} adoption market"
        else:
            return f"Low {map_genre} adoption market"

    map_df["market_signal"] = map_df.streams.apply(classify)

    scope_map = {
        "World": "world",
        "North America": "north america",
        "Europe": "europe",
        "LATAM": "south america",
        "APAC": "asia",
        "MENA": "africa"
    }

    fig_map = px.choropleth(
        map_df,
        locations="country",
        locationmode="country names",
        color="streams",
        hover_name="country",
        hover_data={"streams": True, "market_signal": True},
        color_continuous_scale="Greens",
        scope=scope_map[zoom_region]
    )
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown(
        "<div class='insight-box'>Heat intensity and labels reveal genre adoption strength by market, "
        "supporting regional playlist and marketing decisions.</div>",
        unsafe_allow_html=True
    )

    # ================= DRILL-DOWN =================
    st.subheader("Country-level Top Artist Drill-down")
    selected_country = st.selectbox("Select Country", sorted(df.country.unique()))
    drill_df = (
        df[df.country == selected_country]
        .groupby("artist_name").streams.sum()
        .reset_index().sort_values("streams", ascending=False)
        .head(5)
    )

    fig_drill = px.bar(
        drill_df,
        x="artist_name",
        y="streams",
        color_discrete_sequence=["#1DB954"],
        text_auto=True
    )
    fig_drill.update_traces(textposition="outside")
    st.plotly_chart(fig_drill, use_container_width=True)

    st.markdown(
        f"<div class='insight-box'>In {selected_country}, listening is dominated by a small number of artists, "
        "guiding local playlist curation.</div>",
        unsafe_allow_html=True
    )

    # ================= VISUAL 4 =================
    st.subheader("Free vs Premium Engagement")
    v4 = df.groupby("subscription_type").streams.sum().reset_index()
    st.plotly_chart(
        px.pie(v4, names="subscription_type", values="streams",
               color_discrete_sequence=["#1DB954", "#0A5D2A"]),
        use_container_width=True
    )
    st.markdown("<div class='insight-box'>Premium users contribute a disproportionate share of streams.</div>", unsafe_allow_html=True)

# ==================================================
# PAGE 2 — MARKETING CAMPAIGN IMPACT (UNCHANGED, FINAL)
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
    st.markdown("<div class='insight-box'>Campaigns with darker bars deliver stronger acquisition impact.</div>", unsafe_allow_html=True)

    st.subheader("User Growth vs Premium Growth")
    v2 = cdf.groupby("campaign_name")[["user_growth_pct", "premium_growth_pct"]].mean().reset_index()
    fig2 = px.bar(
        v2.melt(
            id_vars="campaign_name",
            value_vars=["user_growth_pct", "premium_growth_pct"],
            var_name="Metric",
            value_name="Growth %"
        ),
        x="campaign_name", y="Growth %", color="Metric",
        barmode="group", color_discrete_sequence=["#1DB954", "#0A5D2A"],
        text_auto=".1f"
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("<div class='insight-box'>Side-by-side view contrasts growth vs monetization effectiveness.</div>", unsafe_allow_html=True)

    st.subheader("User Growth by Target Genre")
    v3 = cdf.groupby("target_genre").net_user_gain.sum().reset_index()
    fig3 = px.bar(
        v3, x="target_genre", y="net_user_gain",
        color="net_user_gain", color_continuous_scale="Greens", text_auto=True
    )
    fig3.update_traces(textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("<div class='insight-box'>Genre-led campaigns reveal strongest acquisition levers.</div>", unsafe_allow_html=True)

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
