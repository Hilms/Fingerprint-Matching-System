from fastapi import HTTPException

from app.security.auth import hash_password, verify_password

class UserService:

    def __init__(self, database):
        self.db = database

    # =========================
    # CREATE
    # =========================

    async def create_admin(
        self,
        data: dict
    ):
        password_hash = hash_password(
            data["password"]
        )

        query = """
            INSERT INTO users (
                first_name,
                last_name,
                username,
                email,
                password_hash,
                role
            )
            VALUES (
                :first_name,
                :last_name,
                :username,
                :email,
                :password_hash,
                :role
            )
        """

        await self.db.execute(
            query=query,
            values={
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "username": data["username"],
                "email": data["email"],
                "password_hash": password_hash,
                "role": data["role"]
            }
        )

    async def create_user(
        self,
        data
    ):
        existing_user = await self.db.fetch_one(
            query="""
                SELECT username, email
                FROM users
                WHERE username = :username
                   OR email = :email
            """,
            values={
                "username": data.username,
                "email": data.email,
            }
        )

        if existing_user:

            if existing_user["username"] == data.username:
                return {
                    "success": False,
                    "message": f'Username "{data.username}" already exists'
                }

            if existing_user["email"] == data.email:
                return {
                    "success": False,
                    "message": f'Email "{data.email}" already exists'
                }

        password_hash = hash_password(
            data.password
        )

        query = """
            INSERT INTO users (
                first_name,
                last_name,
                username,
                email,
                password_hash
            )
            VALUES (
                :first_name,
                :last_name,
                :username,
                :email,
                :password_hash
            )
        """

        await self.db.execute(
            query=query,
            values={
                "first_name": data.first_name,
                "last_name": data.last_name,
                "username": data.username,
                "email": data.email,
                "password_hash": password_hash
            }
        )

        return {
            "success": True,
            "message": f'{data.username} successfully created'
        }

    # =========================
    # GET
    # =========================

    async def get_all_users(self):

        query = """
            SELECT
                id,
                first_name,
                last_name,
                username,
                email,
                role,
                is_active,
                created_at
            FROM users
            ORDER BY username
        """

        users = await self.db.fetch_all(query)

        return [dict(user) for user in users]

    async def get_user(
        self,
        username: str
    ):
        query = """
            SELECT
                id,
                first_name,
                last_name,
                username,
                email,
                role,
                is_active,
                created_at
            FROM users
            WHERE username = :username
        """

        user = await self.db.fetch_one(
            query=query,
            values={
                "username": username
            }
        )

        return dict(user) if user else None


    async def get_user_mail(
            self,
            email: str
        ):
            query = """
                SELECT
                    email
                FROM users
                WHERE email = :email
            """

            mail = await self.db.fetch_one(
                query=query,
                values={
                    "email": email
                }
            )

            return dict(mail) if mail else None


    async def get_user_with_password(
        self,
        username: str
    ):
        query = """
            SELECT *
            FROM users
            WHERE username = :username
        """

        user = await self.db.fetch_one(
            query=query,
            values={
                "username": username
            }
        )

        return dict(user) if user else None

    # =========================
    # SEARCH
    # =========================

    async def search_users(
        self,
        query: str
    ):
        sql = """
            SELECT
                id,
                first_name,
                last_name,
                username,
                email,
                role,
                is_active,
                created_at
            FROM users
            WHERE
                first_name ILIKE :query
                OR last_name ILIKE :query
                OR username ILIKE :query
                OR email ILIKE :query
                OR role ILIKE :query
        """

        users = await self.db.fetch_all(
            query=sql,
            values={
                "query": f"%{query}%"
            }
        )

        return [
            dict(user)
            for user in users
        ]

    # =========================
    # UPDATE
    # =========================

    async def update_user(
        self,
        username: str,
        data: dict
    ):
        existing = await self.get_user(
            username
        )

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="user not found"
            )

        update_data = {
            k: v
            for k, v in data.items()
            if v is not None
        }

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="nothing to update"
            )

        fields = [
            f"{key} = :{key}"
            for key in update_data.keys()
        ]

        sql = f"""
            UPDATE users
            SET {", ".join(fields)}
            WHERE username = :current_username
        """

        update_data["current_username"] = username

        await self.db.execute(
                query=sql,
                values=update_data
        )

        return {
            "success": True,
            "message": f"{username} successfully updated"
        }

    # =========================
    # PASSWORD
    # =========================

    async def update_password(
        self,
        username: str,
        current_password: str,
        new_password: str
    ):
        user = await self.get_user_with_password(
            username
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="user not found"
            )

        if not verify_password(
            current_password,
            user["password_hash"]
        ):
            raise HTTPException(
                status_code=401,
                detail="invalid password"
            )

        password_hash = hash_password(
            new_password
        )

        sql = """
            UPDATE users
            SET password_hash = :password_hash
            WHERE username = :username
        """

        await self.db.execute(
            query=sql,
            values={
                "username": username,
                "password_hash": password_hash
            }
        )

        return {
            "success": True,
            "message": "Password updated successfully"
        }

    async def admin_reset_password(
        self,
        username: str,
        new_password: str
    ):
        user = await self.get_user(
            username
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="user not found"
            )

        password_hash = hash_password(
            new_password
        )

        sql = """
            UPDATE users
            SET password_hash = :password_hash
            WHERE username = :username
        """

        await self.db.execute(
            query=sql,
            values={
                "username": username,
                "password_hash": password_hash
            }
        )

        return {
            "success": True,
            "message": f"Reset password successfully for {username}"
        }

    # =========================
    # DELETE
    # =========================

    async def delete_user(
        self,
        username: str
    ):
        user = await self.get_user(
            username
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="user not found"
            )

        if user["role"] == "admin":
            raise HTTPException(
                status_code=403,
                detail="admin users cannot be deleted"
            )

        sql = """
            DELETE FROM users
            WHERE username = :username
        """

        await self.db.execute(
            query=sql,
            values={
                "username": username
            }
        )

        return {
            "success": True,
            "message": f"{username} successfully deleted"
        }