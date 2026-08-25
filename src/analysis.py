import sqlite3
import pandas as pd


def run_analysis(database_path):

    connection = sqlite3.connect(database_path)

    # --------------------------------
    # 1. Total Revenue
    # --------------------------------

    revenue_query = """
    SELECT 
        SUM(TransactionValue) AS total_revenue
    FROM retail_transactions;
    """

    result = connection.execute(revenue_query).fetchone()

    print("\n========== SQL ANALYSIS ==========")
    print("Total Revenue:", result[0])


    # --------------------------------
    # 2. Top 10 Products by Revenue
    # --------------------------------

    product_query = """
    SELECT
        StockCode,
        Description,
        SUM(TransactionValue) AS revenue
    FROM retail_transactions
    GROUP BY StockCode, Description
    ORDER BY revenue DESC
    LIMIT 10;
    """

    products = connection.execute(product_query).fetchall()

    print("\n========== TOP 10 PRODUCTS BY REVENUE ==========")

    for product in products:
        print(product)


    # --------------------------------
    # 3. Revenue by Country
    # --------------------------------

    country_query = """
    SELECT
        Country,
        SUM(TransactionValue) AS revenue
    FROM retail_transactions
    GROUP BY Country
    ORDER BY revenue DESC
    LIMIT 10;
    """

    countries = connection.execute(country_query).fetchall()

    print("\n========== TOP 10 COUNTRIES BY REVENUE ==========")

    for country in countries:
        print(country)


    # --------------------------------
    # 4. Top 10 Customers by Revenue
    # --------------------------------

    customer_query = """
    SELECT
        CustomerID,
        SUM(TransactionValue) AS total_revenue
    FROM retail_transactions
    WHERE CustomerID IS NOT NULL
    GROUP BY CustomerID
    ORDER BY total_revenue DESC
    LIMIT 10;
    """

    top_customers = connection.execute(customer_query).fetchall()

    print("\n========== TOP 10 CUSTOMERS BY REVENUE ==========")

    for customer in top_customers:
        print(customer)


    # --------------------------------
    # 5. Customer Order Frequency
    # --------------------------------

    frequency_query = """
    SELECT
        CustomerID,
        COUNT(DISTINCT InvoiceNo) AS number_of_orders
    FROM retail_transactions
    WHERE CustomerID IS NOT NULL
    GROUP BY CustomerID
    ORDER BY number_of_orders DESC
    LIMIT 10;
    """

    frequent_customers = connection.execute(frequency_query).fetchall()

    print("\n========== TOP 10 CUSTOMERS BY ORDER FREQUENCY ==========")

    for customer in frequent_customers:
        print(customer)


    # --------------------------------
    # 6. Average Order Value
    # --------------------------------

    aov_query = """
    SELECT
        CustomerID,
        SUM(TransactionValue) / COUNT(DISTINCT InvoiceNo) AS average_order_value
    FROM retail_transactions
    WHERE CustomerID IS NOT NULL
    GROUP BY CustomerID
    HAVING COUNT(DISTINCT InvoiceNo) >= 2
    ORDER BY average_order_value DESC
    LIMIT 10;
    """

    high_value_customers = connection.execute(aov_query).fetchall()

    print("\n========== TOP 10 CUSTOMERS BY AVERAGE ORDER VALUE ==========")

    for customer in high_value_customers:
        print(customer)


    # --------------------------------
    # 7. RFM Customer Analysis
    # --------------------------------

    rfm_query = """
    SELECT
        CustomerID,

        CAST(
            julianday(
                (SELECT MAX(InvoiceDate)
                 FROM retail_transactions)
            )
            - julianday(MAX(InvoiceDate))
            AS INTEGER
        ) AS Recency,

        COUNT(DISTINCT InvoiceNo) AS Frequency,

        SUM(TransactionValue) AS Monetary

    FROM retail_transactions

    WHERE CustomerID IS NOT NULL

    GROUP BY CustomerID;
    """

    rfm_data = connection.execute(rfm_query).fetchall()

    rfm_df = pd.DataFrame(
        rfm_data,
        columns=[
            "CustomerID",
            "Recency",
            "Frequency",
            "Monetary"
        ]
    )

    print("\n========== RFM CUSTOMER ANALYSIS ==========")

    print(rfm_df.head(10))


    # --------------------------------
    # Calculate RFM Scores
    # --------------------------------

    rfm_df["R_Score"] = pd.qcut(
        rfm_df["Recency"],
        5,
        labels=[5, 4, 3, 2, 1]
    )

    rfm_df["F_Score"] = pd.qcut(
        rfm_df["Frequency"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5]
    )

    rfm_df["M_Score"] = pd.qcut(
        rfm_df["Monetary"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5]
    )

    rfm_df["RFM_Score"] = (
        rfm_df["R_Score"].astype(str)
        + rfm_df["F_Score"].astype(str)
        + rfm_df["M_Score"].astype(str)
    )

    print("\n========== RFM SCORES ==========")

    print(
        rfm_df[
            [
                "CustomerID",
                "Recency",
                "Frequency",
                "Monetary",
                "RFM_Score"
            ]
        ].head(10)
    )


    # --------------------------------
    # Customer Segmentation
    # --------------------------------

    def segment_customer(row):

        r = int(row["R_Score"])
        f = int(row["F_Score"])
        m = int(row["M_Score"])

        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"

        elif r >= 3 and f >= 4:
            return "Loyal Customers"

        elif r >= 4 and m >= 4:
            return "High Value"

        elif r <= 2 and f >= 3 and m >= 3:
            return "At Risk"

        elif r <= 2 and f <= 2:
            return "Lost Customers"

        else:
            return "Regular Customers"


    rfm_df["Segment"] = rfm_df.apply(
        segment_customer,
        axis=1
    )

    print("\n========== CUSTOMER SEGMENTS ==========")

    print(
        rfm_df["Segment"].value_counts()
    )


    # --------------------------------
    # Top Champion Customers
    # --------------------------------

    print("\n========== TOP CHAMPION CUSTOMERS ==========")

    champions = rfm_df[
        rfm_df["Segment"] == "Champions"
    ].sort_values(
        "Monetary",
        ascending=False
    )

    print(
        champions[
            [
                "CustomerID",
                "Recency",
                "Frequency",
                "Monetary",
                "RFM_Score"
            ]
        ].head(10)
    )
        # --------------------------------
    # Save RFM Analysis
    # --------------------------------

    rfm_output_path = "data/processed/customer_rfm_analysis.csv"

    rfm_df.to_csv(
        rfm_output_path,
        index=False
    )

    print("\nRFM analysis saved successfully!")
    print("Output file:", rfm_output_path)


    # --------------------------------
    # 8. Monthly Revenue & Growth
    # --------------------------------

    monthly_query = """
    SELECT
        strftime('%Y-%m', InvoiceDate) AS month,
        SUM(TransactionValue) AS revenue
    FROM retail_transactions
    GROUP BY month
    ORDER BY month;
    """

    monthly_revenue = connection.execute(
        monthly_query
    ).fetchall()

    print("\n========== MONTHLY REVENUE ==========")

    previous_revenue = None

    for month, revenue in monthly_revenue:

        if previous_revenue is None:

            growth = None

        else:

            growth = (
                (revenue - previous_revenue)
                / previous_revenue
            ) * 100

        if growth is None:

            print(
                f"{month}: Revenue = {revenue:.2f}"
            )

        else:

            print(
                f"{month}: Revenue = {revenue:.2f}, "
                f"MoM Growth = {growth:.2f}%"
            )

        previous_revenue = revenue


    # --------------------------------
    # Close Database
    # --------------------------------

    connection.close()

    return monthly_revenue