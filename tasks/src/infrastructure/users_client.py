import httpx
import os
import logging

logger = logging.getLogger("fastapi-app")

USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://users_app:8000")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "")


class UsersClient:
    def __init__(self):
        self.base_url = USERS_SERVICE_URL
        self.headers = {"X-Internal-Key": INTERNAL_API_KEY}

    async def get_user_by_id(self, user_id: int) -> dict | None:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/api/users/{user_id}",
                    headers=self.headers
                )
                if response.status_code == 200:
                    return response.json()
                logger.warning("Users service returned %d for user_id=%d", response.status_code, user_id)
                return None
        except httpx.HTTPError as e:
            logger.error("Failed to call users service: %s", e)
            return None

    async def get_user_by_email(self, email: str) -> dict | None:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/api/users/by-email/{email}",
                    headers=self.headers
                )
                if response.status_code == 200:
                    return response.json()
                logger.warning("Users service returned %d for email=%s", response.status_code, email)
                return None
        except httpx.HTTPError as e:
            logger.error("Failed to call users service: %s", e)
            return None


users_client = UsersClient()
