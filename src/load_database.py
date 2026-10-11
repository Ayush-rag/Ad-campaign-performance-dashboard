"""Step 3 - Load the clean data into a SQL database.

Uses SQLite (built into Python, nothing to install). The clean CSV is
split into a campaigns table and a daily performance table.
"""
import sqlite3

import pandas as pd

from config import CLEAN_CSV, DB_PATH, SCHEMA_SQL


def main():
    df = pd.read_csv(CLEAN_CSV)
    campaigns = (df[["campaign_id", "campaign_name", "platform", "objective"]]
                 .drop_duplicates().sort_values("campaign_id"))
    performance = df[["date", "campaign_id", "age_group", "device", "impressions",
                      "clicks", "spend", "conversions", "revenue"]]

    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA_SQL.read_text())
        campaigns.to_sql("campaigns", conn, if_exists="append", index=False)
        performance.to_sql("ad_performance", conn, if_exists="append", index=False)
        n_perf = conn.execute("SELECT COUNT(*) FROM ad_performance").fetchone()[0]

    print(f"[3/5] Loaded SQLite database: {len(campaigns)} campaigns, {n_perf:,} performance rows")


if __name__ == "__main__":
    main()
