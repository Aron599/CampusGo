import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User, ShopItem, UserPurchase
from app.schemas import ShopItemOut, BuyItemResponse, PurchaseOut
from app.core.security import get_current_user

router = APIRouter(prefix="/api/shop", tags=["Shop"])


@router.get("/items", response_model=List[ShopItemOut])
def get_shop_items(db: Session = Depends(get_db)):
    """Kilistazza az osszes aktiv megvasarolhato termeket."""
    return db.query(ShopItem).filter(ShopItem.is_active == True).all()


@router.post("/buy/{item_id}", response_model=BuyItemResponse)
def buy_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Termek vasarlasa coinert egyenleg- es keszletellenorzessel."""
    item = (
        db.query(ShopItem)
        .filter(ShopItem.id == item_id, ShopItem.is_active == True)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A termek nem talalhato vagy nem elerheto.",
        )

    if item.stock is not None and item.stock <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ez a termek jelenleg elfogyott.",
        )

    if current_user.coins < item.price:
        missing = item.price - current_user.coins
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nincs eleg coinod! Ennyi hianyzik meg: {missing} coin.",
        )

    # Coin levonasa es keszlet csokkentese
    current_user.coins -= item.price
    if item.stock is not None:
        item.stock -= 1

    # Egyedi bevaltokod generalasa a bufehez
    coupon_code = f"CAMPUS-{uuid.uuid4().hex[:6].upper()}"

    purchase = UserPurchase(
        user_id=current_user.id,
        item_id=item.id,
        price_paid=item.price,
        coupon_code=coupon_code,
    )

    db.add(purchase)
    db.commit()
    db.refresh(current_user)

    return BuyItemResponse(
        message="Sikeres vasarlas!",
        item_name=item.name,
        price_paid=item.price,
        remaining_coins=current_user.coins,
        coupon_code=coupon_code,

    )


@router.get("/my-purchases", response_model=List[PurchaseOut])
def get_my_purchases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Visszaadja a bejelentkezett felhasznalo megvasarolt kuponjait."""
    purchases = (
        db.query(UserPurchase)
        .filter(UserPurchase.user_id == current_user.id)
        .order_by(UserPurchase.purchased_at.desc())
        .all()
    )

    return [
        PurchaseOut(
            id=p.id,
            item_id=p.item_id,
            item_name=p.item.name,
            price_paid=p.price_paid,
            coupon_code=p.coupon_code,
            purchased_at=p.purchased_at,
        )
        for p in purchases
    ]
@router.post("/dev/add-coins")
def add_test_coins(
    amount: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Csak teszteleshez: coin hozzaadasa a bejelentkezett felhasznalonak."""
    current_user.coins += amount
    db.commit()
    db.refresh(current_user)
    return {
        "message": f"{amount} coin hozzaadva!",
        "current_coins": current_user.coins,
    }