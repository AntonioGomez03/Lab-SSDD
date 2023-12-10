import json

class JsonManager:
    @staticmethod
    def load_users(filename: str) -> list:
        """Load the users from the given filename."""
        with open(filename, "r") as f:
            data = json.load(f)
        
        users = []
        for user in data["users"]:
            users.append({"username": user["username"], "password": user["password"]})
        
        return users

    @staticmethod
    def add_user(username: str, password: str, filename: str) -> None:
        """Add the given user to the given filename."""
        user_info = {
            "username": username,
            "password": password
        } 

        with open(filename, "r") as f:
            data = json.load(f)
        
        data["users"].append(user_info)

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def remove_user(username: str, password: str, filename: str) -> None:
        """Remove the given user from the given filename."""
        with open(filename, "r") as f:
            data = json.load(f)
        
        for user_info in data["users"]:
            if user_info["username"] == username and user_info["password"] == password:
                data["users"].remove(user_info)
                break

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def exist_user(username: str, password: str, filename: str) -> bool:
        """Return True if the given user exists in the given filename, False otherwise."""
        exist=False
        with open(filename, "r") as f:
            data = json.load(f)
        
        for user_info in data["users"]:
            if user_info["username"] == username and user_info["password"] == password:
                exist=True 
        return exist
    
    @staticmethod
    def exist_username(username:str, filename:str)->bool:
        exist=False
        with open(filename, "r") as f:
            data = json.load(f)
        
        for user_info in data["users"]:
            if user_info["username"] == username:
                exist= True    
        return exist

