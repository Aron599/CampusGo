from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.schemas import UserRegister, UserLogin, Token, UserOut
from app.core.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        (models.User.neptun_code == user_data.neptun_code.upper()) | 
        (models.User.email == user_data.email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="A Neptun-kód vagy email már használatban van."
        )

    new_user = models.User(
        neptun_code=user_data.neptun_code.upper(),
        email=user_data.email,
        name=user_data.name,
        password_hash=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Sikeres regisztráció!", "userId": new_user.id}

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.neptun_code == login_data.neptun_code.upper()
    ).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Hibás Neptun-kód vagy jelszó."
        )

    token = create_access_token(data={"sub": user.id, "role": user.role.value})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserOut)
def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user
