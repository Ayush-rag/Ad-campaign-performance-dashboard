"""Step 1 - Generate the raw ad export.

Real ad-account data is private, so this script SIMULATES 6 months
(Jan-Jun 2026) of daily performance for 11 campaigns on 5 platforms.
The numbers follow typical industry ranges for each platform
(e.g. search ads have high CTR, LinkedIn has expensive clicks but
high-value B2B customers, TikTok has cheap clicks but low conversion).

It also adds the messiness found in real exports - inconsistent
platform names, duplicate rows, spend saved as text, blanks and
invalid rows - so the cleaning step has real work to do.
"""
import numpy as np
import pandas as pd

from config import RAW_CSV, SEED

# id, platform, campaign name, objective, daily budget (₹), CTR, CPC (₹), conversion rate, avg order value (₹)
CAMPAIGNS = [
    ("C01", "Google Ads", "Search - Brand Keywords", "Conversions", 3000, 0.060, 22, 0.070, 2400),
    ("C02", "Google Ads", "Search - Generic Keywords", "Conversions", 5000, 0.035, 32, 0.035, 2200),
    ("C03", "Google Ads", "Display - Remarketing", "Conversions", 2000, 0.009, 9, 0.010, 2000),
    ("C04", "Meta Ads", "Prospecting - Video", "Traffic", 4500, 0.011, 11, 0.012, 1900),
    ("C05", "Meta Ads", "Retargeting - Carousel", "Conversions", 2500, 0.018, 14, 0.035, 2100),
    ("C06", "Meta Ads", "Lookalike - Broad Audience", "Conversions", 4000, 0.007, 16, 0.006, 1800),
    ("C07", "LinkedIn Ads", "Sponsored Content - B2B", "Lead Generation", 3500, 0.0055, 85, 0.025, 9500),
    ("C08", "LinkedIn Ads", "Message Ads - Decision Makers", "Lead Generation", 2000, 0.006, 110, 0.012, 8000),
    ("C09", "Microsoft Ads", "Search - Generic Keywords", "Conversions", 1500, 0.032, 20, 0.038, 2300),
    ("C10", "TikTok Ads", "In-Feed - Gen Z Awareness", "Awareness", 3000, 0.014, 5, 0.005, 1200),
    ("C11", "TikTok Ads", "Spark Ads - Creator Content", "Traffic", 1500, 0.019, 6, 0.012, 1400),
]
FATIGUE_CAMPAIGN = "C04"  # same video creative all 6 months -> CTR slowly drops

AGE_GROUPS = ["18-24", "25-34", "35-44", "45-54", "55+"]
AGE_CVR = [0.70, 1.30, 1.15, 0.90, 0.60]          # 25-44 buy the most
AGE_SHARE = {                                     # share of budget each age group gets
    "default": [0.20, 0.32, 0.25, 0.15, 0.08],
    "Meta Ads": [0.22, 0.30, 0.24, 0.15, 0.09],
    "LinkedIn Ads": [0.08, 0.38, 0.32, 0.17, 0.05],
    "TikTok Ads": [0.50, 0.32, 0.12, 0.04, 0.02],
}

DEVICES = ["Mobile", "Desktop", "Tablet"]
DEVICE_CVR = [0.85, 1.40, 1.00]   # people click on mobile but buy on desktop
DEVICE_CTR = [1.05, 0.90, 0.95]
DEVICE_SHARE = {
    "default": [0.62, 0.32, 0.06],
    "LinkedIn Ads": [0.40, 0.55, 0.05],
    "TikTok Ads": [0.92, 0.05, 0.03],
}

MONTH_BUDGET = {1: 0.90, 2: 0.95, 3: 1.15, 4: 1.00, 5: 1.05, 6: 1.00}  # March = Holi sale
MONTH_CVR = {3: 1.15}

# How a messy export might spell each platform
PLATFORM_VARIANTS = {
    "Google Ads": ["google ads", "Google", "GOOGLE ADS", " Google Ads "],
    "Meta Ads": ["Facebook Ads", "meta", "Meta Ads "],
    "LinkedIn Ads": ["Linkedin", "linkedin ads"],
    "Microsoft Ads": ["Bing Ads", "microsoft ads"],
    "TikTok Ads": ["Tiktok", "TikTok Ads "],
}


def simulate(rng: np.random.Generator) -> pd.DataFrame:
    dates = pd.date_range("2026-01-01", "2026-06-30", freq="D")
    n_days = len(dates)
    rows = []

    for day_index, date in enumerate(dates):
        weekend = date.dayofweek >= 5
        for cid, platform, name, objective, budget, ctr, cpc, cvr, aov in CAMPAIGNS:
            day_budget = budget * MONTH_BUDGET[date.month] * rng.lognormal(0, 0.12)
            day_cvr = cvr * MONTH_CVR.get(date.month, 1.0)
            day_ctr, day_cpc = ctr, cpc

            if platform == "LinkedIn Ads" and weekend:   # B2B audiences are offline at weekends
                day_budget *= 0.5
                day_cvr *= 0.8
            elif weekend:
                day_cvr *= 1.08

            if cid == FATIGUE_CAMPAIGN:                  # creative fatigue: CTR falls 40% over 6 months
                fatigue = 1 - 0.40 * day_index / (n_days - 1)
                day_ctr *= fatigue
                day_cpc /= fatigue ** 0.7

            age_share = AGE_SHARE.get(platform, AGE_SHARE["default"])
            device_share = DEVICE_SHARE.get(platform, DEVICE_SHARE["default"])

            for age, a_share, a_cvr in zip(AGE_GROUPS, age_share, AGE_CVR):
                for device, d_share, d_cvr, d_ctr in zip(DEVICES, device_share, DEVICE_CVR, DEVICE_CTR):
                    cell_budget = day_budget * a_share * d_share * rng.lognormal(0, 0.10)
                    cell_cpc = day_cpc * rng.lognormal(0, 0.08)
                    cell_ctr = min(day_ctr * d_ctr * rng.lognormal(0, 0.08), 0.5)

                    impressions = int(rng.poisson(cell_budget / cell_cpc / cell_ctr))
                    clicks = int(rng.binomial(impressions, cell_ctr))
                    spend = round(clicks * cell_cpc, 2)
                    conversions = int(rng.binomial(clicks, min(day_cvr * a_cvr * d_cvr, 1.0)))
                    revenue = round(conversions * aov * rng.lognormal(0, 0.20), 2) if conversions else 0.0

                    rows.append((date.strftime("%Y-%m-%d"), platform, cid, name, objective, age, device,
                                 impressions, clicks, spend, conversions, revenue))

    return pd.DataFrame(rows, columns=[
        "Date", "Platform", "Campaign ID", "Campaign Name", "Objective", "Age Group", "Device",
        "Impressions", "Clicks", "Amount Spent (INR)", "Conversions", "Revenue (INR)",
    ])


def make_messy(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    df["Amount Spent (INR)"] = df["Amount Spent (INR)"].astype(object)
    df["Revenue (INR)"] = df["Revenue (INR)"].astype(object)

    # 1. Inconsistent platform names on ~8% of rows
    idx = rng.choice(n, size=int(n * 0.08), replace=False)
    for i in idx:
        df.at[i, "Platform"] = rng.choice(PLATFORM_VARIANTS[df.at[i, "Platform"]])

    # 2. Spend exported as text like "₹1,234.50" on ~5% of rows
    idx = rng.choice(n, size=int(n * 0.05), replace=False)
    for i in idx:
        df.at[i, "Amount Spent (INR)"] = f"₹{float(df.at[i, 'Amount Spent (INR)']):,.2f}"

    # 3. Revenue left blank when there were no conversions (~40% of those rows)
    zero_conv = df.index[df["Conversions"] == 0].to_numpy()
    idx = rng.choice(zero_conv, size=int(len(zero_conv) * 0.40), replace=False)
    df.loc[idx, "Revenue (INR)"] = np.nan

    # 4. Tracking errors: clicks higher than impressions
    idx = rng.choice(n, size=25, replace=False)
    df.loc[idx, "Clicks"] = df.loc[idx, "Impressions"] + rng.integers(5, 50, size=25)

    # 5. Refund adjustments exported as negative spend
    idx = rng.choice(n, size=12, replace=False)
    df.loc[idx, "Amount Spent (INR)"] = -rng.uniform(50, 500, size=12).round(2)

    # 6. Duplicate rows from overlapping exports
    dupes = df.sample(n=180, random_state=SEED)
    df = pd.concat([df, dupes], ignore_index=True)

    return df.sample(frac=1, random_state=SEED).reset_index(drop=True)


def main():
    rng = np.random.default_rng(SEED)
    raw = make_messy(simulate(rng), rng)
    RAW_CSV.parent.mkdir(parents=True, exist_ok=True)
    raw.to_csv(RAW_CSV, index=False)
    print(f"[1/5] Generated raw export: {len(raw):,} rows -> {RAW_CSV.relative_to(RAW_CSV.parents[2])}")


if __name__ == "__main__":
    main()
