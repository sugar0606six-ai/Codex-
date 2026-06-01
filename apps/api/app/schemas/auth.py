from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "analyst"
