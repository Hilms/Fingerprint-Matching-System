from fastapi import HTTPException

from app.security.auth import hash_password, verify_password

class UserService:

    def __init__(self, database):
        self.db = database

    # CREATE ADMIN
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
                "role" : data["role"]
            }
        )

    # CREATE USER
    async def create_user(
        self,
        data
    ):
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
                "username": data.username,
                "email": data.email,
                "first_name": data.first_name,
                "last_name": data.last_name,
                "password_hash": password_hash
            }
        )


    # GET USER
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

        if not user:
            return None

        return dict(user)

    # GET USER
    async def get_user_with_password(
        self,
        username: str
    ):

        # used internally for auth/login

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

        if not user:
            return None

        return dict(user)

    # SEARCH
    async def search_user(
        self,
        query: str
    ):

        search_query = """
            SELECT
                *
            FROM users
            WHERE
                first_name ILIKE :query
                OR last_name ILIKE :query
                OR username ILIKE :query
        """

        users = await self.db.fetch_all(
            query=search_query,
            values={
                "query": f"%{query}%"
            }
        )

        return [
            dict(user)
            for user in users
        ]

    # DELETE
    async def delete_user(
        self,
        username: str
    ):

        existing = await self.get_user(username)

        if not existing:

            raise HTTPException(
                status_code=404,
                detail="user not found"
            )

        query = """
            DELETE FROM users
            WHERE username = :username
        """

        await self.db.execute(
            query=query,
            values={
                "username": username
            }
        )

        return {
            "message": f"{username} deleted"
        }

    # UPDATE
    async def update_user(
        self,
        username: str,
        data: dict
    ):

        existing = await self.get_user(username)

        if not existing:

            raise HTTPException(
                status_code=404,
                detail="user not found"
            )

        # remove fields that were not sent

        update_data = {
            key: value
            for key, value in data.items()
            if value is not None
        }

        # nothing to update

        if not update_data:

            raise HTTPException(
                status_code=400,
                detail="no fields to update"
            )

        # build dynamic query

        fields = []

        for key in update_data.keys():
            fields.append(f"{key} = :{key}")

        query = f"""
            UPDATE users
            SET {", ".join(fields)}
            WHERE username = :username
        """

        # add username to values

        update_data["username"] = username

        await self.db.execute(
            query=query,
            values=update_data
        )

        return {
            "message": f"{username} updated"
        }

    # UPDATE
    async def update_password(
        self,
        username: str,
        current_password: str,
        new_password: str
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

        if not user:

            raise HTTPException(
                status_code=404,
                detail="user not found"
            )

        user = dict(user)

        # verify current password

        valid_password = verify_password(
            current_password,
            user["password_hash"]
        )

        if not valid_password:

            raise HTTPException(
                status_code=401,
                detail="invalid password"
            )

        # hash new password

        new_password_hash = hash_password(
            new_password
        )

        update_query = """
            UPDATE users
            SET password_hash = :password_hash
            WHERE username = :username
        """

        await self.db.execute(
            query=update_query,
            values={
                "username": username,
                "password_hash": new_password_hash
            }
        )

        return {
            "message": "password updated"
        }


    async def admin_reset_password(
        self,
        username: str,
        new_password: str
    ):

        existing = await self.get_user(
            username
        )

        if not existing:

            raise HTTPException(
                status_code=404,
                detail="user not found"
            )

        new_password_hash = hash_password(
            new_password
        )

        query = """
            UPDATE users
            SET password_hash = :password_hash
            WHERE username = :username
        """

        await self.db.execute(
            query=query,
            values={
                "username": username,
                "password_hash": new_password_hash
            }
        )

        return {
            "message": f"{username} password reset"
        }