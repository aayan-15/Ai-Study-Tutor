
import json
import os
import hashlib
import re


DATA_FILE = "data/students.json"


class Authentication:

    def __init__(self):
        os.makedirs("data", exist_ok=True)

        if not os.path.exists(DATA_FILE):
            self.save_users([])

    def load_users(self):
        with open(DATA_FILE, "r") as file:
            return json.load(file)

    def save_users(self, users):
        with open(DATA_FILE, "w") as file:
            json.dump(users, file, indent=4)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, email, username, password):

        users = self.load_users()

        email = email.strip().lower()
        username = username.strip()

        # Check duplicate username
        for user in users:
            if user["username"].lower() == username.lower():
                return False, "This username is already taken."

        # Check duplicate email
        for user in users:
            if user["email"].lower() == email:
                return False, "An account with this email already exists."

        # Validate email format
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if not re.match(email_pattern, email):
            return False, "Please enter a valid email address."

        new_user = {
            "email": email,
            "username": username,
            "password": self.hash_password(password),
            "role": "student"
        }

        users.append(new_user)
        self.save_users(users)

        return True, "Account created successfully!"

    def login(self, identifier, password):

        users = self.load_users()

        identifier = identifier.strip().lower()
        hashed_password = self.hash_password(password)

        for user in users:

            email_matches = user["email"].lower() == identifier
            username_matches = user["username"].lower() == identifier

            if (
                (email_matches or username_matches)
                and user["password"] == hashed_password
            ):
                return True, user

        return False, "Incorrect email/username or password."
