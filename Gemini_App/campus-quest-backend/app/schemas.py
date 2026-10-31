from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from app.db.models import Role, QuestType

class UserRegister(BaseModel):
    neptun_code: str
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    neptun_code: str
    password: str

class UserOut(BaseModel):
    id: str
    neptun_code: str
    name: str
    role: Role
    level: int
    xp: int
    coins: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class QuestOut(BaseModel):
    id: str
    title: str
    description: str
    type: QuestType
    xp_reward: int
    coin_reward: int
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RedeemQR(BaseModel):
    qr_token: str

class QuestRedeemResult(BaseModel):
    message: str
    rewards: Dict[str, int]
    current_stats: Dict[str, int]
