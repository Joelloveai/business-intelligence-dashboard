import streamlit as st
import pandas as pd
import plotly.express as px

def kpi_cards(st, df_monthly):
    if df_monthly.empty:
        st.warning("No data for KPIs")
        return
    revenue = int(df_monthly['revenue'].sum())
    orders = int(df_monthly['orders'].sum())
    customers = int(df_monthly['customers'].sum()) if 'customers' in df_monthly else orders
    aov = revenue / orders if orders > 0 else 0
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"RM {revenue:,.0f}")
    col2.metric("Total Orders", f"{orders:,}")
    col3.metric("Customers", f"{customers:,}")
    col4.metric("Average Order Value", f"RM {aov:,.2f}")

def line_monthly(df):
    # Ensure the DataFrame has 'month' and 'revenue'
    if 'month' not in df.columns:
        st.error("line_monthly: DataFrame missing 'month' column. Columns: " + str(df.columns.tolist()))
        return px.line(title="Error")
    fig = px.line(df, x="month", y="revenue", title="Monthly Revenue")
    return fig

def donut_share(df):
    fig = px.pie(df, names="channel", values="revenue", hole=0.5, title="Channel Share")
    return fig

def bar_top(df):
    fig = px.bar(df, x="revenue", y="product", orientation='h', title="Top Products by Revenue")
    return fig
