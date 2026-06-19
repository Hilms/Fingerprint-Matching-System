CREATE OR REPLACE FUNCTION refresh_dashboard_views()
RETURNS void AS $$
BEGIN

    -- =========================
    -- CORE SUBJECT DASHBOARD
    -- =========================
    REFRESH MATERIALIZED VIEW mv_dashboard_summary;

    REFRESH MATERIALIZED VIEW mv_gender_stats;
    REFRESH MATERIALIZED VIEW mv_finger_stats;
    REFRESH MATERIALIZED VIEW mv_hand_stats;

    REFRESH MATERIALIZED VIEW mv_country_stats;
    REFRESH MATERIALIZED VIEW mv_city_stats;

    -- =========================
    -- AGE ANALYTICS (NEW)
    -- =========================
    REFRESH MATERIALIZED VIEW mv_age_stats;
    REFRESH MATERIALIZED VIEW mv_age_gender_stats;

    -- =========================
    -- STACKED GEO ANALYTICS
    -- =========================
    REFRESH MATERIALIZED VIEW mv_country_gender_stats;
    REFRESH MATERIALIZED VIEW mv_city_gender_stats;

    -- =========================
    -- USER ADMIN DASHBOARD
    -- =========================
    REFRESH MATERIALIZED VIEW mv_user_summary;
    REFRESH MATERIALIZED VIEW mv_user_roles;
    REFRESH MATERIALIZED VIEW mv_user_registrations_30d;

END;
$$ LANGUAGE plpgsql;