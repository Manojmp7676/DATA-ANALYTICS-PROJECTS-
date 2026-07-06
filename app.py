
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from data_prep import (
    clean_data, get_overview_metrics, get_monthly_trends,
    get_country_stats, get_product_stats, get_category_stats,
)
from theme import base_css, metric_card, plotly_layout_defaults, COLORS, PLOTLY_SEQUENCE

st.set_page_config(
    page_title="Retail Business Overview",
    page_icon="🎁",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(base_css(), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

with st.spinner("Loading transaction data..."):
    df, return_stats = clean_data()

metrics = get_overview_metrics(df)
monthly = get_monthly_trends(df)
country_stats = get_country_stats(df)
product_stats = get_product_stats(df)
category_stats = get_category_stats(df)

date_min = df["InvoiceDate"].min().strftime("%d %b %Y")
date_max = df["InvoiceDate"].max().strftime("%d %b %Y")

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown('<div class="dash-eyebrow">Retail Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:Space Grotesk; font-size:1.3rem; font-weight:700; margin-bottom:0.3rem;">🎁 Gift & Home Retailer</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:{COLORS["muted"]}; font-size:0.85rem;">Data window<br><b style="color:{COLORS["text"]}">{date_min} → {date_max}</b></div>', unsafe_allow_html=True)
    st.markdown("---")
    countries = ["All Countries"] + sorted(country_stats["Country"].unique().tolist())
    selected_country = st.selectbox("Filter by country", countries)
    st.markdown("---")
    st.markdown(f'<div style="color:{COLORS["muted"]}; font-size:0.78rem;">Page 1 of 2 — Business Overview<br>See sidebar navigation above for Customer RFM Analysis.</div>', unsafe_allow_html=True)

if selected_country != "All Countries":
    df_view = df[df["Country"] == selected_country]
    metrics = get_overview_metrics(df_view)
    monthly = get_monthly_trends(df_view)
    product_stats = get_product_stats(df_view)
    category_stats = get_category_stats(df_view)
else:
    df_view = df

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown('<div class="dash-eyebrow">Business Overview</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-title">Revenue, Customers & Product Performance</div>', unsafe_allow_html=True)
scope = selected_country if selected_country != "All Countries" else "all markets"
st.markdown(f'<div class="dash-subtitle">Cleaned transaction data from {date_min} to {date_max} · scope: {scope}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(metric_card("Total Revenue", f"£{metrics['total_revenue']:,.0f}", COLORS["gold"]), unsafe_allow_html=True)
with k2:
    st.markdown(metric_card("Customers", f"{metrics['total_customers']:,}", COLORS["violet"]), unsafe_allow_html=True)
with k3:
    st.markdown(metric_card("Avg. Order Value", f"£{metrics['aov']:,.2f}", COLORS["teal"]), unsafe_allow_html=True)
with k4:
    st.markdown(metric_card("Return Rate", f"{return_stats['return_rate_pct']:.1f}%", COLORS["coral"],
                             delta=f"{return_stats['cancelled_invoices']:,} cancelled invoices"), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Revenue trend
# ---------------------------------------------------------------------------

st.markdown('<div class="section-label">Revenue Trend</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Monthly Revenue", "Monthly AOV & Orders"])

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["YearMonth"], y=monthly["Revenue"],
        mode="lines+markers", fill="tozeroy",
        line=dict(color=COLORS["gold"], width=3),
        fillcolor="rgba(242,184,75,0.15)",
        marker=dict(size=6),
        name="Revenue",
    ))
    fig.update_layout(title="Monthly Revenue Over Time", yaxis_title="Revenue (£)", xaxis_title="")
    fig = plotly_layout_defaults(fig, height=380)
    st.plotly_chart(fig, width="stretch")

with tab2:
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=monthly["YearMonth"], y=monthly["Orders"], name="Orders", marker_color=COLORS["violet"], opacity=0.55, yaxis="y2"))
    fig2.add_trace(go.Scatter(x=monthly["YearMonth"], y=monthly["AOV"], name="AOV (£)", mode="lines+markers", line=dict(color=COLORS["teal"], width=3)))
    fig2.update_layout(
        title="Average Order Value & Order Volume",
        yaxis=dict(title="AOV (£)"),
        yaxis2=dict(title="Orders", overlaying="y", side="right", showgrid=False),
    )
    fig2 = plotly_layout_defaults(fig2, height=380)
    st.plotly_chart(fig2, width="stretch")

# ---------------------------------------------------------------------------
# Geographic analysis
# ---------------------------------------------------------------------------

st.markdown('<div class="section-label">Geographic Analysis</div>', unsafe_allow_html=True)

geo_col1, geo_col2 = st.columns([3, 2])

with geo_col1:
    top_n = st.slider("Show top N countries by revenue", 5, 20, 10, key="geo_slider")
    top_countries = country_stats.head(top_n).sort_values("Revenue")
    fig3 = go.Figure(go.Bar(
        x=top_countries["Revenue"], y=top_countries["Country"],
        orientation="h", marker_color=COLORS["gold"],
        text=top_countries["Revenue"].apply(lambda v: f"£{v:,.0f}"),
        textposition="outside",
    ))
    fig3.update_layout(title=f"Top {top_n} Countries by Revenue", xaxis_title="Revenue (£)")
    fig3 = plotly_layout_defaults(fig3, height=max(320, top_n * 28))
    st.plotly_chart(fig3, width="stretch")

with geo_col2:
    non_uk = country_stats[country_stats["Country"] != "United Kingdom"].head(8)
    fig4 = px.pie(non_uk, names="Country", values="Revenue", hole=0.55,
                   color_discrete_sequence=PLOTLY_SEQUENCE)
    fig4.update_traces(textposition="inside", textinfo="percent+label")
    fig4.update_layout(title="Revenue Share (Excl. UK)", showlegend=False)
    fig4 = plotly_layout_defaults(fig4, height=max(320, top_n * 28))
    st.plotly_chart(fig4, width="stretch")

st.caption("💡 The UK accounts for the large majority of revenue in this dataset; the chart on the right excludes it to surface the next-largest international markets.")

# ---------------------------------------------------------------------------
# Product performance
# ---------------------------------------------------------------------------

st.markdown('<div class="section-label">Product Performance</div>', unsafe_allow_html=True)

prod_col1, prod_col2 = st.columns([3, 2])

with prod_col1:
    top_products = product_stats.head(12).copy()
    top_products["Label"] = top_products["Description"].str.slice(0, 38)
    fig5 = go.Figure(go.Bar(
        x=top_products["Revenue"].iloc[::-1], y=top_products["Label"].iloc[::-1],
        orientation="h", marker_color=COLORS["violet"],
        text=top_products["Revenue"].iloc[::-1].apply(lambda v: f"£{v:,.0f}"),
        textposition="outside",
    ))
    fig5.update_layout(title="Top 12 Products by Revenue", xaxis_title="Revenue (£)")
    fig5 = plotly_layout_defaults(fig5, height=440)
    st.plotly_chart(fig5, width="stretch")

with prod_col2:
    fig6 = px.treemap(
        category_stats, path=["Category"], values="Revenue",
        color="Revenue", color_continuous_scale=["#2A2660", COLORS["violet"], COLORS["gold"]],
    )
    fig6.update_layout(title="Revenue by Category", coloraxis_showscale=False)
    fig6 = plotly_layout_defaults(fig6, height=440)
    fig6.update_traces(marker=dict(line=dict(color=COLORS["bg"], width=2)))
    st.plotly_chart(fig6, width="stretch")

st.caption("Categories are derived from product description keywords (no category field in the source data).")
