import pandas as pd


def generate_recommendations(
    quality_score: float,
    issues: list,
    drift_warnings: list | None = None,
    class_balance: dict | None = None,
) -> list:
    """
    Generate actionable recommendations based on:
    - overall data quality
    - detected quality issues
    - data drift warnings
    - target class balance (classification tasks only)

    Priority is determined by actual risk:
    High > Medium > Low
    """

    recommendations = []

    drift_warnings = drift_warnings or []
    issues = issues or []

    # DETERMINE HIGHEST ISSUE SEVERITY

    severity_order = {
        "High": 3,
        "Medium": 2,
        "Low": 1,
    }

    highest_issue_severity = "Low"

    for issue in issues:

        severity = issue.get(
            "severity",
            "Low",
        )

        if severity_order.get(
            severity,
            0,
        ) > severity_order.get(
            highest_issue_severity,
            0,
        ):

            highest_issue_severity = severity

    # DATA QUALITY RECOMMENDATION

    if quality_score < 60:

        recommendations.append(
            {
                "priority": "High",
                "area": "Data Quality",
                "recommendation": (
                    "Data quality is poor. Clean and validate "
                    "the dataset before using it for machine "
                    "learning."
                ),
            }
        )

    elif highest_issue_severity == "High":

        recommendations.append(
            {
                "priority": "High",
                "area": "Data Quality",
                "recommendation": (
                    "High-severity data-quality issues were "
                    "detected. Review and resolve them before "
                    "model training."
                ),
            }
        )

    elif quality_score < 80:

        recommendations.append(
            {
                "priority": "Medium",
                "area": "Data Quality",
                "recommendation": (
                    "Review the detected data-quality issues "
                    "before model training."
                ),
            }
        )

    elif issues:

        recommendations.append(
            {
                "priority": highest_issue_severity,
                "area": "Data Quality",
                "recommendation": (
                    "The dataset is generally usable, but "
                    "some quality issues should be reviewed."
                ),
            }
        )

    else:

        recommendations.append(
            {
                "priority": "Low",
                "area": "Data Quality",
                "recommendation": (
                    "Dataset quality is good. Continue "
                    "monitoring future data."
                ),
            }
        )

    # CLEANING RECOMMENDATION

    if issues:

        cleaning_priority = highest_issue_severity

        recommendations.append(
            {
                "priority": cleaning_priority,
                "area": "Cleaning",
                "recommendation": (
                    f"{len(issues)} data-quality issue(s) "
                    "were detected. Run automatic cleaning "
                    "and review the cleaning audit log."
                ),
            }
        )

    # DATA DRIFT RECOMMENDATION

    if drift_warnings:

        recommendations.append(
            {
                "priority": "High",
                "area": "Data Drift",
                "recommendation": (
                    f"{len(drift_warnings)} drift warning(s) "
                    "were detected. Investigate changes in "
                    "the incoming dataset before relying on "
                    "model results."
                ),
            }
        )

    # CLASS IMBALANCE RECOMMENDATION

    if class_balance and class_balance.get("is_imbalanced"):

        minority_class = class_balance.get("minority_class")
        minority_ratio = class_balance.get("minority_ratio", 0)

        if class_balance.get("too_few_to_split"):

            recommendations.append(
                {
                    "priority": "High",
                    "area": "Class Imbalance",
                    "recommendation": (
                        f"Class '{minority_class}' has only "
                        f"{class_balance.get('minority_count')} "
                        "example(s) — too few to reliably "
                        "split into train/test sets. Collect "
                        "more examples of this class, or "
                        "treat model results for it with "
                        "caution."
                    ),
                }
            )

        else:

            recommendations.append(
                {
                    "priority": "High",
                    "area": "Class Imbalance",
                    "recommendation": (
                        f"The target is heavily imbalanced — "
                        f"class '{minority_class}' makes up "
                        f"only {minority_ratio:.1%} of rows. "
                        "Accuracy alone can be misleading "
                        "here; check precision/recall/F1 per "
                        "class, and consider resampling or "
                        "class weighting."
                    ),
                }
            )

    return recommendations


def recommendations_to_dataframe(
    recommendations: list,
) -> pd.DataFrame:
    """
    Convert recommendations into a DataFrame.
    """

    if not recommendations:

        return pd.DataFrame(
            columns=[
                "priority",
                "area",
                "recommendation",
            ]
        )

    return pd.DataFrame(
        recommendations
    )