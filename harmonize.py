"""Drop the columns the group cut and rename the rest to canonical names, so
every year's file has the same columns, in the same order, before merging.
 
Based on SO_Survey_Schema_Harmonization_2011-2026_2.xlsx (red = dropped,
yellow = undecided, kept for now). This file does NOT read the spreadsheet:
edit the settings below instead.
 
  KEEP          canonical columns to keep, in the order every file will use
  RENAME        per year, only the raw names that differ from the canonical name
  DROP_IN_YEAR  per year, canonical columns to drop in that year only
 
How a year is processed:
  1. Columns are renamed using RENAME[year].
  2. A column is kept if its name is in KEEP, or if it is an extra split
     column named '<name in KEEP>__<original>' (e.g. DevType__WebDeveloperType).
  3. Anything in DROP_IN_YEAR[year] is removed.
  4. Everything else is dropped. Columns come out in KEEP order.
 
Safety checks (printed or raised every run):
  - two columns end up with the same name             -> error
  - a RENAME source isn't in the file (typo?)         -> warning
  - a RENAME target isn't kept, so it would vanish    -> warning
  - columns kept WITHOUT a rename (raw name already
    matched KEEP) are listed, so a same-named column
    with a different meaning can't slip in unnoticed
 
Corrections to the spreadsheet already applied:
  - YearsCodingProf (2018) / YearsCodePro (2019-21) -> YearsCodePro, not YearsCode
  - 2017 Salary -> ConvertedCompYearly (it is already in USD)
  - 2018 SalaryType -> CompFreq (pay period, not the salary)
 
Usage (after clean_survey):
    from harmonize import harmonize
    h17 = harmonize(clean17, 2017)
"""
 
# Columns added by clean_survey(): always kept, always first
ADDED_COLS = ["year", "uid", "salary_usd", "has_salary", "n_answered"]
 
# ---------------------------------------------------------------------------
# 1. KEEP: canonical columns to keep (non-red rows), in output order
# ---------------------------------------------------------------------------
KEEP = [
    # Meta
    "ResponseId", "MainBranch",
    # Compensation
    "ConvertedCompYearly", "CompTotal", "CompFreq", "Currency",
    # Demographics
    "Country", "Age",
    # Education
    "EdLevel", "LearnCode",
    # Experience
    "YearsCode", "YearsCodePro", "WorkExp",
    # Employment
    "Employment", "DevType", "OrgSize", "Industry", "RemoteWork", "Hobbyist",
    # Satisfaction
    "JobSat",
    # Technology
    "LanguageHaveWorkedWith", "LanguageWantToWorkWith",
    "DatabaseHaveWorkedWith", "DatabaseWantToWorkWith",
    "PlatformHaveWorkedWith", "PlatformWantToWorkWith",
    "WebframeHaveWorkedWith", "WebframeWantToWorkWith",
    "DevEnvsHaveWorkedWith", "DevEnvsWantToWorkWith",
    "CollabToolsHaveWorkedWith", "CollabToolsWantToWorkWith",
    "MiscTechHaveWorkedWith", "MiscTechWantToWorkWith",      # yellow (undecided)
    "ToolsTechHaveWorkedWith", "ToolsTechWantToWorkWith",    # yellow (undecided)
    "OpSys",
    # Purchasing
    "PurchaseInfluence",
    # AI
    "AIFuture2018",
    "AISelect", "AISent", "AIAcc", "AIBen", "AIComplex", "AINext", "AIThreat",
    "AIDevHaveWorkedWith", "AIDevWantToWorkWith",
    "AIModelsHaveWorkedWith", "AIModelsWantToWorkWith", "AIAgents",
    # Kept in the sheet but named as GROUPS there, not single columns. Whoever adds
    # 2022+ lists the actual column names: AITool (by workflow stage),
    # AIEthics / AIChallenges, AIFrustration / AIExplain / AIHuman / AIOpen,
    # Tech gating & write-ins (2025).
]
 
# Yellow rows in the sheet: kept for now, still undecided
UNDECIDED = {"MiscTechHaveWorkedWith", "MiscTechWantToWorkWith",
             "ToolsTechHaveWorkedWith", "ToolsTechWantToWorkWith"}
 
# ---------------------------------------------------------------------------
# 2. RENAME: raw name -> canonical name, ONLY where they differ
#    '<Canonical>__<original>' = extra column when one year splits a question
# ---------------------------------------------------------------------------
RENAME = {
    2017: {
        "Respondent": "ResponseId",
        "Professional": "MainBranch",
        "Salary": "ConvertedCompYearly",          # already USD in 2017
        "FormalEducation": "EdLevel",
        "EducationTypes": "LearnCode",
        "SelfTaughtTypes": "LearnCode__SelfTaughtTypes",
        "YearsProgram": "YearsCode",
        "YearsCodedJob": "YearsCodePro",
        "YearsCodedJobPast": "YearsCodePro__YearsCodedJobPast",
        "EmploymentStatus": "Employment",
        "DeveloperType": "DevType",
        "WebDeveloperType": "DevType__WebDeveloperType",
        "MobileDeveloperType": "DevType__MobileDeveloperType",
        "NonDeveloperType": "DevType__NonDeveloperType",
        "CompanySize": "OrgSize",
        "HomeRemote": "RemoteWork",
        "ProgramHobby": "Hobbyist",
        "JobSatisfaction": "JobSat",
        "HaveWorkedLanguage": "LanguageHaveWorkedWith",
        "WantWorkLanguage": "LanguageWantToWorkWith",
        "HaveWorkedDatabase": "DatabaseHaveWorkedWith",
        "WantWorkDatabase": "DatabaseWantToWorkWith",
        "HaveWorkedPlatform": "PlatformHaveWorkedWith",
        "WantWorkPlatform": "PlatformWantToWorkWith",
        "HaveWorkedFramework": "WebframeHaveWorkedWith",
        "WantWorkFramework": "WebframeWantToWorkWith",
        "IDE": "DevEnvsHaveWorkedWith",
        # 2017 asks purchasing influence as 12 separate items
        "InfluenceInternet": "PurchaseInfluence__InfluenceInternet",
        "InfluenceWorkstation": "PurchaseInfluence__InfluenceWorkstation",
        "InfluenceHardware": "PurchaseInfluence__InfluenceHardware",
        "InfluenceServers": "PurchaseInfluence__InfluenceServers",
        "InfluenceTechStack": "PurchaseInfluence__InfluenceTechStack",
        "InfluenceDeptTech": "PurchaseInfluence__InfluenceDeptTech",
        "InfluenceVizTools": "PurchaseInfluence__InfluenceVizTools",
        "InfluenceDatabase": "PurchaseInfluence__InfluenceDatabase",
        "InfluenceCloud": "PurchaseInfluence__InfluenceCloud",
        "InfluenceConsultants": "PurchaseInfluence__InfluenceConsultants",
        "InfluenceRecruitment": "PurchaseInfluence__InfluenceRecruitment",
        "InfluenceCommunication": "PurchaseInfluence__InfluenceCommunication",
    },
    2018: {
        "Respondent": "ResponseId",
        "ConvertedSalary": "ConvertedCompYearly",
        "Salary": "CompTotal",                    # local currency in 2018
        "SalaryType": "CompFreq",
        "CurrencySymbol": "Currency__CurrencySymbol",
        "FormalEducation": "EdLevel",
        "EducationTypes": "LearnCode",
        "SelfTaughtTypes": "LearnCode__SelfTaughtTypes",
        "YearsCoding": "YearsCode",
        "YearsCodingProf": "YearsCodePro",
        "CompanySize": "OrgSize",
        "Hobby": "Hobbyist",
        "JobSatisfaction": "JobSat",
        "LanguageWorkedWith": "LanguageHaveWorkedWith",
        "LanguageDesireNextYear": "LanguageWantToWorkWith",
        "DatabaseWorkedWith": "DatabaseHaveWorkedWith",
        "DatabaseDesireNextYear": "DatabaseWantToWorkWith",
        "PlatformWorkedWith": "PlatformHaveWorkedWith",
        "PlatformDesireNextYear": "PlatformWantToWorkWith",
        "FrameworkWorkedWith": "WebframeHaveWorkedWith",
        "FrameworkDesireNextYear": "WebframeWantToWorkWith",
        "IDE": "DevEnvsHaveWorkedWith",
        "CommunicationTools": "CollabToolsHaveWorkedWith",
        "OperatingSystem": "OpSys",
        "AIDangerous": "AIFuture2018__AIDangerous",
        "AIInteresting": "AIFuture2018__AIInteresting",
        "AIResponsible": "AIFuture2018__AIResponsible",
        "AIFuture": "AIFuture2018__AIFuture",
    },
    2019: {
        "Respondent": "ResponseId",
        "ConvertedComp": "ConvertedCompYearly",
        "CurrencySymbol": "Currency",
        "CurrencyDesc": "Currency__CurrencyDesc",
        "EduOther": "LearnCode",
        "WorkRemote": "RemoteWork",
        "WorkLoc": "RemoteWork__WorkLoc",
        "LanguageWorkedWith": "LanguageHaveWorkedWith",
        "LanguageDesireNextYear": "LanguageWantToWorkWith",
        "DatabaseWorkedWith": "DatabaseHaveWorkedWith",
        "DatabaseDesireNextYear": "DatabaseWantToWorkWith",
        "PlatformWorkedWith": "PlatformHaveWorkedWith",
        "PlatformDesireNextYear": "PlatformWantToWorkWith",
        "WebFrameWorkedWith": "WebframeHaveWorkedWith",
        "WebFrameDesireNextYear": "WebframeWantToWorkWith",
        "MiscTechWorkedWith": "MiscTechHaveWorkedWith",
        "MiscTechDesireNextYear": "MiscTechWantToWorkWith",
        "DevEnviron": "DevEnvsHaveWorkedWith",
        "PurchaseWhat": "PurchaseInfluence",
    },
    2020: {
        "Respondent": "ResponseId",
        "ConvertedComp": "ConvertedCompYearly",
        "CurrencySymbol": "Currency",
        "CurrencyDesc": "Currency__CurrencyDesc",
        "LanguageWorkedWith": "LanguageHaveWorkedWith",
        "LanguageDesireNextYear": "LanguageWantToWorkWith",
        "DatabaseWorkedWith": "DatabaseHaveWorkedWith",
        "DatabaseDesireNextYear": "DatabaseWantToWorkWith",
        "PlatformWorkedWith": "PlatformHaveWorkedWith",
        "PlatformDesireNextYear": "PlatformWantToWorkWith",
        "WebframeWorkedWith": "WebframeHaveWorkedWith",
        "WebframeDesireNextYear": "WebframeWantToWorkWith",
        "MiscTechWorkedWith": "MiscTechHaveWorkedWith",
        "MiscTechDesireNextYear": "MiscTechWantToWorkWith",
        # In 2020, NEWCollabTools = Jira/Slack-type tools (NOT IDEs as in 2021-24)
        "NEWCollabToolsWorkedWith": "CollabToolsHaveWorkedWith",
        "NEWCollabToolsDesireNextYear": "CollabToolsWantToWorkWith",
        "PurchaseWhat": "PurchaseInfluence",
    },
    2021: {
        # In 2021-24, NEWCollabTools = the IDE question
        "NEWCollabToolsHaveWorkedWith": "DevEnvsHaveWorkedWith",
        "NEWCollabToolsWantToWorkWith": "DevEnvsWantToWorkWith",
    },
}
 
# ---------------------------------------------------------------------------
# 3. DROP_IN_YEAR: canonical columns to drop in ONE year only, e.g. when a
#    column has the right name but means something else that year.
#    Use the name AFTER renaming. Extra split columns ('X__...') go with 'X'.
# ---------------------------------------------------------------------------
DROP_IN_YEAR = {
    # 2017: ["Hobbyist"],   # example
}
 
 
def _base(name):
    """'DevType__WebDeveloperType' -> 'DevType'."""
    return name.split("__")[0]
 
 
def harmonize(df, year, verbose=True):
    """Return a COPY of df with only the kept columns, renamed, in KEEP order."""
    if year not in RENAME:
        raise KeyError(f"No RENAME entry for {year}. Add one (use {{}} if no names change).")
    renames = RENAME[year]
    keep_set = set(KEEP)
    drop_set = set(DROP_IN_YEAR.get(year, []))
 
    # Checks on the settings themselves
    missing_src = [r for r in renames if r not in df.columns]
    lost_targets = [t for t in renames.values() if _base(t) not in keep_set]
 
    out = df.rename(columns=renames)
    dupes = out.columns[out.columns.duplicated()].unique().tolist()
    if dupes:
        raise ValueError(f"[{year}] two columns would share a name: {dupes}. "
                         "Check RENAME: a raw column may already have that name.")
 
    def wanted(c):
        b = _base(c)
        return b in keep_set and b not in drop_set
 
    kept = [c for c in out.columns if c not in ADDED_COLS and wanted(c)]
    order = {name: i for i, name in enumerate(KEEP)}
    kept.sort(key=lambda c: (order[_base(c)], c != _base(c)))   # main column before its extras
    added = [c for c in ADDED_COLS if c in out.columns]
    result = out[added + kept]
 
    if verbose:
        dropped = len(df.columns) - len(added) - len(kept)
        print(f"[{year}] kept {len(kept)} columns, dropped {dropped}")
        as_is = [c for c in kept if c not in renames.values()]
        print(f"[{year}] kept as-is (raw name already canonical): {as_is}")
        und = [c for c in kept if _base(c) in UNDECIDED]
        if und:
            print(f"[{year}] yellow (undecided): {und}")
        if drop_set:
            print(f"[{year}] dropped by DROP_IN_YEAR: {sorted(drop_set)}")
        if missing_src:
            print(f"[{year}] WARNING: RENAME lists columns not in the file: {missing_src}")
        if lost_targets:
            print(f"[{year}] WARNING: renamed but not in KEEP, so dropped: {lost_targets}")
    return result
 
