-- ============================================================
-- KPI queries. Each query starts with "-- name: <query_name>"
-- so the Python script can run them one by one and save the
-- results.
--
-- KPI definitions
--   CTR  (click-through rate)  = clicks / impressions
--   CPC  (cost per click)      = spend / clicks
--   CVR  (conversion rate)     = conversions / clicks
--   CPA  (cost per acquisition)= spend / conversions
--   ROAS (return on ad spend)  = revenue / spend
-- NULLIF(x, 0) avoids divide-by-zero errors.
-- ============================================================


-- name: overall_kpis
-- Headline numbers for the whole 6 months
SELECT
    SUM(impressions)                                             AS impressions,
    SUM(clicks)                                                  AS clicks,
    ROUND(SUM(spend), 2)                                         AS spend,
    SUM(conversions)                                             AS conversions,
    ROUND(SUM(revenue), 2)                                       AS revenue,
    ROUND(100.0 * SUM(clicks) / NULLIF(SUM(impressions), 0), 2)  AS ctr_pct,
    ROUND(SUM(spend) / NULLIF(SUM(clicks), 0), 2)                AS cpc,
    ROUND(100.0 * SUM(conversions) / NULLIF(SUM(clicks), 0), 2)  AS cvr_pct,
    ROUND(SUM(spend) / NULLIF(SUM(conversions), 0), 2)           AS cpa,
    ROUND(SUM(revenue) / NULLIF(SUM(spend), 0), 2)               AS roas
FROM ad_performance;


-- name: platform_kpis
-- Which platform gives the best return, and is budget going to the right place?
SELECT
    c.platform,
    ROUND(SUM(p.spend), 2)                                           AS spend,
    ROUND(SUM(p.revenue), 2)                                         AS revenue,
    SUM(p.conversions)                                               AS conversions,
    ROUND(100.0 * SUM(p.clicks) / NULLIF(SUM(p.impressions), 0), 2)  AS ctr_pct,
    ROUND(SUM(p.spend) / NULLIF(SUM(p.clicks), 0), 2)                AS cpc,
    ROUND(100.0 * SUM(p.conversions) / NULLIF(SUM(p.clicks), 0), 2)  AS cvr_pct,
    ROUND(SUM(p.spend) / NULLIF(SUM(p.conversions), 0), 2)           AS cpa,
    ROUND(SUM(p.revenue) / NULLIF(SUM(p.spend), 0), 2)               AS roas,
    ROUND(100.0 * SUM(p.spend)   / SUM(SUM(p.spend))   OVER (), 1)   AS spend_share_pct,
    ROUND(100.0 * SUM(p.revenue) / SUM(SUM(p.revenue)) OVER (), 1)   AS revenue_share_pct
FROM ad_performance p
JOIN campaigns c ON c.campaign_id = p.campaign_id
GROUP BY c.platform
ORDER BY roas DESC;


-- name: campaign_kpis
-- Every campaign ranked by ROAS
SELECT
    c.campaign_id,
    c.platform,
    c.campaign_name,
    c.objective,
    ROUND(SUM(p.spend), 2)                                           AS spend,
    ROUND(SUM(p.revenue), 2)                                         AS revenue,
    SUM(p.conversions)                                               AS conversions,
    ROUND(100.0 * SUM(p.clicks) / NULLIF(SUM(p.impressions), 0), 2)  AS ctr_pct,
    ROUND(SUM(p.spend) / NULLIF(SUM(p.clicks), 0), 2)                AS cpc,
    ROUND(SUM(p.spend) / NULLIF(SUM(p.conversions), 0), 2)           AS cpa,
    ROUND(SUM(p.revenue) / NULLIF(SUM(p.spend), 0), 2)               AS roas,
    RANK() OVER (ORDER BY SUM(p.revenue) / SUM(p.spend) DESC)        AS roas_rank
FROM ad_performance p
JOIN campaigns c ON c.campaign_id = p.campaign_id
GROUP BY c.campaign_id, c.platform, c.campaign_name, c.objective
ORDER BY roas DESC;


-- name: budget_wasters
-- Campaigns that return less than they cost (ROAS below 1)
SELECT
    c.platform,
    c.campaign_name,
    ROUND(SUM(p.spend), 2)                              AS spend,
    ROUND(SUM(p.revenue), 2)                            AS revenue,
    ROUND(SUM(p.revenue) - SUM(p.spend), 2)             AS net_return,
    ROUND(SUM(p.revenue) / NULLIF(SUM(p.spend), 0), 2)  AS roas
FROM ad_performance p
JOIN campaigns c ON c.campaign_id = p.campaign_id
GROUP BY c.platform, c.campaign_name
HAVING SUM(p.revenue) < SUM(p.spend)
ORDER BY net_return;


-- name: monthly_platform_trend
-- Month-by-month performance for each platform
SELECT
    strftime('%Y-%m', p.date)                                         AS month,
    c.platform,
    ROUND(SUM(p.spend), 2)                                            AS spend,
    ROUND(SUM(p.revenue), 2)                                          AS revenue,
    SUM(p.conversions)                                                AS conversions,
    ROUND(SUM(p.revenue) / NULLIF(SUM(p.spend), 0), 2)                AS roas
FROM ad_performance p
JOIN campaigns c ON c.campaign_id = p.campaign_id
GROUP BY month, c.platform
ORDER BY month, c.platform;


-- name: creative_fatigue
-- Monthly CTR per campaign and its change versus January.
-- A steady fall means people are tired of seeing the same ad.
WITH monthly AS (
    SELECT
        c.campaign_id,
        c.platform,
        c.campaign_name,
        strftime('%Y-%m', p.date)                                    AS month,
        100.0 * SUM(p.clicks) / NULLIF(SUM(p.impressions), 0)        AS ctr_pct
    FROM ad_performance p
    JOIN campaigns c ON c.campaign_id = p.campaign_id
    GROUP BY c.campaign_id, c.platform, c.campaign_name, month
)
SELECT
    campaign_id,
    platform,
    campaign_name,
    month,
    ROUND(ctr_pct, 3)                                                AS ctr_pct,
    ROUND(100.0 * (ctr_pct - FIRST_VALUE(ctr_pct) OVER w)
          / FIRST_VALUE(ctr_pct) OVER w, 1)                          AS ctr_change_vs_jan_pct
FROM monthly
WINDOW w AS (PARTITION BY campaign_id ORDER BY month)
ORDER BY campaign_id, month;


-- name: age_group_kpis
-- Which age group converts best and cheapest?
SELECT
    age_group,
    ROUND(SUM(spend), 2)                                          AS spend,
    ROUND(SUM(revenue), 2)                                        AS revenue,
    SUM(conversions)                                              AS conversions,
    ROUND(100.0 * SUM(conversions) / NULLIF(SUM(clicks), 0), 2)   AS cvr_pct,
    ROUND(SUM(spend) / NULLIF(SUM(conversions), 0), 2)            AS cpa,
    ROUND(SUM(revenue) / NULLIF(SUM(spend), 0), 2)                AS roas
FROM ad_performance
GROUP BY age_group
ORDER BY age_group;


-- name: device_kpis
-- Do people buy on mobile or desktop?
SELECT
    device,
    ROUND(SUM(spend), 2)                                          AS spend,
    ROUND(SUM(revenue), 2)                                        AS revenue,
    SUM(clicks)                                                   AS clicks,
    SUM(conversions)                                              AS conversions,
    ROUND(100.0 * SUM(clicks) / NULLIF(SUM(impressions), 0), 2)   AS ctr_pct,
    ROUND(100.0 * SUM(conversions) / NULLIF(SUM(clicks), 0), 2)   AS cvr_pct,
    ROUND(SUM(spend) / NULLIF(SUM(conversions), 0), 2)            AS cpa,
    ROUND(SUM(revenue) / NULLIF(SUM(spend), 0), 2)                AS roas
FROM ad_performance
GROUP BY device
ORDER BY spend DESC;
