import pandas as pd


def validate_data(df):

    validation_report = {}

    # -----------------------------
    # Missing Values
    # -----------------------------

    missing_values = df.isnull().sum()

    validation_report["missing_values"] = missing_values.to_dict()

    # -----------------------------
    # Duplicate Rows
    # -----------------------------

    duplicate_count = df.duplicated().sum()

    validation_report["duplicate_rows"] = duplicate_count

    # -----------------------------
    # Negative Quantity
    # -----------------------------

    negative_quantity = (df["Quantity"] < 0).sum()

    validation_report["negative_quantity"] = negative_quantity

    # -----------------------------
    # Invalid Prices
    # -----------------------------

    invalid_price = (df["UnitPrice"] <= 0).sum()

    validation_report["invalid_price"] = invalid_price

    # -----------------------------
    # Cancelled Transactions
    # -----------------------------

    cancelled_transactions = (
        df["InvoiceNo"]
        .astype(str)
        .str.startswith("C")
        .sum()
    )

    validation_report["cancelled_transactions"] = cancelled_transactions

    return validation_report