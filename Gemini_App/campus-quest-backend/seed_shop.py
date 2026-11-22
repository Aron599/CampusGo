from app.db.database import SessionLocal, engine, Base
from app.db.models import ShopItem

Base.metadata.create_all(bind=engine)


def seed_shop_items():
    db = SessionLocal()
    try:
        items = [
            ShopItem(
                name="Kave",
                description="Egy friss eszpresszo vagy cappuccino az egyetemi bufeben.",
                price=50,
                stock=1000,
            ),
            ShopItem(
                name="Suti",
                description="Egy szabadon valasztott friss sutemeny.",
                price=30,
                stock=200,
            ),
        ]

        added = 0
        for item in items:
            exists = db.query(ShopItem).filter(ShopItem.name == item.name).first()
            if not exists:
                db.add(item)
                added += 1

        db.commit()
        print(f"Shop feltoltve! Uj termekek szama: {added}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_shop_items()