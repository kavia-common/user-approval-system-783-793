from typing import Optional, Literal, List
from pydantic import BaseModel, Field, EmailStr


# Auth
class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: Literal["bearer"] = Field("bearer", description="Token type")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="User password")


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="User password")
    full_name: str = Field(..., description="Full name for profile")


# Users / Profiles
class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: Literal["user", "admin"]
    is_active: bool


class ProfileOut(BaseModel):
    user_id: int
    full_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, description="Full name")
    bio: Optional[str] = Field(None, description="Short bio")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")


# Posts
class PostCreate(BaseModel):
    content: str = Field(..., description="Post content")


class PostOut(BaseModel):
    id: int
    user_id: int
    content: str
    created_at: str


# Engagements
class EngagementCreate(BaseModel):
    type: Literal["like", "comment", "share"] = Field(..., description="Engagement type")
    content: Optional[str] = Field(None, description="Optional text for comments")


class EngagementOut(BaseModel):
    id: int
    post_id: int
    user_id: int
    type: str
    content: Optional[str]
    created_at: str


# Analytics
class AnalyticsSummary(BaseModel):
    total_users: int
    total_posts: int
    total_engagements: int
    top_posts: List[dict]
    recent_growth: dict
