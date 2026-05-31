import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet

st.set_page_config(page_title="Joel's Business Dashboard", page_icon="📊", layout="wide")
st.title("Business Intelligence Dashboard — Joel Leong")
st.caption("Sales KPIs, trends, channel share, top products, and AI forecasts.")

fallback_start = "2024-01-01"
fallback_end = "2025-10-31"

st.sidebar.header("Filters")
start = st.sidebar.date_input("Start date", value=pd.to_datetime(fallback_start).date())
end = st.sidebar.date_input("End date", value=pd.to_datetime(fallback_end).date())

# Load data
df = pd.read_csv("data/sales.csv", parse_dates=["date"])
mask = (df["date"] >= pd.to_datetime(start)) & (df["date"] <= pd.to_datetime(end))
df_filtered = df[mask]

if df_filtered.empty:
    st.warning("No data for selected period. Check CSV file.")
    st.stop()

# Monthly aggregation
df_filtered["month"] = df_filtered["date"].dt.to_period("M").dt.start_time
monthly = df_filtered.groupby("month").agg(
    revenue=("revenue", "sum"),
    orders=("orders", "sum")
).reset_index()
monthly["aov"] = monthly["revenue"] / monthly["orders"]
monthly["customers"] = monthly["orders"]

# KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue", f"RM {monthly['revenue'].sum():,.0f}")
c2.metric("Total Orders", f"{monthly['orders'].sum():,}")
c3.metric("Customers", f"{monthly['customers'].sum():,}")
c4.metric("Average Order Value", f"RM {monthly['aov'].mean():,.2f}")

# Charts
col1, col2 = st.columns((3, 2))
with col1:
    fig_line = px.line(monthly, x="month", y="revenue", title="Monthly Revenue")
    st.plotly_chart(fig_line, use_container_width=True)
with col2:
    channel_share = df_filtered.groupby("channel")["revenue"].sum().reset_index()
    fig_donut = px.pie(channel_share, names="channel", values="revenue", hole=0.5, title="Channel Share")
    st.plotly_chart(fig_donut, use_container_width=True)

st.subheader("Top Products")
top_products = df_filtered.groupby("product")["revenue"].sum().reset_index().nlargest(5, "revenue")
fig_bar = px.bar(top_products, x="revenue", y="product", orientation='h', title="Top Products by Revenue")
st.plotly_chart(fig_bar, use_container_width=True)

# Forecast
st.header("Forecasts")
try:
    df_prophet = monthly[["month", "revenue"]].rename(columns={"month": "ds", "revenue": "y"})
    model = Prophet()
    model.fit(df_prophet)
    future = model.make_future_dataframe(periods=6, freq='MS')
    forecast = model.predict(future)
    fig_forecast = px.line(forecast, x="ds", y="yhat", title="6‑Month Revenue Forecast")
    st.plotly_chart(fig_forecast, use_container_width=True)
    st.dataframe(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(6))
except Exception as e:
    st.warning(f"Forecast unavailable: {e}")

st.markdown("---")
st.markdown("🚀 **Built by Joel Leong** | [AI Marketing Auditor](https://joel-marketing-audit.streamlit.app) | [GitHub](https://github.com/Joelloveai)")
