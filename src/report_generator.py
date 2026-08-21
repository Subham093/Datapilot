from datetime import datetime


def generate_full_report(
    dataset_name: str,
    profile: dict,
    quality_score: float,
    issues: list,
    cleaning_log: list | None = None,
    leakage_warnings: list | None = None,
    ml_analysis: dict | None = None,
    best_model: str | None = None,
    evaluation_results=None,
    feature_importance=None,
    drift_warnings: list | None = None,
    recommendations: list | None = None,
) -> str:
    """
    Generate a complete human-readable DataPilot report.

    All new parameters default to None and are skipped
    entirely when not supplied, so existing callers that only
    pass the original arguments keep working unchanged.
    """

    report = []

    report.append(
        "DATAPILOT AUTONOMOUS AI DATA SCIENTIST REPORT"
    )

    report.append(
        "=" * 55
    )

    report.append("")

    report.append(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    report.append(
        f"Dataset: {dataset_name}"
    )

    report.append("")

    # DATASET OVERVIEW

    report.append(
        "DATASET OVERVIEW"
    )

    report.append(
        "-" * 30
    )

    report.append(
        f"Rows: {profile.get('rows', 'N/A')}"
    )

    report.append(
        f"Columns: {profile.get('columns', 'N/A')}"
    )

    report.append(
        f"Missing Values: "
        f"{profile.get('total_missing_values', 'N/A')}"
    )

    report.append(
        f"Duplicate Rows: "
        f"{profile.get('duplicate_rows', 'N/A')}"
    )

    report.append("")

    # QUALITY

    report.append(
        "DATA QUALITY"
    )

    report.append(
        "-" * 30
    )

    report.append(
        f"Quality Score: {quality_score}/100"
    )

    report.append(
        f"Issues Detected: {len(issues)}"
    )

    report.append("")

    if issues:

        for issue in issues:

            report.append(
                f"- {issue.get('type', 'Unknown')} | "
                f"{issue.get('column', 'N/A')} | "
                f"{issue.get('severity', 'N/A')} | "
                f"{issue.get('description', '')}"
            )

    else:

        report.append(
            "No major data-quality issues detected."
        )

    report.append("")

    # CLEANING

    if cleaning_log is not None:

        report.append(
            "CLEANING PERFORMED"
        )

        report.append(
            "-" * 30
        )

        report.append(
            f"Total Changes: {len(cleaning_log)}"
        )

        report.append("")

        if cleaning_log:

            report.append(
                "CLEANING AUDIT"
            )

            report.append(
                "-" * 30
            )

            for entry in cleaning_log:

                report.append(
                    f"- {entry.get('category', 'Unknown')} | "
                    f"{entry.get('column', 'N/A')} | "
                    f"{entry.get('action', 'N/A')} | "
                    f"count={entry.get('count', 'N/A')} | "
                    f"{entry.get('reason', '')}"
                )

        else:

            report.append(
                "No cleaning changes were needed."
            )

        report.append("")

    # ML ANALYSIS

    if ml_analysis is not None:

        report.append(
            "MACHINE LEARNING ANALYSIS"
        )

        report.append(
            "-" * 30
        )

        report.append(
            f"Target Column: "
            f"{ml_analysis.get('target_column', 'N/A')}"
        )

        report.append(
            f"Task Type: "
            f"{ml_analysis.get('task_type', 'N/A')}"
        )

        report.append(
            f"Features: "
            f"{ml_analysis.get('features', 'N/A')}"
        )

        class_balance = ml_analysis.get("class_balance")

        if class_balance and class_balance.get("is_imbalanced"):

            minority_class = class_balance.get("minority_class")
            minority_ratio = class_balance.get("minority_ratio", 0)
            minority_count = class_balance.get("minority_count")

            report.append(
                f"Class Imbalance: class '{minority_class}' "
                f"makes up only {minority_ratio:.1%} of rows "
                f"({minority_count} example(s)). Accuracy "
                "alone can be misleading for this dataset."
            )

        report.append("")

        # LEAKAGE CHECK

        if leakage_warnings is not None:

            report.append(
                "LEAKAGE CHECK"
            )

            report.append(
                "-" * 30
            )

            if leakage_warnings:

                for warning in leakage_warnings:

                    report.append(
                        f"- {warning.get('type', 'Unknown')} | "
                        f"{warning.get('column', 'N/A')} | "
                        f"{warning.get('severity', 'N/A')} | "
                        f"{warning.get('description', '')}"
                    )

            else:

                report.append(
                    "No target leakage warnings detected."
                )

            report.append("")

        if best_model:

            report.append(
                f"Best Model: {best_model}"
            )

            report.append("")

        if evaluation_results is not None:

            report.append(
                "MODEL COMPARISON"
            )

            if (
                hasattr(evaluation_results, "columns")
                and "cv_score" in evaluation_results.columns
            ):

                report.append(
                    "(includes cross-validation scores, "
                    "column: cv_score)"
                )

            report.append(
                str(evaluation_results)
            )

            report.append("")

        # FEATURE IMPORTANCE

        if feature_importance is not None:

            report.append(
                "FEATURE IMPORTANCE"
            )

            report.append(
                "-" * 30
            )

            is_empty = (
                hasattr(feature_importance, "empty")
                and feature_importance.empty
            )

            if is_empty:

                report.append(
                    "Feature importance is not available "
                    "for this model."
                )

            else:

                report.append(
                    str(feature_importance)
                )

            report.append("")

    # DRIFT

    if drift_warnings is not None:

        report.append(
            "DATA MONITORING"
        )

        report.append(
            "-" * 30
        )

        report.append(
            f"Drift Warnings: {len(drift_warnings)}"
        )

        if drift_warnings:

            for warning in drift_warnings:

                report.append(
                    f"- {warning.get('type', 'Unknown')} | "
                    f"{warning.get('column', 'N/A')} | "
                    f"{warning.get('severity', 'N/A')} | "
                    f"{warning.get('description', '')}"
                )

        else:

            report.append(
                "No drift warnings detected."
            )

        report.append("")

    # RECOMMENDATIONS

    if recommendations is not None:

        report.append(
            "RECOMMENDATIONS"
        )

        report.append(
            "-" * 30
        )

        for recommendation in recommendations:

            report.append(
                f"- [{recommendation.get('priority', 'N/A')}] "
                f"{recommendation.get('area', 'General')}: "
                f"{recommendation.get('recommendation', '')}"
            )

        report.append("")

    # FOOTER

    report.append(
        "=" * 55
    )

    report.append(
        "Generated automatically by DataPilot."
    )

    return "\n".join(report)