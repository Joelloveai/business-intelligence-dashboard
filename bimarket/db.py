import pandas as pd
import streamlit as st


@st.cache_data(ttl=600)
def fetch_df(query_name, params=None):
    """
    Reads data from data/sales.csv and returns the required dataframe.
    query_name: 'MONTHLY_KPIS', 'CHANNEL_SHARE', or 'TOP_PRODUCTS'
    params: dict with 'start' and 'end' date strings (ISO format)
    """
    try:
        df = pd.read_csv("data/sales.csv", parse_dates=["date"])
    except FileNotFoundError:
        print("ERROR: data/sales.csv not found")
        # Return empty DataFrames with expected columns
        if query_name == "MONTHLY_KPIS":
            return pd.DataFrame(columns=["month", "revenue", "orders", "aov"])
        elif query_name == "CHANNEL_SHARE":
            return pd.DataFrame(columns=["channel", "revenue"])
        elif query_name == "TOP_PRODUCTS":
            return pd.DataFrame(columns=["product", "revenue"])
        else:
            return pd.DataFrame()

    # Apply date filter
    if params and "start" in params and "end" in params:
        start = pd.to_datetime(params["start"])
        end = pd.to_datetime(params["end"])
        df = df[(df["date"] >= start) & (df["date"] <= end)]

    if df.empty:
        if query_name == "MONTHLY_KPIS":
            return pd.DataFrame(columns=["month", "revenue", "orders", "aov"])
        elif query_name == "CHANNEL_SHARE":
            return pd.DataFrame(columns=["channel", "revenue"])
        elif query_name == "TOP_PRODUCTS":
            return pd.DataFrame(columns=["product", "revenue"])
        else:
            return df

    if query_name == "MONTHLY_KPIS":
        # Create month column from date
        df["month"] = df["date"].dt.to_period("M").dt.start_time
        monthly = (
            df.groupby("month")
            .agg(revenue=("revenue", "sum"), orders=("orders", "sum"))
            .reset_index()
        )
        monthly["aov"] = monthly["revenue"] / monthly["orders"]
        return monthly

    elif query_name == "CHANNEL_SHARE":
        channel_share = df.groupby("channel")["revenue"].sum().reset_index()
        return channel_share

    elif query_name == "TOP_PRODUCTS":
        product_rev = df.groupby("product")["revenue"].sum().reset_index()
        top5 = product_rev.nlargest(5, "revenue")
        return top5

    else:
        return df
