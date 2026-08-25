import pandas as pd

from src.validation import validate_data
from src.cleaning import clean_data
from src.anomaly_detection import detect_anomalies
from src.database import load_to_database
from src.analysis import run_analysis
from src.monitoring import check_revenue_growth

# -----------------------------
# Load Dataset
# -----------------------------

file_path = "data/raw/Online Retail.xlsx"

df = pd.read_excel(file_path)

print("Dataset loaded successfully!")
print("Number of rows:", len(df))
print("Number of columns:", len(df.columns))


# -----------------------------
# Validate Dataset
# -----------------------------

validation_report = validate_data(df)


# -----------------------------
# Display Validation Report
# -----------------------------

print("\n========== DATA VALIDATION REPORT ==========")

print("\nMissing Values:")
print(validation_report["missing_values"])

print("\nDuplicate Rows:")
print(validation_report["duplicate_rows"])

print("\nNegative Quantity Records:")
print(validation_report["negative_quantity"])

print("\nZero/Negative Price Records:")
print(validation_report["invalid_price"])

print("\nCancelled Transactions:")
print(validation_report["cancelled_transactions"])

# -----------------------------
# Clean Dataset
# -----------------------------

cleaned_df = clean_data(df)

print("\n========== CLEANING REPORT ==========")

print("Original records:", len(df))
print("Cleaned records:", len(cleaned_df))
print("Records removed:", len(df) - len(cleaned_df))

# -----------------------------
# Save Cleaned Dataset
# -----------------------------

output_path = "data/processed/cleaned_retail_data.csv"



# -----------------------------
# Anomaly Detection
# -----------------------------

quantity_anomalies, quantity_lower, quantity_upper = detect_anomalies(
    cleaned_df,
    "Quantity"
)

price_anomalies, price_lower, price_upper = detect_anomalies(
    cleaned_df,
    "UnitPrice"
)

cleaned_df["Quantity_Anomaly"] = quantity_anomalies
cleaned_df["Price_Anomaly"] = price_anomalies

# -----------------------------
# Calculate Transaction Value
# -----------------------------

cleaned_df["TransactionValue"] = (
    cleaned_df["Quantity"] * cleaned_df["UnitPrice"]
)

print("\n========== ANOMALY DETECTION ==========")

print("Quantity lower boundary:", quantity_lower)
print("Quantity upper boundary:", quantity_upper)

print("Quantity anomalies:", quantity_anomalies.sum())

print("\nPrice lower boundary:", price_lower)
print("Price upper boundary:", price_upper)

print("Price anomalies:", price_anomalies.sum())

transaction_anomalies, transaction_lower, transaction_upper = detect_anomalies(
    cleaned_df,
    "TransactionValue"
)

cleaned_df["TransactionValue_Anomaly"] = transaction_anomalies

print("\nTransaction Value lower boundary:", transaction_lower)
print("Transaction Value upper boundary:", transaction_upper)
print("Transaction Value anomalies:", transaction_anomalies.sum())

# -----------------------------
# Save Final Processed Dataset
# -----------------------------

output_path = "data/processed/cleaned_retail_data.csv"

cleaned_df.to_csv(output_path, index=False)

print("\nFinal processed dataset saved successfully!")
print("Output file:", output_path)

# -----------------------------
# Load Data into SQLite
# -----------------------------

database_path = "data/processed/retail_database.db"

load_to_database(
    cleaned_df,
    database_path
)

# -----------------------------
# Run SQL Analysis
# -----------------------------

monthly_revenue = run_analysis(database_path)

# -----------------------------
# Automated Monitoring
# -----------------------------

alerts = check_revenue_growth(monthly_revenue)

print("\n========== MONITORING ALERTS ==========")

if alerts:
    for alert in alerts:
        print(alert)
else:
    print("No significant revenue changes detected.")