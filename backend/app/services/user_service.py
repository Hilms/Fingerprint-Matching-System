fake_users = {
    "admin": {
        "username": "admin",
        "role": "admin"
    },
    "max": {
        "username": "max",
        "role": "user"
    }
}


class UserService:

    def get_user(self, username: str):

        return fake_users.get(username)


    def search_user(self, query: str):

        results = []

        for user in fake_users.values():

            if query.lower() in user["username"].lower():
                results.append(user)

        return results


    def delete_user(self, username: str):

        if username not in fake_users:
            return {
                "error": "User not found"
            }

        del fake_users[username]

        return {
            "message": f"{username} deleted"
        }


    def update_user(self, username: str):

        if username not in fake_users:
            return {
                "error": "User not found"
            }

        # placeholder for future DB updates
        return {
            "message": f"{username} updated"
        }