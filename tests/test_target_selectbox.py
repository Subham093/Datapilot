from src.task_detector import (
    NO_CONFIDENT_TARGET_LABEL,
    resolve_target_selectbox_options,
)


def test_confident_detection_preselects_the_right_column():
    """When auto-detection succeeds, the selectbox should
    default straight to that column — no placeholder needed."""

    options, index = resolve_target_selectbox_options(
        auto_detected_target="purchased",
        available_columns=["age", "income", "purchased"],
    )

    assert options == ["age", "income", "purchased"]
    assert options[index] == "purchased"


def test_no_confident_detection_never_defaults_to_first_column():
    """
    Regression test for a real bug: when detect_target_column()
    returns None (no confident guess), the dashboard used to
    fall back to `default_index = 0`, silently pre-selecting
    the FIRST column as if it were a real guess. This confirms
    that state is now an explicit placeholder the user must
    replace, never a real column.
    """

    options, index = resolve_target_selectbox_options(
        auto_detected_target=None,
        available_columns=["age", "income", "city"],
    )

    assert options[index] == NO_CONFIDENT_TARGET_LABEL
    assert options[0] == NO_CONFIDENT_TARGET_LABEL
    assert "age" not in [options[index]]


def test_placeholder_is_never_a_real_column_name():
    """The sentinel string must not collide with an actual
    dataset column, or a real column named exactly that would
    be silently swallowed."""

    options, _ = resolve_target_selectbox_options(
        auto_detected_target=None,
        available_columns=["age", "income", "city"],
    )

    assert NO_CONFIDENT_TARGET_LABEL not in ["age", "income", "city"]
    assert options.count(NO_CONFIDENT_TARGET_LABEL) == 1


def test_auto_detected_target_not_in_available_columns_falls_back_safely():
    """Defensive case: if the detected target somehow isn't in
    the available columns list (shouldn't normally happen, but
    must never crash), treat it the same as 'no confident
    target' rather than raising or guessing."""

    options, index = resolve_target_selectbox_options(
        auto_detected_target="some_column_that_does_not_exist",
        available_columns=["age", "income", "city"],
    )

    assert options[index] == NO_CONFIDENT_TARGET_LABEL