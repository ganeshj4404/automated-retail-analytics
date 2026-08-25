def check_revenue_growth(monthly_revenue):

    alerts = []

    previous_revenue = None

    for i, (month, revenue) in enumerate(monthly_revenue):

        # Skip the final month because it may be incomplete
        if i == len(monthly_revenue) - 1:
            continue

        if previous_revenue is not None:

            growth = (
                (revenue - previous_revenue)
                / previous_revenue
            ) * 100

            if growth <= -20:
                alerts.append(
                    f"ALERT: Revenue dropped {growth:.2f}% in {month}"
                )

            elif growth >= 30:
                alerts.append(
                    f"ALERT: Revenue increased {growth:.2f}% in {month}"
                )

        previous_revenue = revenue

    return alerts