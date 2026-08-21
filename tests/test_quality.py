from src.quality import detect_quality_issues, calculate_quality_score


def test_no_issues_on_clean_data(clean_valid_df):
    issues = detect_quality_issues(clean_valid_df)
    assert issues == []


def test_quality_score_is_100_for_clean_data(clean_valid_df):
    issues = detect_quality_issues(clean_valid_df)
    score = calculate_quality_score(clean_valid_df, issues)
    assert score == 100


def test_missing_values_lower_the_score(messy_df):
    issues = detect_quality_issues(messy_df)
    score = calculate_quality_score(messy_df, issues)

    assert any(i["type"] == "Missing Values" for i in issues)
    assert score < 100
