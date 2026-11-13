"""Basic cleaning for the Stack Overflow Developer Survey (any year).
 
Applies only the fixes the group has agreed on:
  - Text tidied: curly quotes -> straight, extra spaces removed
  - "Prefer not to say" / "I don't know" style answers -> NaN
  - Experience text ("2 to 3 years") -> numbers ONLY if convert_years=True
    (the group plans to do this after combining years)
  - Standard columns: year, uid, salary_usd, n_answered
    (plus has_salary, only when drop_no_salary=False)
  - Rows with no salary dropped (drop_no_salary=True)
Helpers for later (one-hot encoding, finding multi-select questions,
setting up a new year) are in later_helpers.py.
Open issues (low-salary cutoff, small countries, tick-all, HoursPerWeek) are NOT handled yet.
"""
import re
import numpy as np
import pandas as pd
 
# ---------------------------------------------------------------------------
# Settings per year. Check each year's schema.csv before adding it.
# ---------------------------------------------------------------------------
CONFIGS = {
    2017: dict(id_col="Respondent",
               salary_col="Salary",
               years_cols=["YearsProgram", "YearsCodedJob", "YearsCodedJobPast"]),
    2018: dict(id_col="Respondent",
               salary_col="ConvertedSalary",
               years_cols=["YearsCoding", "YearsCodingProf"]),
    2019: dict(id_col="Respondent",
               salary_col="ConvertedComp",
               years_cols=["YearsCode", "YearsCodePro"]),
    2020: dict(id_col="Respondent",
               salary_col="ConvertedComp",
               years_cols=["YearsCode", "YearsCodePro"]),
    2021: dict(id_col="ResponseId",
               salary_col="ConvertedCompYearly",
               years_cols=["YearsCode", "YearsCodePro"]),
    2025: dict(id_col="ResponseId",
               salary_col="ConvertedCompYearly",
               years_cols=["YearsCode", "WorkExp"]),
}
 
# Whole-cell answers that really mean "no answer" (both apostrophe styles)
NON_ANSWERS = [
    "I prefer not to say", "I prefer not to answer", "Prefer not to say",
    "I don't know", "I don’t know",
    "I don't know/not sure", "I'm not sure/I don't know", "Unsure / I don't know",
]
 
 
def parse_years(value):
    """Turn an experience answer into a number of years.
 
    "Less than a year" -> 0.5     "2 to 3 years" -> 2.5
    "20 or more years" -> 20      "More than 50 years" -> 50
    "14" or 14.0 -> 14.0          blank -> NaN
    """
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float, np.number)):
        return float(value)
    text = str(value).strip().lower()
    if text.startswith("less than"):
        return 0.5
    nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", text)]
    if not nums:
        return np.nan
    if len(nums) >= 2:                      # a range like "2 to 3 years"
        return (nums[0] + nums[1]) / 2
    return nums[0]                          # "20 or more", "More than 50", "14"
 
 
def clean_survey(raw, year, config=None, drop_no_salary=True, convert_years=False):
    """Return a cleaned COPY of one year's survey. The input is not changed.
 
    drop_no_salary=True  -> keep only people who reported a salary (default)
    drop_no_salary=False -> keep everyone (e.g. for plot_salary_sparsity)
    convert_years=False  -> leave experience as text, e.g. "2 to 3 years" (default)
    convert_years=True   -> turn experience into numbers, e.g. 2.5
    """
    cfg = config or CONFIGS[year]
    id_col, salary_col = cfg["id_col"], cfg["salary_col"]
    df = raw.copy()
 
    # How many questions each person answered (measured before any cleaning)
    df["n_answered"] = raw.drop(columns=id_col).notna().sum(axis=1)
 
    # Tidy text so the same answer is spelled the same way in every year:
    # curly quotes -> straight ("Bachelor’s" -> "Bachelor's"), strip extra spaces
    text_cols = df.select_dtypes(exclude="number").columns
    for col in text_cols:
        df[col] = (df[col].astype("string")
                          .str.replace("\u2019", "'", regex=False)
                          .str.replace("\u2018", "'", regex=False)
                          .str.replace("\u201c", '"', regex=False)
                          .str.replace("\u201d", '"', regex=False)
                          .str.strip()
                          .astype(object))
    df[text_cols] = df[text_cols].where(df[text_cols].notna(), np.nan)
 
    # Hidden missing values -> NaN (exact whole-cell matches only)
    before = df[text_cols].isna().sum().sum()
    df[text_cols] = df[text_cols].replace(NON_ANSWERS, np.nan)
    print(f"[{year}] non-answers converted to NaN: {df[text_cols].isna().sum().sum() - before:,}")
 
    # Experience text -> numbers
    for col in (cfg.get("years_cols", []) if convert_years else []):
        if col in df:
            unknown = df[col].notna() & df[col].map(parse_years).isna()
            df[col] = df[col].map(parse_years)
            print(f"[{year}] {col}: converted to years (unparsed values: {unknown.sum()})")
 
    # Standard columns, same names every year
    df = df.copy()                      # tidy memory after many column edits
    df.insert(0, "year", year)
    df.insert(1, "uid", f"{year}_" + df[id_col].astype(str))
    df["salary_usd"] = pd.to_numeric(df[salary_col], errors="coerce")
    lost = (df[salary_col].notna() & df["salary_usd"].isna()).sum()
    if lost:
        print(f"[{year}] WARNING: {lost:,} salary values aren't plain numbers "
              f"(e.g. ranges or text) and became NaN. Check {salary_col}!")
    df["has_salary"] = df["salary_usd"].notna()
 
    print(f"[{year}] rows: {len(df):,} | with salary: {df['has_salary'].sum():,} "
          f"({df['has_salary'].mean():.0%})")
 
    if drop_no_salary:
        df = df[df["has_salary"]].drop(columns="has_salary").reset_index(drop=True)
        print(f"[{year}] dropped rows with no salary -> {len(df):,} rows left")
    return df
