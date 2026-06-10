import os
import random
import time

from locust import HttpUser, between, task


class NotificationApiUser(HttpUser):
    wait_time = between(0.5, 2)

    def on_start(self):
        suffix = f"{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
        self.email = os.getenv("LOCUST_EMAIL", f"locust_{suffix}@example.com")
        self.password = os.getenv("LOCUST_PASSWORD", "pass12345")
        self.headers = {}
        self.notification_ids = []

        self.client.post(
            "/auth/register",
            json={
                "email": self.email,
                "username": f"locust_{suffix}",
                "full_name": "Locust Test User",
                "password": self.password,
            },
            name="/auth/register",
        )

        response = self.client.post(
            "/auth/login",
            json={"email": self.email, "password": self.password},
            name="/auth/login",
        )

        if response.ok:
            token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {token}"}

    @task(1)
    def get_current_user(self):
        self.client.get("/auth/me", headers=self.headers, name="/auth/me")

    @task(5)
    def list_notifications(self):
        response = self.client.get(
            "/notifications/",
            headers=self.headers,
            name="/notifications/",
        )

        if response.ok:
            self.notification_ids = [item["id"] for item in response.json()]

    @task(2)
    def create_notification(self):
        response = self.client.post(
            "/notifications/",
            headers=self.headers,
            json={
                "recipient": f"user_{random.randint(1, 1000)}@example.com",
                "channel": random.choice(["email", "sms", "other"]),
                "subject": "Load test notification",
                "content": "Created by Locust during API load testing.",
            },
            name="/notifications/ create",
        )

        if response.ok:
            self.notification_ids.append(response.json()["id"])

    @task(2)
    def get_notification_by_id(self):
        if not self.notification_ids:
            return

        notification_id = random.choice(self.notification_ids)
        self.client.get(
            f"/notifications/{notification_id}",
            headers=self.headers,
            name="/notifications/{id}",
        )
