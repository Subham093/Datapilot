# DataPilot Edge-Case CSV Test Pack

Use these files one at a time in DataPilot.

Expected behavior:
- DataPilot should not crash.
- Cleaning should complete or fail gracefully with a clear user-facing message.
- Suspicious columns should be reported rather than silently used.
- ML should refuse/guide the user when the dataset is unsuitable for training.

Files:
01_mixed_numeric_decimal.csv        - decimal value in an integer-like column
02_all_missing_column.csv           - completely empty column
03_constant_columns.csv             - constant numeric/text columns
04_duplicate_rows.csv               - duplicate records
05_extreme_class_imbalance.csv     - almost all target values are one class
06_identifier_high_cardinality.csv - IDs/emails with high cardinality
07_target_leakage.csv              - exact target copy + target-like column names
08_numeric_as_text.csv              - numeric-looking strings and messy currency values
09_messy_text.csv                   - Unicode, quotes, commas and embedded newlines
10_mixed_dates.csv                  - multiple date formats + invalid date
11_tiny_dataset.csv                 - very small dataset
12_no_target_dataset.csv            - no obvious supervised-learning target
13_single_class_target.csv          - target has only one class
14_inf_and_extreme_values.csv       - +/- infinity and extreme magnitudes
15_mostly_missing.csv                - heavily missing dataset
16_weird_column_names.csv            - spaces, symbols and Unicode in column names
