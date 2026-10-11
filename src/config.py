"""Shared settings for the whole project: file paths and business assumptions."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Data files
RAW_CSV = ROOT / "data" / "raw" / "ad_campaigns_raw.csv"
CLEAN_CSV = ROOT / "data" / "processed" / "ad_campaigns_clean.csv"
DB_PATH = ROOT / "data" / "ad_campaigns.db"

# SQL files
SCHEMA_SQL = ROOT / "sql" / "01_create_tables.sql"
KPI_SQL = ROOT / "sql" / "02_kpi_queries.sql"

# Outputs
OUTPUT_DIR = ROOT / "outputs"
EXCEL_REPORT = OUTPUT_DIR / "ad_kpi_report.xlsx"
DASHBOARD_HTML = ROOT / "docs" / "index.html"   # docs/ so GitHub Pages can host it
IMAGES_DIR = ROOT / "images"

# Business assumptions
SEED = 42                 # makes the generated data the same on every run
TARGET_ROAS = 2.0         # every campaign should return at least ₹2 per ₹1 spent
REALLOCATION_EFFICIENCY = 0.75  # moved budget assumed to earn 75% of the receiving
                                # campaign's current ROAS (diminishing returns)

PLATFORMS = ["Google Ads", "Meta Ads", "LinkedIn Ads", "Microsoft Ads", "TikTok Ads"]

# One fixed colour per platform (colour-blind safe, validated order)
PLATFORM_COLORS = {
    "Google Ads": "#2a78d6",
    "Meta Ads": "#eb6834",
    "LinkedIn Ads": "#1baf7a",
    "Microsoft Ads": "#eda100",
    "TikTok Ads": "#e87ba4",
}


def roas_action(roas: float) -> str:
    """Turn a ROAS number into a budget decision."""
    if roas >= 4:
        return "Scale"
    if roas >= TARGET_ROAS:
        return "Keep"
    if roas >= 1:
        return "Optimize"
    return "Cut"
