"""Step 2 - Clean the raw export.

Each fix is logged with how many rows it touched, so the cleaning is
transparent and easy to explain in an interview.
"""
import pandas as pd

from config import CLEAN_CSV, OUTPUT_DIR, PLATFORMS, RAW_CSV

COLUMN_NAMES = {
    "Date": "date",
    "Platform": "platform",
    "Campaign ID": "campaign_id",
    "Campaign Name": "campaign_name",
    "Objective": "objective",
    "Age Group": "age_group",
    "Device": "device",
    "Impressions": "impressions",
    "Clicks": "clicks",
    "Amount Spent (INR)": "spend",
    "Conversions": "conversions",
    "Revenue (INR)": "revenue",
}

# Every spelling seen in the export -> one standard name
PLATFORM_MAP = {
    "google ads": "Google Ads", "google": "Google Ads",
    "meta ads": "Meta Ads", "meta": "Meta Ads", "facebook ads": "Meta Ads",
    "linkedin ads": "LinkedIn Ads", "linkedin": "LinkedIn Ads",
    "microsoft ads": "Microsoft Ads", "bing ads": "Microsoft Ads",
    "tiktok ads": "TikTok Ads", "tiktok": "TikTok Ads",
}


def clean(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    log = []
    df = raw.rename(columns=COLUMN_NAMES)
    log.append(("Rows in raw export", len(df)))

    # 1. Standardise platform names
    original = df["platform"].copy()
    df["platform"] = df["platform"].str.strip().str.lower().map(PLATFORM_MAP)
    assert df["platform"].isin(PLATFORMS).all(), "Unknown platform name found"
    log.append(("Platform names standardised", int((original != df["platform"]).sum())))

    # 2. Convert spend stored as text ("₹1,234.50") to numbers
    is_text = df["spend"].astype(str).str.contains("₹")
    df["spend"] = pd.to_numeric(
        df["spend"].astype(str).str.replace("₹", "", regex=False).str.replace(",", "", regex=False)
    )
    log.append(("Spend values converted from text", int(is_text.sum())))

    # 3. Blank revenue on rows with zero conversions means ₹0
    blank_rev = df["revenue"].isna() & (df["conversions"] == 0)
    df.loc[blank_rev, "revenue"] = 0
    df["revenue"] = pd.to_numeric(df["revenue"])
    log.append(("Blank revenue filled with 0 (no conversions)", int(blank_rev.sum())))

    # 4. Remove exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    log.append(("Duplicate rows removed", before - len(df)))

    # 5. Remove impossible rows
    bad_clicks = df["clicks"] > df["impressions"]
    log.append(("Rows removed: clicks > impressions", int(bad_clicks.sum())))
    df = df[~bad_clicks]

    negative = df["spend"] < 0
    log.append(("Rows removed: negative spend (refund adjustments)", int(negative.sum())))
    df = df[~negative]

    # 6. Correct data types and sort
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df = df.sort_values(["date", "campaign_id", "age_group", "device"]).reset_index(drop=True)
    log.append(("Rows in clean dataset", len(df)))

    return df, pd.DataFrame(log, columns=["step", "rows"])


def main():
    raw = pd.read_csv(RAW_CSV)
    df, log = clean(raw)
    CLEAN_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    df.to_csv(CLEAN_CSV, index=False)
    log.to_csv(OUTPUT_DIR / "cleaning_log.csv", index=False)

    print("[2/5] Cleaned data:")
    for step, rows in log.itertuples(index=False):
        print(f"      {step:<52} {rows:>7,}")


if __name__ == "__main__":
    main()
