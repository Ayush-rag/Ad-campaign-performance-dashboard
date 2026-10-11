# Rebuilding the Dashboard in Power BI

This guide recreates the dashboard in **Power BI Desktop** (free, Windows) using the clean dataset. It takes about 45-60 minutes.

## 1. Load the data

1. Open Power BI Desktop → **Get data → Text/CSV**.
2. Choose `data/processed/ad_campaigns_clean.csv` → **Transform Data**.
3. In Power Query, check the column types:
   - `date` → Date
   - `impressions`, `clicks`, `conversions` → Whole number
   - `spend`, `revenue` → Fixed decimal number
4. Rename the table to **Ads** → **Close & Apply**.

## 2. Add a Month column

In **Table view**, click **New column**:

```DAX
Month = FORMAT(Ads[date], "MMM YYYY")
Month Sort = YEAR(Ads[date]) * 100 + MONTH(Ads[date])
```

Select `Month` → **Sort by column → Month Sort**, so months show in calendar order.

## 3. Create the measures

Click **New measure** for each one:

```DAX
Total Spend = SUM(Ads[spend])

Total Revenue = SUM(Ads[revenue])

Total Conversions = SUM(Ads[conversions])

Total Clicks = SUM(Ads[clicks])

Total Impressions = SUM(Ads[impressions])

ROAS = DIVIDE([Total Revenue], [Total Spend])

CTR = DIVIDE([Total Clicks], [Total Impressions])

CPC = DIVIDE([Total Spend], [Total Clicks])

Conversion Rate = DIVIDE([Total Conversions], [Total Clicks])

CPA = DIVIDE([Total Spend], [Total Conversions])

Spend Share =
DIVIDE([Total Spend], CALCULATE([Total Spend], ALLSELECTED(Ads[platform])))

Revenue Share =
DIVIDE([Total Revenue], CALCULATE([Total Revenue], ALLSELECTED(Ads[platform])))

Target ROAS = 2

Budget Decision =
SWITCH(
    TRUE(),
    [ROAS] >= 4, "Scale",
    [ROAS] >= 2, "Keep",
    [ROAS] >= 1, "Optimize",
    "Cut"
)
```

**Formatting:** Set `CTR`, `Conversion Rate`, `Spend Share` and `Revenue Share` to **Percentage**. Set `ROAS` to a decimal number with 2 places. Set `Total Spend`, `Total Revenue`, `CPA` and `CPC` to **Currency → ₹ (English, India)**.

## 4. Build the page

| Position | Visual | Fields |
|---|---|---|
| Top row | **Slicer** (buttons) | `platform` |
| Top row | **Slicer** (between) | `date` |
| Row 2 | 6 × **Card** | Total Spend, Total Revenue, ROAS, Total Conversions, CPA, CTR |
| Row 3 left | **Clustered bar chart** | Y-axis: `platform` · X-axis: `ROAS` · add a constant line at 2 (Analytics pane) |
| Row 3 right | **Clustered column chart** | X-axis: `platform` · Y-axis: `Spend Share`, `Revenue Share` |
| Row 4 | **Line chart** | X-axis: `Month` · Y-axis: `ROAS` · Legend: `platform` |
| Row 5 | **Table** | `campaign_name`, `platform`, Total Spend, Total Revenue, ROAS, CPA, CTR, Budget Decision |
| Row 6 left | **Column chart** | X-axis: `age_group` · Y-axis: `CPA` |
| Row 6 right | **Column chart** | X-axis: `device` · Y-axis: `Conversion Rate` |

### Finishing touches
- **Table:** Sort by ROAS (descending). Under **Conditional formatting → Font colour → Rules** on `Budget Decision`, use green for Scale and red for Cut.
- **Consistent colours:** Give each platform the same colour in every visual: Google `#2A78D6`, Meta `#EB6834`, LinkedIn `#1BAF7A`, Microsoft `#EDA100`, TikTok `#E87BA4`.
- **Title:** Add a text box: *Ad Campaign Performance Dashboard · Jan-Jun 2026*.

## 5. Save and share

1. Save as `powerbi/ad_campaign_dashboard.pbix` and add it to the repo.
2. Take a screenshot and save it as `images/powerbi_dashboard.png`. Add it to the README.
3. Optional: Upload the `.pbix` to **NovyPro** (free) so recruiters can click through it without installing Power BI.

## Check your numbers

With no filters applied, your cards should show:

| Card | Value |
|---|---|
| Total Spend | ₹58,60,770 |
| Total Revenue | ₹1,86,75,993 |
| ROAS | 3.19 |
| Total Conversions | 7,943 |
| CPA | ₹738 |
| CTR | 1.23% |
