"""
Shared data loading, cleaning, RFM, and categorization logic for the
Retail Analytics Dashboard.

Cleaning approach mirrors retail_data_analysis.ipynb (drop duplicates,
drop rows with any missing values, remove cancelled/negative-quantity
transactions, keep positive prices, derive Revenue). This same cleaned
dataset is then used to compute RFM per rfm_analysis.ipynb so both
dashboard pages stay consistent with a single source of truth.
"""

import pandas as pd
import numpy as np
import streamlit as st

DATA_PATH = "Online_Retail.xlsx"


# ---------------------------------------------------------------------------
# Loading & cleaning
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_raw_data():
    df = pd.read_excel(DATA_PATH)
    return df


@st.cache_data(show_spinner=False)
def clean_data():
    """Clean transactions and derive Revenue + Category. Also returns
    raw-data stats needed for return-rate calculation."""
    df_raw = load_raw_data()

    total_invoices_raw = df_raw["InvoiceNo"].astype(str).nunique()
    cancelled_mask = df_raw["InvoiceNo"].astype(str).str.startswith("C")
    cancelled_invoices = df_raw.loc[cancelled_mask, "InvoiceNo"].astype(str).nunique()

    df = df_raw.copy()
    df = df.drop_duplicates()
    df = df.dropna()
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
    df = df[df["Quantity"] > 0]
    df = df[df["UnitPrice"] > 0]
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["CustomerID"] = df["CustomerID"].astype(int)
    df["StockCode"] = df["StockCode"].astype(str)
    df["InvoiceNo"] = df["InvoiceNo"].astype(str)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Category"] = df["Description"].apply(assign_category)

    return_stats = {
        "total_invoices_raw": total_invoices_raw,
        "cancelled_invoices": cancelled_invoices,
        "return_rate_pct": (cancelled_invoices / total_invoices_raw * 100)
        if total_invoices_raw else 0,
    }

    return df, return_stats


def assign_category(desc):
    """Map product description to a category using keyword rules
    (identical logic to retail_data_analysis.ipynb)."""
    d = str(desc).upper()

    if d in ("POSTAGE", "MANUAL", "DOTCOM POSTAGE", "BANK CHARGES", "CRUK COMMISSION") or "POSTAGE" in d:
        return "Postage & Admin"
    if any(k in d for k in ["BAG", "SHOPPER", "POUCH"]):
        return "Bags & Carriers"
    if any(k in d for k in ["LIGHT", "LANTERN", "CANDLE", "T-LIGHT", "NIGHT LIGHT"]):
        return "Lighting"
    if any(k in d for k in ["CAKE", "JAR", "TIN", "KITCHEN", "PICNIC", "TEA ", "TEAPOT", "JAM", "MUG",
                             "CUP", "PLATE", "BOWL", "SPOON", "CAKESTAND", "BAKING", "BOTTLE", "POPCORN",
                             "MOULD", "CUTLERY"]):
        return "Kitchen & Dining"
    if any(k in d for k in ["CARD", "PAPER", "CHAIN KIT", "NOTEBOOK", "WRAPPING"]):
        return "Cards & Paper Crafts"
    if any(k in d for k in ["CUSHION", "DOORMAT", "BLANKET", "TOWEL", "WICKER"]):
        return "Textiles & Home Soft Goods"
    if any(k in d for k in ["ORNAMENT", "BUNTING", "WREATH", "FRAME", "SIGN", "BOARD", "CLOCK", "VASE",
                             "FIGURINE", "STATUE", "GARLAND", "PARASOL", "FAN", "RIBBON", "PAINT SET"]):
        return "Home Decor & Gifts"
    if any(k in d for k in ["STORAGE", "BOX", "CASE", "RACK", "HANGER", "CABINET", "DRAWER"]):
        return "Storage & Organisation"
    if "HEART" in d:
        return "Heart-themed Gifts"
    if "CHRISTMAS" in d:
        return "Seasonal / Christmas"
    if any(k in d for k in ["TOY", "GAME", "DOLL"]):
        return "Toys & Games"
    return "Other"


# ---------------------------------------------------------------------------
# Business overview aggregations
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def get_overview_metrics(df):
    total_revenue = df["Revenue"].sum()
    total_customers = df["CustomerID"].nunique()
    total_orders = df["InvoiceNo"].nunique()
    aov = total_revenue / total_orders if total_orders else 0
    return {
        "total_revenue": total_revenue,
        "total_customers": total_customers,
        "total_orders": total_orders,
        "aov": aov,
    }


@st.cache_data(show_spinner=False)
def get_monthly_trends(df):
    d = df.copy()
    d["YearMonth"] = d["InvoiceDate"].dt.to_period("M").astype(str)
    monthly = d.groupby("YearMonth").agg(
        Revenue=("Revenue", "sum"),
        Orders=("InvoiceNo", "nunique"),
        Units_Sold=("Quantity", "sum"),
    ).reset_index()
    monthly["AOV"] = monthly["Revenue"] / monthly["Orders"]
    return monthly


@st.cache_data(show_spinner=False)
def get_country_stats(df):
    stats = df.groupby("Country").agg(
        Revenue=("Revenue", "sum"),
        Units_Sold=("Quantity", "sum"),
        Orders=("InvoiceNo", "nunique"),
        Customers=("CustomerID", "nunique"),
    ).reset_index()
    stats["AOV"] = stats["Revenue"] / stats["Orders"]
    stats = stats.sort_values("Revenue", ascending=False).reset_index(drop=True)
    return stats


@st.cache_data(show_spinner=False)
def get_product_stats(df):
    stats = df.groupby(["StockCode", "Description"]).agg(
        Revenue=("Revenue", "sum"),
        Units_Sold=("Quantity", "sum"),
        Orders=("InvoiceNo", "nunique"),
    ).reset_index()
    return stats.sort_values("Revenue", ascending=False)


@st.cache_data(show_spinner=False)
def get_category_stats(df):
    stats = df.groupby("Category").agg(
        Revenue=("Revenue", "sum"),
        Units_Sold=("Quantity", "sum"),
        Orders=("InvoiceNo", "nunique"),
        Products=("StockCode", "nunique"),
    ).reset_index()
    stats["Revenue_Share_%"] = (stats["Revenue"] / stats["Revenue"].sum() * 100).round(1)
    return stats.sort_values("Revenue", ascending=False)


# ---------------------------------------------------------------------------
# RFM
# ---------------------------------------------------------------------------

SEGMENT_INFO = {
    "Champions": {
        "color": "#F5B942",
        "emoji": "🏆",
        "tagline": "Your best customers — recent, frequent, and high-spending.",
        "recommendations": [
            "Give early access to new product lines before general release.",
            "Enrol in a VIP or loyalty tier with tangible perks, not just points.",
            "Ask for reviews/referrals — they are your most credible advocates.",
        ],
    },
    "Loyal Customers": {
        "color": "#7C9CFF",
        "emoji": "💙",
        "tagline": "Consistent repeat buyers who keep coming back.",
        "recommendations": [
            "Upsell complementary products based on past purchase categories.",
            "Invite to a loyalty programme to reward continued frequency.",
            "Send personalized replenishment reminders for repeat items.",
        ],
    },
    "Big Spenders": {
        "color": "#C689F0",
        "emoji": "💎",
        "tagline": "Spend a lot per order, but don't order very often.",
        "recommendations": [
            "Encourage a second purchase soon with a time-limited offer.",
            "Bundle premium items to lift order frequency, not just basket size.",
            "Feature them in a 'we miss you' campaign if their gap grows.",
        ],
    },
    "Potential Loyalists": {
        "color": "#63D9C8",
        "emoji": "🌱",
        "tagline": "Recent, reasonably engaged — showing signs of becoming loyal.",
        "recommendations": [
            "Nudge toward a second and third purchase with onboarding offers.",
            "Introduce loyalty programme benefits early to build habit.",
            "Cross-sell based on their first category of interest.",
        ],
    },
    "New Customers": {
        "color": "#6EE7B7",
        "emoji": "✨",
        "tagline": "Just made their first purchase(s) — still forming an impression.",
        "recommendations": [
            "Send a warm welcome series introducing bestsellers.",
            "Offer a small incentive on their next order to build the repeat habit.",
            "Ask for feedback on their first purchase experience.",
        ],
    },
    "At Risk": {
        "color": "#F2994A",
        "emoji": "⚠️",
        "tagline": "Used to be valuable, but haven't purchased in a while.",
        "recommendations": [
            "Launch a win-back campaign with a personalized discount.",
            "Ask directly (survey/email) what changed since their last order.",
            "Highlight new arrivals in categories they used to buy from.",
        ],
    },
    "Hibernating": {
        "color": "#9CA3AF",
        "emoji": "💤",
        "tagline": "Long inactive with low historical engagement.",
        "recommendations": [
            "Include in low-cost, broad re-engagement emails only.",
            "Test a strong incentive once — if no response, deprioritize spend.",
            "Consider removing from frequent marketing sends to protect deliverability.",
        ],
    },
    "Lost": {
        "color": "#EF6F6C",
        "emoji": "🥀",
        "tagline": "Least recent, least frequent, least valuable historically.",
        "recommendations": [
            "Attempt one final strong win-back offer before archiving.",
            "Exclude from regular campaigns to reduce marketing waste.",
            "Use as a signal to review what drove churn at that lifecycle stage.",
        ],
    },
    "Others": {
        "color": "#94A3B8",
        "emoji": "◌",
        "tagline": "A mixed pattern that doesn't fit a clean segment.",
        "recommendations": [
            "Monitor over the next cycle to see which segment they trend toward.",
            "Apply general lifecycle marketing until a clearer pattern emerges.",
        ],
    },
}


def assign_segment(row):
    r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    elif f >= 4 and r >= 3:
        return "Loyal Customers"
    elif m >= 4 and f <= 2:
        return "Big Spenders"
    elif r >= 4 and f <= 2 and m <= 2:
        return "New Customers"
    elif r >= 3 and f >= 3 and m >= 3:
        return "Potential Loyalists"
    elif r <= 2 and f >= 4 and m >= 4:
        return "At Risk"
    elif r <= 2 and f <= 2 and m <= 2:
        return "Lost"
    elif r <= 2 and f <= 3 and m <= 3:
        return "Hibernating"
    else:
        return "Others"


@st.cache_data(show_spinner=False)
def compute_rfm(df):
    reference_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda x: (reference_date - x.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Revenue", "sum"),
        Country=("Country", "first"),
        FirstPurchase=("InvoiceDate", "min"),
        LastPurchase=("InvoiceDate", "max"),
    ).reset_index()

    rfm["R_Score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)

    rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)
    rfm["RFM_Total"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]
    rfm["Segment"] = rfm.apply(assign_segment, axis=1)

    return rfm


@st.cache_data(show_spinner=False)
def get_customer_transactions(df, customer_id):
    return df[df["CustomerID"] == customer_id].copy()
