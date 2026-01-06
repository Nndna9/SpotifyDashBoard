
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Spotify Stakeholder Dashboard", page_icon="🎧", layout="wide")

# ---------------- STYLES ----------------
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

# ---------------- DATA ----------------
@st.cache_data
def load_spotify():
    return pd.read_csv("spotify.csv")

@st.cache_data
def load_campaigns():
    return pd.read_csv("marketing_campaigns.csv")

spotify_df = load_spotify()
campaign_df = load_campaigns()

# Numeric safety
num_cols = ["users_before", "users_after", "net_user_gain", "user_growth_pct", "premium_growth_pct"]
for c in num_cols:
    campaign_df[c] = pd.to_numeric(campaign_df[c], errors="coerce")
campaign_df = campaign_df.dropna()

# ---------------- HEADER ----------------
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg", width=80)
with col_title:
    st.title("Spotify Stakeholder Dashboard")
    st.caption("Executive-ready insights for content, growth & marketing")

# ---------------- NAV ----------------
page = st.sidebar.radio("Navigate", ["🎵 Streaming Performance", "📣 Marketing Campaign Impact"])

# =====================================================
# PAGE 1: STREAMING PERFORMANCE (unchanged)
# =====================================================
if page == "🎵 Streaming Performance":
    st.info("Streaming performance view unchanged — focus on campaign clarity improvements on next page.")

# =====================================================
# PAGE 2: MARKETING CAMPAIGN IMPACT (IMPROVED)
# =====================================================
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

    # KPI Row
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Net User Gain", f"{cdf.net_user_gain.sum():,}")
    k2.metric("Avg User Growth %", f"{cdf.user_growth_pct.mean():.1f}%")
    k3.metric("Avg Premium Growth %", f"{cdf.premium_growth_pct.mean():.1f}%")

    st.divider()

    # ---------------- VISUAL 1 ----------------
    st.subheader("Net User Gain by Campaign")
    sort_order = st.radio("Sort by", ["Highest to Lowest", "Lowest to Highest"], horizontal=True)

    v1 = cdf.groupby("campaign_name").net_user_gain.sum().reset_index()
    v1 = v1.sort_values("net_user_gain", ascending=(sort_order=="Lowest to Highest"))

    fig1 = px.bar(
        v1,
        x="campaign_name",
        y="net_user_gain",
        color="net_user_gain",
        color_continuous_scale="Greens",
        text_auto=True,
        labels={"net_user_gain": "Net Users Gained"}
    )
    fig1.update_traces(textposition="outside")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("<div class='insight-box'>Darker green campaigns drive higher user growth. Negative bars highlight campaigns to reassess.</div>", unsafe_allow_html=True)

    # ---------------- VISUAL 2 ----------------
    st.subheader("Campaign User Growth vs Premium Growth (Decision View)")

    threshold_users = st.slider("User Growth Threshold (%)", 0.0, 30.0, 10.0)
    threshold_premium = st.slider("Premium Growth Threshold (%)", 0.0, 30.0, 5.0)

    v2 = cdf.groupby("campaign_name")[["user_growth_pct", "premium_growth_pct"]].mean().reset_index()

    fig2 = px.bar(
        v2.melt(id_vars="campaign_name", value_vars=["user_growth_pct", "premium_growth_pct"],
                var_name="Metric", value_name="Growth %"),
        x="campaign_name",
        y="Growth %",
        color="Metric",
        barmode="group",
        color_discrete_sequence=["#1DB954", "#0A5D2A"],
        text_auto=".1f"
    )
    fig2.update_layout(yaxis_title="Growth (%)")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown(
        "<div class='insight-box'>Campaigns exceeding both thresholds are strong scale candidates. "
        "High user but low premium growth suggests monetization gaps.</div>",
        unsafe_allow_html=True
    )

    # ---------------- VISUAL 3 ----------------
    st.subheader("User Growth by Target Genre")
    v3 = cdf.groupby("target_genre").net_user_gain.sum().reset_index()

    fig3 = px.bar(
        v3,
        x="target_genre",
        y="net_user_gain",
        color="net_user_gain",
        color_continuous_scale="Greens",
        text_auto=True,
        labels={"net_user_gain": "Net Users Gained"}
    )
    fig3.update_traces(textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div class='insight-box'>Genre-led campaigns reveal where audience passion converts most effectively.</div>", unsafe_allow_html=True)

    # ---------------- VISUAL 4 ----------------
    st.subheader("Premium Conversion Effectiveness (Simple Ranking)")
    v4 = cdf.groupby("campaign_name").premium_growth_pct.mean().reset_index().sort_values("premium_growth_pct", ascending=False)

    fig4 = px.bar(
        v4,
        x="campaign_name",
        y="premium_growth_pct",
        color="premium_growth_pct",
        color_continuous_scale="Greens",
        text_auto=".1f",
        labels={"premium_growth_pct": "Premium Growth %"}
    )
    fig4.update_traces(textposition="outside")
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("<div class='insight-box'>This ranking clearly shows which campaigns drive monetization, not just acquisition.</div>", unsafe_allow_html=True)
