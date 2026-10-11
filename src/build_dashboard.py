"""Step 5 - Build the interactive HTML dashboard.

Aggregates the database to month x campaign x age group x device, embeds
that small dataset in a single HTML page together with Plotly.js, and
writes docs/index.html. The page works offline and can be hosted for free
with GitHub Pages. Filters (platform, months) recalculate every chart in
the browser, like slicers in Power BI.
"""
import json
import os
import re
import sqlite3

import plotly

from config import DASHBOARD_HTML, DB_PATH, OUTPUT_DIR, PLATFORMS, TARGET_ROAS

TEMPLATE = os.path.join(os.path.dirname(__file__), "dashboard_template.html")
AGES = ["18-24", "25-34", "35-44", "45-54", "55+"]
DEVICES = ["Mobile", "Desktop", "Tablet"]

QUERY = """
SELECT strftime('%Y-%m', date) AS month, campaign_id, age_group, device,
       SUM(impressions), SUM(clicks), ROUND(SUM(spend), 2),
       SUM(conversions), ROUND(SUM(revenue), 2)
FROM ad_performance
GROUP BY month, campaign_id, age_group, device
ORDER BY month, campaign_id
"""


def dashboard_data() -> dict:
    with sqlite3.connect(DB_PATH) as conn:
        campaigns = conn.execute(
            "SELECT campaign_id, campaign_name, platform FROM campaigns ORDER BY campaign_id").fetchall()
        rows = conn.execute(QUERY).fetchall()

    months = sorted({r[0] for r in rows})
    camp_index = {cid: i for i, (cid, _, _) in enumerate(campaigns)}
    compact = [[months.index(m), camp_index[c], AGES.index(a), DEVICES.index(d), *vals]
               for m, c, a, d, *vals in rows]

    return {
        "months": months,
        "platforms": PLATFORMS,
        "ages": AGES,
        "devices": DEVICES,
        "campaigns": [{"id": cid, "name": name, "platform": plat} for cid, name, plat in campaigns],
        "rows": compact,
    }


def insights_html() -> str:
    md = (OUTPUT_DIR / "insights.md").read_text(encoding="utf-8")
    items = re.findall(r"^\d+\.\s+(.*)$", md, flags=re.MULTILINE)
    return "".join(f"<li>{re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)}</li>" for s in items)


def main():
    plotly_js = open(os.path.join(os.path.dirname(plotly.__file__), "package_data", "plotly.min.js"),
                     encoding="utf-8").read()
    html = open(TEMPLATE, encoding="utf-8").read()
    html = (html.replace("__DATA__", json.dumps(dashboard_data(), separators=(",", ":")))
                .replace("__TARGET_ROAS__", str(TARGET_ROAS))
                .replace("__INSIGHTS__", insights_html())
                .replace("__PLOTLY_JS__", plotly_js))   # last, so its text is never searched

    DASHBOARD_HTML.parent.mkdir(exist_ok=True)
    DASHBOARD_HTML.write_text(html, encoding="utf-8")
    print(f"[5/5] Built interactive dashboard -> docs/index.html")


if __name__ == "__main__":
    main()
