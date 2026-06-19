-- =====================================================
-- DASHBOARD SUMMARY (MAIN KPI CARDS)
-- =====================================================

CREATE MATERIALIZED VIEW mv_dashboard_summary AS
SELECT
    (SELECT COUNT(*) FROM subjects) AS total_subjects,
    (SELECT COUNT(*) FROM fingerprints) AS total_fingerprints,

    (SELECT COUNT(DISTINCT COALESCE(NULLIF(country, ''), 'Unknown')) FROM subjects) AS total_countries,
    (SELECT COUNT(DISTINCT COALESCE(NULLIF(city, ''), 'Unknown')) FROM subjects) AS total_cities,

    (SELECT COUNT(*) FROM subjects WHERE age IS NOT NULL) AS total_with_age;


-- =====================================================
-- GENDER DISTRIBUTION
-- =====================================================

CREATE MATERIALIZED VIEW mv_gender_stats AS
SELECT
    COALESCE(NULLIF(sex, ''), 'Unknown') AS gender,
    COUNT(*) AS count
FROM fingerprints
GROUP BY COALESCE(NULLIF(sex, ''), 'Unknown');


-- =====================================================
-- FINGER TYPE DISTRIBUTION
-- =====================================================

CREATE MATERIALIZED VIEW mv_finger_stats AS
SELECT
    finger,
    COUNT(*) AS count
FROM fingerprints
GROUP BY finger;


-- =====================================================
-- HAND DISTRIBUTION
-- =====================================================

CREATE MATERIALIZED VIEW mv_hand_stats AS
SELECT
    hand,
    COUNT(*) AS count
FROM fingerprints
GROUP BY hand;


-- =====================================================
-- COUNTRY STATS
-- =====================================================

CREATE MATERIALIZED VIEW mv_country_stats AS
SELECT
    COALESCE(NULLIF(country, ''), 'Unknown') AS country,
    COUNT(*) AS count
FROM subjects
GROUP BY COALESCE(NULLIF(country, ''), 'Unknown');


-- =====================================================
-- CITY STATS
-- =====================================================

CREATE MATERIALIZED VIEW mv_city_stats AS
SELECT
    COALESCE(NULLIF(city, ''), 'Unknown') AS city,
    COUNT(*) AS count
FROM subjects
GROUP BY COALESCE(NULLIF(city, ''), 'Unknown');


-- =====================================================
-- AGE DISTRIBUTION (NEW)
-- =====================================================

CREATE MATERIALIZED VIEW mv_age_stats AS
SELECT
    CASE
        WHEN age IS NULL THEN 'Unknown'
        WHEN age < 18 THEN 'Under 18'
        WHEN age BETWEEN 18 AND 30 THEN '18-30'
        WHEN age BETWEEN 31 AND 50 THEN '31-50'
        ELSE '50+'
        END AS age_group,
    COUNT(*) AS count
FROM subjects
GROUP BY
    CASE
    WHEN age IS NULL THEN 'Unknown'
    WHEN age < 18 THEN 'Under 18'
    WHEN age BETWEEN 18 AND 30 THEN '18-30'
    WHEN age BETWEEN 31 AND 50 THEN '31-50'
    ELSE '50+'
END;


-- =====================================================
-- COUNTRY + GENDER (STACKED CHART)
-- =====================================================

CREATE MATERIALIZED VIEW mv_country_gender_stats AS
SELECT
    COALESCE(NULLIF(s.country, ''), 'Unknown') AS country,
    COALESCE(NULLIF(f.sex, ''), 'Unknown') AS gender,
    COUNT(*) AS count
FROM fingerprints f
    JOIN subjects s
ON s.external_id = f.subject_external_id
GROUP BY
    COALESCE(NULLIF(s.country, ''), 'Unknown'),
    COALESCE(NULLIF(f.sex, ''), 'Unknown');


-- =====================================================
-- CITY + GENDER (STACKED CHART)
-- =====================================================

CREATE MATERIALIZED VIEW mv_city_gender_stats AS
SELECT
    COALESCE(NULLIF(s.city, ''), 'Unknown') AS city,
    COALESCE(NULLIF(f.sex, ''), 'Unknown') AS gender,
    COUNT(*) AS count
FROM fingerprints f
    JOIN subjects s
ON s.external_id = f.subject_external_id
GROUP BY
    COALESCE(NULLIF(s.city, ''), 'Unknown'),
    COALESCE(NULLIF(f.sex, ''), 'Unknown');


-- =====================================================
-- AGE + GENDER (NEW STACKED CHART)
-- =====================================================

CREATE MATERIALIZED VIEW mv_age_gender_stats AS
SELECT
    CASE
        WHEN s.age IS NULL THEN 'Unknown'
        WHEN s.age < 18 THEN 'Under 18'
        WHEN s.age BETWEEN 18 AND 30 THEN '18-30'
        WHEN s.age BETWEEN 31 AND 50 THEN '31-50'
        ELSE '50+'
        END AS age_group,

    COALESCE(NULLIF(f.sex, ''), 'Unknown') AS gender,

    COUNT(*) AS count
FROM fingerprints f
    JOIN subjects s
ON s.external_id = f.subject_external_id
GROUP BY
    CASE
    WHEN s.age IS NULL THEN 'Unknown'
    WHEN s.age < 18 THEN 'Under 18'
    WHEN s.age BETWEEN 18 AND 30 THEN '18-30'
    WHEN s.age BETWEEN 31 AND 50 THEN '31-50'
    ELSE '50+'
END,
    COALESCE(NULLIF(f.sex, ''), 'Unknown');


-- =====================================================
-- ADMIN: USER SUMMARY
-- =====================================================

CREATE MATERIALIZED VIEW mv_user_summary AS
SELECT
    COUNT(*) AS total_users,
    COUNT(*) FILTER (WHERE is_active = TRUE) AS active_users,
    COUNT(*) FILTER (WHERE is_active = FALSE) AS inactive_users,
    COUNT(*) FILTER (WHERE role = 'admin') AS admin_users,
    COUNT(*) FILTER (WHERE role = 'user') AS normal_users
FROM users;


-- =====================================================
-- ADMIN: USER ROLE DISTRIBUTION
-- =====================================================

CREATE MATERIALIZED VIEW mv_user_roles AS
SELECT
    role,
    COUNT(*) AS count
FROM users
GROUP BY role;


-- =====================================================
-- USER REGISTRATION OVER TIME (30 DAYS)
-- =====================================================

CREATE MATERIALIZED VIEW mv_user_registrations_30d AS
SELECT
    DATE(created_at) AS date,
    COUNT(*) AS count
FROM users
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date;


-- =====================================================
-- INDEXES (REQUIRED FOR CONCURRENT REFRESH)
-- =====================================================

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_gender_stats
    ON mv_gender_stats(gender);

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_finger_stats
    ON mv_finger_stats(finger);

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_hand_stats
    ON mv_hand_stats(hand);

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_user_roles
    ON mv_user_roles(role);

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_age_stats
    ON mv_age_stats(age_group);