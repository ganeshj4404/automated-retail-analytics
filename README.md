# Automated Retail Analytics & Data Processing Pipeline

An end-to-end retail analytics project built using Python, SQL, Pandas, NumPy, SQLite, and Streamlit.

The project processes a large public retail transaction dataset, performs automated data validation and cleaning, detects anomalies, conducts SQL-based business analysis, performs RFM customer segmentation, monitors revenue changes, and presents the results through an interactive Streamlit dashboard.

---

## 📊 Dashboard

![Retail Analytics Dashboard](dashboard_screenshot.png)

The dashboard provides an interactive view of:

- Total Revenue
- Number of Customers
- Number of Transactions
- Number of Products
- Monthly Revenue Trends
- Revenue Growth
- Country-level Analysis
- Customer Analysis
- RFM Customer Segmentation
- Data Anomaly Information
- Revenue Alerts

---

## 🚀 Project Features

### 1. Automated Data Processing

The pipeline automatically:

- Loads the Online Retail dataset
- Validates the incoming data
- Detects missing values
- Detects duplicate records
- Identifies cancelled transactions
- Detects invalid quantities
- Detects invalid prices
- Cleans the dataset
- Saves the processed dataset

The original dataset contains:

**541,909 records**

After cleaning:

**524,878 records**

---

### 2. Data Validation

The pipeline generates a validation report containing:

- Missing values
- Duplicate records
- Negative quantity records
- Zero/negative price records
- Cancelled transactions

Example:

```text
Missing Values:
Description      1454
CustomerID     135080

Duplicate Rows:
5268

Negative Quantity Records:
10624

Zero/Negative Price Records:
2517

Cancelled Transactions:
9288