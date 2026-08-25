import sqlite3
import pandas as pd


def load_to_database(df, database_path):
    
    connection = sqlite3.connect(database_path)

    df.to_sql(
        "retail_transactions",
        connection,
        if_exists="replace",
        index=False
    )

    connection.close()

    print("Data successfully loaded into SQLite database.")