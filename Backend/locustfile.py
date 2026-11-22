
# # from locust import HttpUser, task, between


# # class GharsetuUser(HttpUser):

# #     wait_time = between(1, 3)

# #     def on_start(self):
# #         self.client.headers.update({
# #             "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzk1MTk3MzM1LCJpYXQiOjE3OTUxOTY0MzUsImp0aSI6ImI4MGIzN2E3NmMxNTQ0NWM5MjI4ZmU3MTY0M2RkYWY2IiwidXNlcl9pZCI6IjMifQ.KnrP1uosyAxuOEJfX8BZp2KtupoqQF97asuLvoCXcxM"
# #         })

# #     @task
# #     def my_leads(self):
# #         with self.client.get(
# #             "/Lead/my-leads/",
# #             name="My Leads",
# #             catch_response=True
# #         ) as response:

# #             if response.status_code == 200:
# #                 response.success()
# #             elif response.status_code == 401:
# #                 response.failure("JWT token invalid or expired")
# #             else:
# #                 response.failure(
# #                     f"Unexpected status: {response.status_code}"
# #                 )



# import os
# import json
# import time
# import base64

# from locust import HttpUser, task, between
# from locust.exception import StopUser


# class GharsetuUser(HttpUser):

#     wait_time = between(1, 3)

#     LOGIN_URL = "/api/token/"
#     REFRESH_URL = "/api/token/refresh/"

#     def on_start(self):
#         self.access_token = None
#         self.refresh_token = None
#         self.token_expiry = 0

#         self.username = os.getenv("TEST_USERNAME")
#         self.password = os.getenv("TEST_PASSWORD")

#         if not self.username or not self.password:
#             raise StopUser("Test credentials missing")

#         if not self.login():
#             raise StopUser("Login failed")

#     def get_token_expiry(self, token):
#         # Decode JWT payload only to read expiry.
#         # Actual token validation is done by the server.
#         payload = token.split(".")[1]
#         payload += "=" * (-len(payload) % 4)

#         decoded = base64.urlsafe_b64decode(payload)
#         data = json.loads(decoded)

#         return data["exp"]

#     def login(self):
#         response = self.client.post(
#             self.LOGIN_URL,
#             json={
#                 "username": self.username,
#                 "password": self.password
#             },
#             name="Login"
#         )

#         if response.status_code != 200:
#             return False

#         data = response.json()

#         self.access_token = data["access"]
#         self.refresh_token = data["refresh"]

#         self.token_expiry = self.get_token_expiry(
#             self.access_token
#         )

#         return True

#     def refresh_access_token(self):

#         response = self.client.post(
#             self.REFRESH_URL,
#             json={
#                 "refresh": self.refresh_token
#             },
#             name="Refresh Token"
#         )

#         if response.status_code == 200:
#             data = response.json()

#             self.access_token = data["access"]

#             self.token_expiry = self.get_token_expiry(
#                 self.access_token
#             )

#             # If refresh rotation is enabled, save new refresh token.
#             if "refresh" in data:
#                 self.refresh_token = data["refresh"]

#             return True

#         # Refresh failed: try logging in again.
#         return self.login()

#     def ensure_valid_token(self):

#         # Refresh 60 seconds before expiry.
#         if time.time() >= self.token_expiry - 60:
#             return self.refresh_access_token()

#         return True

#     @task
#     def my_leads(self):

#         if not self.ensure_valid_token():
#             raise StopUser("Unable to refresh JWT")

#         headers = {
#             "Authorization": f"Bearer {self.access_token}"
#         }

#         with self.client.get(
#             "/Lead/my-leads/",
#             headers=headers,
#             name="My Leads",
#             catch_response=True
#         ) as response:

#             if response.status_code == 200:
#                 response.success()

#             elif response.status_code == 401:
#                 response.failure("Unexpected JWT authentication failure")

#             else:
#                 response.failure(
#                     f"Unexpected status: {response.status_code}"
#                 )





# import os
# import json
# import time
# import base64

# from locust import HttpUser, task, between
# from locust.exception import StopUser


# class GharsetuUser(HttpUser):

#     wait_time = between(1, 3)

#     LOGIN_URL = "/User/login/"
#     REFRESH_URL = "/User/token/refresh/"

#     def on_start(self):
#         self.access_token = None
#         self.refresh_token = None
#         self.token_expiry = 0

#         self.username = os.getenv("TEST_USERNAME")
#         self.password = os.getenv("TEST_PASSWORD")

#         if not self.username or not self.password:
#             raise StopUser("Test credentials missing")

#         if not self.login():
#             raise StopUser("Login failed")

#     def get_token_expiry(self, token):
#         # Decode JWT payload only to read expiry.
#         # Actual token validation is done by the server.
#         payload = token.split(".")[1]
#         payload += "=" * (-len(payload) % 4)

#         decoded = base64.urlsafe_b64decode(payload)
#         data = json.loads(decoded)

#         return data["exp"]

#     def login(self):
#     response = self.client.post(
#         self.LOGIN_URL,
#         json={
#             "email": self.username,
#             "password": self.password
#         },
#         name="Login"
#     )

#     if response.status_code != 200:
#         print("Login failed:", response.status_code, response.text)
#         return False

#     data = response.json()

#     self.access_token = data["access"]
#     self.refresh_token = data["refresh"]
#     self.token_expiry = self.get_token_expiry(self.access_token)

#     return True

#     def refresh_access_token(self):

#         response = self.client.post(
#             self.REFRESH_URL,
#             json={
#                 "refresh": self.refresh_token
#             },
#             name="Refresh Token"
#         )

#         if response.status_code == 200:
#             data = response.json()

#             self.access_token = data["access"]

#             self.token_expiry = self.get_token_expiry(
#                 self.access_token
#             )

#             # If refresh rotation is enabled, save new refresh token.
#             if "refresh" in data:
#                 self.refresh_token = data["refresh"]

#             return True

#         # Refresh failed: try logging in again.
#         return self.login()

#     def ensure_valid_token(self):

#         # Refresh 60 seconds before expiry.
#         if time.time() >= self.token_expiry - 60:
#             return self.refresh_access_token()

#         return True

#     @task
#     def my_leads(self):

#         if not self.ensure_valid_token():
#             raise StopUser("Unable to refresh JWT")

#         headers = {
#             "Authorization": f"Bearer {self.access_token}"
#         }

#         with self.client.get(
#             "/Lead/my-leads/",
#             headers=headers,
#             name="My Leads",
#             catch_response=True
#         ) as response:

#             if response.status_code == 200:
#                 response.success()

#             elif response.status_code == 401:
#                 response.failure("Unexpected JWT authentication failure")

#             else:
#                 response.failure(
#                     f"Unexpected status: {response.status_code}"
#                 )






import os
import json
import time
import base64

from locust import HttpUser, task, between
from locust.exception import StopUser

class GharsetuUser(HttpUser):

    wait_time = between(1, 3)

    LOGIN_URL = "/User/login/"
    REFRESH_URL = "/User/token/refresh/"

    def on_start(self):
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = 0

        self.username = os.getenv("TEST_USERNAME")
        self.password = os.getenv("TEST_PASSWORD")

        if not self.username or not self.password:
            raise StopUser("Test credentials missing")

        if not self.login():
            raise StopUser("Login failed")

    def get_token_expiry(self, token):
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)

        decoded = base64.urlsafe_b64decode(payload)
        data = json.loads(decoded)

        return data["exp"]

    def login(self):
        response = self.client.post(
            self.LOGIN_URL,
            json={
                "email": self.username,
                "password": self.password
            },
            name="Login"
        )

        if response.status_code != 200:
            print(
                "Login failed:",
                response.status_code,
                response.text
            )
            return False

        data = response.json()

        self.access_token = data["access"]
        self.refresh_token = data["refresh"]
        self.token_expiry = self.get_token_expiry(
            self.access_token
        )

        return True

    def refresh_access_token(self):
        response = self.client.post(
            self.REFRESH_URL,
            json={
                "refresh": self.refresh_token
            },
            name="Refresh Token"
        )

        if response.status_code == 200:
            data = response.json()

            self.access_token = data["access"]
            self.token_expiry = self.get_token_expiry(
                self.access_token
            )

            if "refresh" in data:
                self.refresh_token = data["refresh"]

            return True

        return self.login()

    def ensure_valid_token(self):
        if time.time() >= self.token_expiry - 60:
            return self.refresh_access_token()

        return True

    @task
    def my_leads(self):

        if not self.ensure_valid_token():
            raise StopUser("Unable to refresh JWT")

        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        with self.client.get(
            "/Lead/my-leads/",
            headers=headers,
            name="My Leads",
            catch_response=True
        ) as response:

            if response.status_code == 200:
                response.success()

            elif response.status_code == 401:
                response.failure(
                    "Unexpected JWT authentication failure"
                )

            else:
                response.failure(
                    f"Unexpected status: {response.status_code}"
                )

