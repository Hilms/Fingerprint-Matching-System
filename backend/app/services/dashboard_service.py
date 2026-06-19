from fastapi import HTTPException

class DashboardService:

    def __init__(self, database):
        self.db = database

    # =====================================================
    # USER DASHBOARD
    # =====================================================

    async def get_dashboard_data(self):

        summary = await self.db.fetch_one("""
            SELECT * FROM mv_dashboard_summary
        """)

        gender = await self.db.fetch_all("""
            SELECT gender, count
            FROM mv_gender_stats
            ORDER BY count DESC
        """)

        fingers = await self.db.fetch_all("""
            SELECT finger, count
            FROM mv_finger_stats
            ORDER BY count DESC
        """)

        hands = await self.db.fetch_all("""
            SELECT hand, count
            FROM mv_hand_stats
            ORDER BY count DESC
        """)

        countries = await self.db.fetch_all("""
            SELECT country, count
            FROM mv_country_stats
            ORDER BY count DESC
            LIMIT 15
        """)

        cities = await self.db.fetch_all("""
            SELECT city, count
            FROM mv_city_stats
            ORDER BY count DESC
            LIMIT 20
        """)

        country_gender = await self.db.fetch_all("""
            SELECT country, gender, count
            FROM mv_country_gender_stats
        """)

        city_gender = await self.db.fetch_all("""
            SELECT city, gender, count
            FROM mv_city_gender_stats
        """)

        # =========================
        # NEW: AGE ANALYTICS
        # =========================

        age = await self.db.fetch_all("""
            SELECT age_group, count
            FROM mv_age_stats
            ORDER BY count DESC
        """)

        age_gender = await self.db.fetch_all("""
            SELECT age_group, gender, count
            FROM mv_age_gender_stats
        """)

        return {
            "summary": dict(summary) if summary else {},

            "gender": [dict(row) for row in gender],
            "fingers": [dict(row) for row in fingers],
            "hands": [dict(row) for row in hands],

            "countries": [dict(row) for row in countries],
            "cities": [dict(row) for row in cities],

            "country_gender": [dict(row) for row in country_gender],
            "city_gender": [dict(row) for row in city_gender],

            "age": [dict(row) for row in age],
            "age_gender": [dict(row) for row in age_gender]
        }

    # =====================================================
    # ADMIN DASHBOARD
    # =====================================================

    async def get_dashboard_admin_data(self):

        summary = await self.db.fetch_one("""
            SELECT * FROM mv_user_summary
        """)

        roles = await self.db.fetch_all("""
            SELECT role, count
            FROM mv_user_roles
            ORDER BY count DESC
        """)

        registrations = await self.db.fetch_all("""
            SELECT date, count
            FROM mv_user_registrations_30d
            ORDER BY date
        """)

        return {
            "summary": dict(summary) if summary else {},
            "roles": [dict(row) for row in roles],
            "registrations": [dict(row) for row in registrations]
        }