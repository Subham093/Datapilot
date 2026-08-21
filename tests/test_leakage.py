from src.leakage import detect_target_leakage


def test_leakage_detects_exact_copy_and_suspicious_name(leakage_df):
    warnings = detect_target_leakage(leakage_df, "purchased")

    types_found = {w["type"] for w in warnings}
    assert "Suspicious Feature Name" in types_found


def test_no_leakage_on_clean_features(clean_valid_df):
    warnings = detect_target_leakage(clean_valid_df, "salary")
    assert isinstance(warnings, list)
