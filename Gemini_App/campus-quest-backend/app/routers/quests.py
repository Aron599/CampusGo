from datetime import datetime
from typing import List
import math
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.schemas import QuestOut, RedeemQR, QuestRedeemResult
from app.core.security import get_current_user

router = APIRouter(prefix="/api/quests", tags=["Quests"])

def calculate_new_level(xp: int) -> int:
    return math.floor(xp / 200) + 1

@router.get("/", response_model=List[QuestOut])
def get_available_quests(
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    completed_subquery = db.query(models.UserQuest.quest_id).filter(
        models.UserQuest.user_id == current_user.id
    ).subquery()

    quests = db.query(models.Quest).filter(~models.Quest.id.in_(completed_subquery)).all()
    return quests

@router.post("/redeem-qr", response_model=QuestRedeemResult)
def redeem_qr(
    payload: RedeemQR,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    quest = db.query(models.Quest).filter(
        models.Quest.qr_secret_token == payload.qr_token
    ).first()
    
    if not quest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Érvénytelen QR kód.")

    if quest.expires_at and datetime.utcnow() > quest.expires_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ez a küldetés már lejárt.")

    already_done = db.query(models.UserQuest).filter(
        models.UserQuest.user_id == current_user.id,
        models.UserQuest.quest_id == quest.id
    ).first()

    if already_done:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Ezt a küldetést már korábban beváltottad!"
        )

    try:
        user_quest = models.UserQuest(user_id=current_user.id, quest_id=quest.id)
        db.add(user_quest)

        current_user.xp += quest.xp_reward
        current_user.coins += quest.coin_reward
        current_user.level = calculate_new_level(current_user.xp)

        db.commit()
        db.refresh(current_user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Hiba a jóváírás során.")

    return {
        "message": "Küldetés sikeresen teljesítve!",
        "rewards": {"xp": quest.xp_reward, "coins": quest.coin_reward},
        "current_stats": {
            "level": current_user.level,
            "xp": current_user.xp,
            "coins": current_user.coins
        }
    }
