from datetime import datetime
from pydantic import BaseModel, EmailStr, HttpUrl, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LinkCreateRequest(BaseModel):
    original_url: HttpUrl
    custom_alias: str | None = Field(default=None, min_length=3, max_length=64)
    expires_at: datetime | None = None


class LinkUpdateRequest(BaseModel):
    original_url: HttpUrl | None = None
    new_short_code: str | None = Field(default=None, min_length=3, max_length=64)


class LinkResponse(BaseModel):
    original_url: str
    short_code: str
    short_url: str
    created_at: datetime
    expires_at: datetime | None
    is_guest: bool

    class Config:
        from_attributes = True


class LinkStatsResponse(BaseModel):
    original_url: str
    short_code: str
    created_at: datetime
    click_count: int
    last_used_at: datetime | None
    expires_at: datetime | None


class SearchResponse(BaseModel):
    found: bool
    short_code: str | None = None
    short_url: str | None = None


class MessageResponse(BaseModel):
    message: str