from typing import Optional

from pydantic import BaseModel, AwareDatetime, ConfigDict


class UserCreate(BaseModel):
    username: str
    password: str
    email: str


class UserLogin(BaseModel):
    password: str
    email: str


class CurrentUser(BaseModel):
    username: str
    email: str
    created_at: Optional[AwareDatetime]
    updated_at: Optional[AwareDatetime]

    model_config = ConfigDict(from_attributes=True)


class PatchUser(BaseModel):
    is_admin: Optional[bool] = None
