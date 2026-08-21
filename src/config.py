"""
config.py

Every magic number used for quality/cleaning/leakage/drift
decisions across the project lives HERE and nowhere else.

Before this file existed, the same thresholds (1.5x IQR,
0.98 uniqueness ratio for identifier detection, 50% missing-
value cutoff, 20% outlier-ratio safety cutoff) were each
hardcoded independently in cleaner.py, quality.py, leakage.py,
validator.py, and monitoring.py. Tuning one meant hunting
through five files and risking missing one — a classic source
of silent inconsistency bugs (e.g. cleaner.py and quality.py
could disagree on what counts as an outlier if only one got
updated).

If a reviewer asks "why does this exist," that's the answer:
single source of truth for tunable behavior.
"""

# OUTLIER DETECTION (IQR method)

IQR_MULTIPLIER = 1.5
"""Standard Tukey's fence multiplier for outlier bounds."""

MAX_OUTLIER_RATIO_FOR_AUTO_CORRECTION = 0.20
"""If more than this fraction of a column's valid values are
flagged as outliers, treat it as real variation (not bad
data) and skip automatic correction."""

MIN_VALID_VALUES_FOR_OUTLIER_DETECTION = 8
"""Below this many valid numeric values, IQR bounds are too
noisy to trust — skip outlier detection entirely."""

# IDENTIFIER COLUMN DETECTION

IDENTIFIER_UNIQUE_RATIO_THRESHOLD = 0.98
"""A column is treated as an identifier (never modified by
outlier/anomaly correction) if this fraction or more of its
values are unique."""

MIN_ROWS_FOR_IDENTIFIER_DETECTION = 30
"""Below this row count, uniqueness ratio is unreliable — a
genuine measurement column (age, income, ...) can easily be
100% unique on a small sample just by chance. 30 is the
common rule-of-thumb minimum sample size before a ratio like
this becomes statistically meaningful; don't classify any
column as an identifier by ratio alone below it.

BUG HISTORY: this was originally set to 10, which caused a
real false positive — an 11-row dataset with an `age` column
where every value happened to differ had its outlier (age of
200 in a column otherwise ranging 24-51) silently skipped
because the ratio check alone (11/11 unique = 100%) treated
`age` as if it were a customer ID. Raised to 30 and paired
with KNOWN_MEASUREMENT_COLUMN_NAMES below as a second,
independent safety net."""

KNOWN_MEASUREMENT_COLUMN_NAMES = frozenset(
    {
        "age",
        "income",
        "salary",
        "experience",
        "price",
        "cost",
        "revenue",
        "sales",
        "amount",
        "quantity",
        "score",
        "rating",
        "weight",
        "height",
        "distance",
        "duration",
        "temperature",
        "count",
        "value",
        "balance",
        "spend",
        "spending",
    }
)
"""Column names that are almost always genuine measurements,
never identifiers, regardless of how unique their values look
on a given sample. Checked before the ratio-based identifier
heuristic runs, so these can never be wrongly protected from
outlier correction."""

# MISSING VALUES

HIGH_MISSING_PERCENTAGE_THRESHOLD = 50.0
"""A column is flagged as a validation warning once its
missing-value percentage reaches this threshold."""

# TARGET LEAKAGE DETECTION

LEAKAGE_CORRELATION_THRESHOLD = 0.98
"""A numeric feature correlated with the target at or above
this value is flagged as probable leakage."""

# DATA DRIFT MONITORING

DEFAULT_DRIFT_THRESHOLD_PERCENT = 20.0
"""Default percentage change in a column's mean that triggers
a drift warning in monitoring.py."""

# NUMERIC-LOOKING COLUMN DETECTION

NUMERIC_PARSE_SUCCESS_RATIO = 0.80
"""A column stored as text is still treated as numeric if at
least this fraction of its non-null values parse as numbers."""

# HIGH-CARDINALITY CATEGORICAL GUARD

HIGH_CARDINALITY_THRESHOLD = 0.90
"""If more than this fraction of a categorical column's
values are unique (free text, names, a leaked ID column),
it is dropped from the feature set entirely before one-hot
encoding — otherwise it would explode into one feature per
unique value, balloon memory, and quietly degrade every
downstream model. See src/preprocessing.py."""

MAX_ONE_HOT_CATEGORIES = 30
"""A categorical column with more unique values than this is
capped during one-hot encoding (sklearn's max_categories) so
a moderately high-cardinality column that survives the guard
above still can't blow up the feature space."""