import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PATHS
# ============================================================

DATABASE_PATH = "data/processed/retail_database.db"
RFM_PATH = "data/processed/customer_rfm_analysis.csv"


# ============================================================
# LOAD DATABASE
# ============================================================

@st.cache_data
def load_data():

    connection = sqlite3.connect(DATABASE_PATH)

    df = pd.read_sql_query(
        "SELECT * FROM retail_transactions",
        connection
    )

    connection.close()

    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"]
    )

    return df


@st.cache_data
def load_rfm_data():

    rfm = pd.read_csv(RFM_PATH)

    return rfm


df = load_data()
rfm_df = load_rfm_data()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📊 Retail Analytics")

st.sidebar.caption(
    "Automated Data Processing & Monitoring"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Overview",
        "📈 Revenue Analytics",
        "📦 Products & Countries",
        "👥 Customer & RFM",
        "🚨 Data Quality",
    ]
)


# ============================================================
# FILTERS
# ============================================================

st.sidebar.divider()

st.sidebar.subheader("🔎 Filters")

countries = sorted(
    df["Country"].dropna().unique()
)

selected_country = st.sidebar.selectbox(
    "Country",
    ["All Countries"] + countries
)


min_date = df["InvoiceDate"].min().date()
max_date = df["InvoiceDate"].max().date()


selected_dates = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()


if selected_country != "All Countries":

    filtered_df = filtered_df[
        filtered_df["Country"] == selected_country
    ]


if len(selected_dates) == 2:

    start_date = pd.Timestamp(
        selected_dates[0]
    )

    end_date = (
        pd.Timestamp(selected_dates[1])
        + pd.Timedelta(days=1)
    )

    filtered_df = filtered_df[
        (filtered_df["InvoiceDate"] >= start_date)
        &
        (filtered_df["InvoiceDate"] < end_date)
    ]


# ============================================================
# HEADER
# ============================================================

st.title("📊 Retail Analytics Dashboard")

st.caption(
    "Automated Data Processing, SQL Analytics, "
    "Customer Segmentation & Monitoring"
)


# ============================================================
# OVERVIEW
# ============================================================

if page == "📊 Overview":

    st.header("Business Overview")

    # -----------------------------
    # KPIs
    # -----------------------------

    total_revenue = filtered_df[
        "TransactionValue"
    ].sum()

    total_transactions = len(
        filtered_df
    )

    total_customers = filtered_df[
        "CustomerID"
    ].nunique()

    total_products = filtered_df[
        "StockCode"
    ].nunique()


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "💰 Total Revenue",
            f"{total_revenue:,.2f}"
        )


    with col2:

        st.metric(
            "👥 Customers",
            f"{total_customers:,}"
        )


    with col3:

        st.metric(
            "🧾 Transactions",
            f"{total_transactions:,}"
        )


    with col4:

        st.metric(
            "📦 Products",
            f"{total_products:,}"
        )


    st.divider()


    # -----------------------------
    # Monthly Revenue
    # -----------------------------

    st.subheader("📈 Revenue Trend")


    monthly_revenue = (
        filtered_df
        .assign(
            Month=filtered_df[
                "InvoiceDate"
            ].dt.to_period("M").astype(str)
        )
        .groupby(
            "Month",
            as_index=False
        )["TransactionValue"]
        .sum()
    )


    monthly_revenue.rename(
        columns={
            "TransactionValue": "Revenue"
        },
        inplace=True
    )


    monthly_revenue["MoM Growth"] = (
        monthly_revenue["Revenue"]
        .pct_change()
        * 100
    )


    fig = px.line(
        monthly_revenue,
        x="Month",
        y="Revenue",
        markers=True,
        title="Monthly Revenue"
    )


    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue",
        hovermode="x unified"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # -----------------------------
    # Quick Insights
    # -----------------------------

    st.subheader("💡 Quick Insights")


    if len(monthly_revenue) > 0:

        highest_month = monthly_revenue.loc[
            monthly_revenue["Revenue"].idxmax()
        ]

        lowest_month = monthly_revenue.loc[
            monthly_revenue["Revenue"].idxmin()
        ]


        col1, col2 = st.columns(2)


        with col1:

            st.info(
                f"🏆 Highest revenue month: "
                f"**{highest_month['Month']}** "
                f"with **{highest_month['Revenue']:,.2f}**"
            )


        with col2:

            st.info(
                f"📉 Lowest revenue month: "
                f"**{lowest_month['Month']}** "
                f"with **{lowest_month['Revenue']:,.2f}**"
            )


# ============================================================
# REVENUE ANALYTICS
# ============================================================

elif page == "📈 Revenue Analytics":

    st.header("📈 Revenue Analytics")


    monthly_revenue = (
        filtered_df
        .assign(
            Month=filtered_df[
                "InvoiceDate"
            ].dt.to_period("M").astype(str)
        )
        .groupby(
            "Month",
            as_index=False
        )["TransactionValue"]
        .sum()
    )


    monthly_revenue.rename(
        columns={
            "TransactionValue": "Revenue"
        },
        inplace=True
    )


    monthly_revenue["MoM Growth"] = (
        monthly_revenue["Revenue"]
        .pct_change()
        * 100
    )


    # -----------------------------
    # Revenue Chart
    # -----------------------------

    st.subheader("Monthly Revenue")


    fig_revenue = px.line(
        monthly_revenue,
        x="Month",
        y="Revenue",
        markers=True,
        title="Monthly Revenue Trend"
    )


    fig_revenue.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue",
        hovermode="x unified"
    )


    st.plotly_chart(
        fig_revenue,
        use_container_width=True
    )


    # -----------------------------
    # Growth Chart
    # -----------------------------

    st.subheader("📊 Month-over-Month Growth")


    growth_data = monthly_revenue.dropna(
        subset=["MoM Growth"]
    )


    fig_growth = px.bar(
        growth_data,
        x="Month",
        y="MoM Growth",
        text="MoM Growth",
        title="Monthly Revenue Growth"
    )


    fig_growth.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )


    fig_growth.update_layout(
        xaxis_title="Month",
        yaxis_title="Growth (%)"
    )


    st.plotly_chart(
        fig_growth,
        use_container_width=True
    )


    # -----------------------------
    # Revenue Table
    # -----------------------------

    st.subheader("Monthly Revenue Details")


    display_monthly = monthly_revenue.copy()

    display_monthly["Revenue"] = (
        display_monthly["Revenue"].round(2)
    )

    display_monthly["MoM Growth"] = (
        display_monthly["MoM Growth"].round(2)
    )


    st.dataframe(
        display_monthly,
        use_container_width=True,
        hide_index=True
    )


    # -----------------------------
    # Alerts
    # -----------------------------

    st.subheader("📡 Revenue Monitoring")


    alerts = monthly_revenue[
        monthly_revenue[
            "MoM Growth"
        ].abs() >= 20
    ]


    if len(alerts) == 0:

        st.success(
            "✅ No significant revenue changes detected."
        )

    else:

        st.warning(
            f"⚠️ {len(alerts)} significant "
            "revenue changes detected."
        )


        for _, row in alerts.iterrows():

            growth = row["MoM Growth"]
            month = row["Month"]


            if growth < 0:

                st.error(
                    f"🔴 Revenue dropped "
                    f"{growth:.2f}% in {month}"
                )

            else:

                st.success(
                    f"🟢 Revenue increased "
                    f"{growth:.2f}% in {month}"
                )


# ============================================================
# PRODUCTS & COUNTRIES
# ============================================================

elif page == "📦 Products & Countries":

    st.header("📦 Products & Country Analytics")


    # -----------------------------
    # Top Products
    # -----------------------------

    st.subheader("🏆 Top 10 Products by Revenue")


    top_products = (
        filtered_df
        .groupby(
            [
                "StockCode",
                "Description"
            ],
            as_index=False
        )["TransactionValue"]
        .sum()
        .sort_values(
            "TransactionValue",
            ascending=False
        )
        .head(10)
    )


    top_products["Product"] = (
        top_products["StockCode"].astype(str)
        + " - "
        + top_products[
            "Description"
        ].fillna("Unknown")
    )


    fig_products = px.bar(
        top_products.sort_values(
            "TransactionValue"
        ),
        x="TransactionValue",
        y="Product",
        orientation="h",
        title="Top Products by Revenue"
    )


    fig_products.update_layout(
        xaxis_title="Revenue",
        yaxis_title="Product"
    )


    st.plotly_chart(
        fig_products,
        use_container_width=True
    )


    # -----------------------------
    # Country Revenue
    # -----------------------------

    st.subheader("🌍 Top 10 Countries by Revenue")


    country_revenue = (
        filtered_df
        .groupby(
            "Country",
            as_index=False
        )["TransactionValue"]
        .sum()
        .sort_values(
            "TransactionValue",
            ascending=False
        )
        .head(10)
    )


    fig_country = px.bar(
        country_revenue.sort_values(
            "TransactionValue"
        ),
        x="TransactionValue",
        y="Country",
        orientation="h",
        title="Revenue by Country"
    )


    fig_country.update_layout(
        xaxis_title="Revenue",
        yaxis_title="Country"
    )


    st.plotly_chart(
        fig_country,
        use_container_width=True
    )


    # -----------------------------
    # Product Table
    # -----------------------------

    st.subheader("Product Revenue Details")


    product_table = top_products[
        [
            "StockCode",
            "Description",
            "TransactionValue"
        ]
    ].copy()


    product_table.rename(
        columns={
            "TransactionValue": "Revenue"
        },
        inplace=True
    )


    product_table["Revenue"] = (
        product_table["Revenue"].round(2)
    )


    st.dataframe(
        product_table,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# CUSTOMER & RFM
# ============================================================

elif page == "👥 Customer & RFM":

    st.header("👥 Customer Analytics & RFM")


    # -----------------------------
    # Customer KPIs
    # -----------------------------

    total_rfm_customers = (
        rfm_df["CustomerID"].nunique()
    )


    average_frequency = (
        rfm_df["Frequency"].mean()
    )


    average_monetary = (
        rfm_df["Monetary"].mean()
    )


    champion_count = (
        rfm_df["Segment"]
        .eq("Champions")
        .sum()
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "👥 RFM Customers",
            f"{total_rfm_customers:,}"
        )


    with col2:

        st.metric(
            "🔁 Avg Orders",
            f"{average_frequency:.1f}"
        )


    with col3:

        st.metric(
            "💰 Avg Customer Revenue",
            f"{average_monetary:,.2f}"
        )


    with col4:

        st.metric(
            "🏆 Champions",
            f"{champion_count:,}"
        )


    st.divider()


    # -----------------------------
    # Segmentation
    # -----------------------------

    st.subheader("🎯 Customer Segmentation")


    segment_counts = (
        rfm_df["Segment"]
        .value_counts()
        .reset_index()
    )


    segment_counts.columns = [
        "Segment",
        "Customers"
    ]


    fig_segments = px.pie(
        segment_counts,
        names="Segment",
        values="Customers",
        hole=0.45,
        title="Customer Distribution"
    )


    fig_segments.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )


    st.plotly_chart(
        fig_segments,
        use_container_width=True
    )


    # -----------------------------
    # RFM Scatter
    # -----------------------------

    st.subheader("📊 Customer Value Analysis")


    fig_rfm = px.scatter(
        rfm_df,
        x="Frequency",
        y="Monetary",
        size="Monetary",
        color="Segment",
        hover_data=[
            "CustomerID",
            "Recency",
            "Frequency",
            "Monetary",
            "RFM_Score"
        ],
        log_y=True,
        title="Customer Frequency vs Monetary Value"
    )


    fig_rfm.update_layout(
        xaxis_title="Purchase Frequency",
        yaxis_title="Monetary Value"
    )


    st.plotly_chart(
        fig_rfm,
        use_container_width=True
    )


    # -----------------------------
    # Segment Summary
    # -----------------------------

    st.subheader("Customer Segment Summary")


    segment_summary = (
        rfm_df
        .groupby("Segment")
        .agg(
            Customers=("CustomerID", "count"),
            Avg_Recency=("Recency", "mean"),
            Avg_Frequency=("Frequency", "mean"),
            Revenue=("Monetary", "sum")
        )
        .reset_index()
    )


    segment_summary["Avg_Recency"] = (
        segment_summary["Avg_Recency"].round(1)
    )


    segment_summary["Avg_Frequency"] = (
        segment_summary["Avg_Frequency"].round(1)
    )


    segment_summary["Revenue"] = (
        segment_summary["Revenue"].round(2)
    )


    st.dataframe(
        segment_summary,
        use_container_width=True,
        hide_index=True
    )


    # -----------------------------
    # Top Customers
    # -----------------------------

    st.subheader("🏆 Top Customers by Revenue")


    top_customers = (
        rfm_df
        .sort_values(
            "Monetary",
            ascending=False
        )
        .head(10)
    )


    display_customers = top_customers[
        [
            "CustomerID",
            "Recency",
            "Frequency",
            "Monetary",
            "RFM_Score",
            "Segment"
        ]
    ].copy()


    display_customers["Monetary"] = (
        display_customers["Monetary"].round(2)
    )


    st.dataframe(
        display_customers,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# DATA QUALITY
# ============================================================

elif page == "🚨 Data Quality":

    st.header("🚨 Data Quality & Anomaly Monitoring")


    # -----------------------------
    # Anomalies
    # -----------------------------

    quantity_anomalies = int(
        df["Quantity_Anomaly"].sum()
    )


    price_anomalies = int(
        df["Price_Anomaly"].sum()
    )


    transaction_anomalies = int(
        df["TransactionValue_Anomaly"].sum()
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "📦 Quantity Anomalies",
            f"{quantity_anomalies:,}"
        )


    with col2:

        st.metric(
            "💲 Price Anomalies",
            f"{price_anomalies:,}"
        )


    with col3:

        st.metric(
            "💰 Transaction Anomalies",
            f"{transaction_anomalies:,}"
        )


    st.divider()


    # -----------------------------
    # Anomaly Chart
    # -----------------------------

    anomaly_data = pd.DataFrame({

        "Anomaly Type": [
            "Quantity",
            "Price",
            "Transaction Value"
        ],

        "Records": [
            quantity_anomalies,
            price_anomalies,
            transaction_anomalies
        ]

    })


    fig_anomalies = px.bar(
        anomaly_data,
        x="Anomaly Type",
        y="Records",
        text="Records",
        title="Detected Data Anomalies"
    )


    fig_anomalies.update_traces(
        textposition="outside"
    )


    fig_anomalies.update_layout(
        xaxis_title="Anomaly Type",
        yaxis_title="Records"
    )


    st.plotly_chart(
        fig_anomalies,
        use_container_width=True
    )


    # -----------------------------
    # Data Quality
    # -----------------------------

    st.subheader("🔍 Data Quality Summary")


    quality_data = pd.DataFrame({

        "Data Quality Check": [

            "Missing Descriptions",
            "Missing Customer IDs",
            "Duplicate Records",
            "Negative Quantity Records",
            "Zero/Negative Price Records",
            "Cancelled Transactions"

        ],

        "Records": [

            1454,
            135080,
            5268,
            10624,
            2517,
            9288

        ]

    })


    st.dataframe(
        quality_data,
        use_container_width=True,
        hide_index=True
    )


    # -----------------------------
    # Cleaning Summary
    # -----------------------------

    st.subheader("🧹 Data Cleaning Summary")


    original_records = 541909

    cleaned_records = len(df)

    records_removed = (
        original_records
        - cleaned_records
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Raw Records",
            f"{original_records:,}"
        )


    with col2:

        st.metric(
            "Processed Records",
            f"{cleaned_records:,}"
        )


    with col3:

        st.metric(
            "Records Removed",
            f"{records_removed:,}"
        )


    st.success(
        "✅ Data validation, cleaning and "
        "anomaly detection pipeline completed."
    )