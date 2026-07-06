import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from data_prep import clean_data, compute_rfm, get_customer_transactions, SEGMENT_INFO
from theme import base_css, metric_card, profile_card, segment_banner, recommendations_list, plotly_layout_defaults, COLORS, PLOTLY_SEQUENCE

st.set_page_config(
    page_title="Customer RFM Analysis",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(base_css(), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

with st.spinner("Loading customer data..."):
    df, _ = clean_data()
    rfm = compute_rfm(df)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown('<div class="dash-eyebrow">Retail Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:Space Grotesk; font-size:1.3rem; font-weight:700; margin-bottom:0.3rem;">🔎 Customer Lookup</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:{COLORS["muted"]}; font-size:0.85rem;">{rfm.shape[0]:,} customers scored on Recency, Frequency & Monetary value.</div>', unsafe_allow_html=True)
    st.markdown("---")

    segment_filter = st.selectbox("Filter customer list by segment", ["All Segments"] + sorted(rfm["Segment"].unique().tolist()))
    candidates = rfm if segment_filter == "All Segments" else rfm[rfm["Segment"] == segment_filter]
    customer_ids = sorted(candidates["CustomerID"].unique().tolist())

    default_index = 0
    selected_customer = st.selectbox(
        "Search / select Customer ID",
        customer_ids,
        index=default_index,
        help="Type to search — narrow the list first using the segment filter if needed.",
    )
    st.markdown("---")
    st.markdown(f'<div style="color:{COLORS["muted"]}; font-size:0.78rem;">Page 2 of 2 — Customer RFM Analysis</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown('<div class="dash-eyebrow">Customer RFM Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-title">Customer 360° Lookup</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-subtitle">Segment membership, purchase history, and personalized recommendations for an individual customer.</div>', unsafe_allow_html=True)

customer_row = rfm[rfm["CustomerID"] == selected_customer].iloc[0]
customer_txns = get_customer_transactions(df, selected_customer)
segment = customer_row["Segment"]
seg_info = SEGMENT_INFO[segment]

# ---------------------------------------------------------------------------
# Segment banner + recommendations
# ---------------------------------------------------------------------------

st.markdown(f'<div class="dash-eyebrow">Customer #{selected_customer}</div>', unsafe_allow_html=True)
st.markdown(
    segment_banner(seg_info["emoji"], segment, seg_info["color"], seg_info["tagline"]),
    unsafe_allow_html=True,
)

rec_col, rfm_col = st.columns([3, 2])

with rec_col:
    st.markdown('<div class="section-label" style="margin-top:0;">Personalized Recommendations</div>', unsafe_allow_html=True)
    st.markdown(recommendations_list(seg_info["recommendations"]), unsafe_allow_html=True)

with rfm_col:
    st.markdown('<div class="section-label" style="margin-top:0;">RFM Score Profile</div>', unsafe_allow_html=True)
    categories = ["Recency", "Frequency", "Monetary"]
    values = [int(customer_row["R_Score"]), int(customer_row["F_Score"]), int(customer_row["M_Score"])]
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(242,184,75,0.25)",
        line=dict(color=COLORS["gold"], width=2),
        name="Score",
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 5], showticklabels=True, gridcolor="rgba(255,255,255,0.15)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.15)"),
        ),
        showlegend=False,
    )
    fig_radar = plotly_layout_defaults(fig_radar, height=260)
    st.plotly_chart(fig_radar, width="stretch")

# ---------------------------------------------------------------------------
# Customer profile
# ---------------------------------------------------------------------------

st.markdown('<div class="section-label">Customer Profile</div>', unsafe_allow_html=True)

p1, p2, p3, p4 = st.columns(4)
with p1:
    st.markdown(profile_card("Location", customer_row["Country"]), unsafe_allow_html=True)
with p2:
    st.markdown(profile_card("First Purchase", customer_row["FirstPurchase"].strftime("%d %b %Y")), unsafe_allow_html=True)
with p3:
    st.markdown(profile_card("Last Purchase", customer_row["LastPurchase"].strftime("%d %b %Y")), unsafe_allow_html=True)
with p4:
    tenure_days = (customer_row["LastPurchase"] - customer_row["FirstPurchase"]).days
    st.markdown(profile_card("Customer Tenure", f"{tenure_days} days"), unsafe_allow_html=True)

st.markdown('<div class="section-label">Financial Summary</div>', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)
with f1:
    st.markdown(metric_card("Total Revenue", f"£{customer_row['Monetary']:,.2f}", COLORS["gold"]), unsafe_allow_html=True)
with f2:
    txn_aov = customer_row["Monetary"] / customer_row["Frequency"] if customer_row["Frequency"] else 0
    st.markdown(metric_card("Avg. Order Value", f"£{txn_aov:,.2f}", COLORS["teal"]), unsafe_allow_html=True)
with f3:
    st.markdown(metric_card("Transactions (Orders)", f"{int(customer_row['Frequency']):,}", COLORS["violet"]), unsafe_allow_html=True)
with f4:
    st.markdown(metric_card("Days Since Last Order", f"{int(customer_row['Recency']):,}", COLORS["coral"]), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Top products & categories purchased
# ---------------------------------------------------------------------------

st.markdown('<div class="section-label">Purchase Breakdown</div>', unsafe_allow_html=True)

b1, b2 = st.columns(2)

with b1:
    top_products = (
        customer_txns.groupby("Description")
        .agg(Revenue=("Revenue", "sum"), Units=("Quantity", "sum"))
        .reset_index()
        .sort_values("Revenue", ascending=False)
        .head(8)
    )
    top_products["Label"] = top_products["Description"].str.slice(0, 32)
    fig_prod = go.Figure(go.Bar(
        x=top_products["Revenue"].iloc[::-1],
        y=top_products["Label"].iloc[::-1],
        orientation="h",
        marker_color=COLORS["gold"],
        text=top_products["Revenue"].iloc[::-1].apply(lambda v: f"£{v:,.0f}"),
        textposition="outside",
    ))
    fig_prod.update_layout(title="Top Products Purchased", xaxis_title="Revenue (£)")
    fig_prod = plotly_layout_defaults(fig_prod, height=380)
    st.plotly_chart(fig_prod, width="stretch")

with b2:
    cat_breakdown = (
        customer_txns.groupby("Category")
        .agg(Revenue=("Revenue", "sum"))
        .reset_index()
        .sort_values("Revenue", ascending=False)
    )
    fig_cat = px.pie(
        cat_breakdown, names="Category", values="Revenue", hole=0.55,
        color_discrete_sequence=PLOTLY_SEQUENCE,
    )
    fig_cat.update_traces(textposition="inside", textinfo="percent+label")
    fig_cat.update_layout(title="Product Categories Purchased", showlegend=False)
    fig_cat = plotly_layout_defaults(fig_cat, height=380)
    st.plotly_chart(fig_cat, width="stretch")

with st.expander("View raw transaction history for this customer"):
    st.dataframe(
        customer_txns[["InvoiceNo", "InvoiceDate", "StockCode", "Description", "Quantity", "UnitPrice", "Revenue", "Category"]]
        .sort_values("InvoiceDate", ascending=False)
        .reset_index(drop=True),
        width="stretch",
    )
