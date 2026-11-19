import uuid
from datetime import datetime
import enum
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base

class Role(str, enum.Enum):
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"

class QuestType(str, enum.Enum):
    QR_EVENT = "QR_EVENT"
    SURVEY = "SURVEY"
    TEXT_INPUT = "TEXT_INPUT"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    neptun_code = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(Enum(Role), default=Role.STUDENT)

    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    coins = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    completed_quests = relationship("UserQuest", back_populates="user")

    purchases = relationship("UserPurchase", back_populates="user")

class ShopItem(Base):
    __tablename__ = "shop_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=True)  # None = korlatlan keszlet
    is_active = Column(Boolean, default=True)

    purchases = relationship("UserPurchase", back_populates="item")

class UserPurchase(Base):
    __tablename__ = "user_purchases"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("shop_items.id"), nullable=False)
    price_paid = Column(Integer, nullable=False)
    coupon_code = Column(String, unique=True, nullable=False)
    purchased_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="purchases")
    item = relationship("ShopItem", back_populates="purchases")

class Quest(Base):
    __tablename__ = "quests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    type = Column(Enum(QuestType), default=QuestType.QR_EVENT)
    xp_reward = Column(Integer, default=50)
    coin_reward = Column(Integer, default=10)

    qr_secret_token = Column(String, unique=True, nullable=True, index=True)
    expires_at = Column(DateTime, nullable=True)

    completions = relationship("UserQuest", back_populates="quest")

class UserQuest(Base):
    __tablename__ = "user_quests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quest_id = Column(String, ForeignKey("quests.id", ondelete="CASCADE"), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "quest_id", name="uix_user_quest"),)

    user = relationship("User", back_populates="completed_quests")
    quest = relationship("Quest", back_populates="completions")
