-- ============================================================
-- Schema: one dimension table (campaigns) + one fact table
-- (daily performance), joined on campaign_id.
-- Written for SQLite; works in MySQL with the small changes
-- noted in the README.
-- ============================================================

DROP TABLE IF EXISTS ad_performance;
DROP TABLE IF EXISTS campaigns;

-- One row per campaign
CREATE TABLE campaigns (
    campaign_id    VARCHAR(10)  PRIMARY KEY,
    campaign_name  VARCHAR(100) NOT NULL,
    platform       VARCHAR(30)  NOT NULL,
    objective      VARCHAR(30)  NOT NULL
);

-- One row per campaign, per day, per age group, per device
CREATE TABLE ad_performance (
    id           INTEGER PRIMARY KEY,
    date         DATE        NOT NULL,
    campaign_id  VARCHAR(10) NOT NULL REFERENCES campaigns(campaign_id),
    age_group    VARCHAR(10) NOT NULL,
    device       VARCHAR(10) NOT NULL,
    impressions  INTEGER     NOT NULL,
    clicks       INTEGER     NOT NULL,
    spend        DECIMAL(12, 2) NOT NULL,
    conversions  INTEGER     NOT NULL,
    revenue      DECIMAL(12, 2) NOT NULL
);

CREATE INDEX idx_performance_date     ON ad_performance (date);
CREATE INDEX idx_performance_campaign ON ad_performance (campaign_id);
