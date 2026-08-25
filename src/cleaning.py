import pandas as pd


def clean_data(df):

    df = df.copy()

    # --------------------------------
    # 1. Remove exact duplicate rows
    # --------------------------------

    df = df.drop_duplicates()

    # --------------------------------
    # 2. Remove records with missing
    #    product descriptions
    # --------------------------------

    df = df.dropna(subset=["Description"])

    # --------------------------------
    # 3. Remove records with
    #    invalid prices
    # --------------------------------

    df = df[df["UnitPrice"] > 0]

    # --------------------------------
    # 4. Separate cancelled/returned
    #    transactions
    # --------------------------------

    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]

    # --------------------------------
    # 5. Keep only positive quantities
    #    for the sales dataset
    # --------------------------------

    df = df[df["Quantity"] > 0]

    return df