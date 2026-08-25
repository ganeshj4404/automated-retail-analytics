import pandas as pd


def detect_anomalies(df, column):

    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)

    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    anomaly_mask = (
        (df[column] < lower_bound) |
        (df[column] > upper_bound)
    )

    return anomaly_mask, lower_bound, upper_bound