from app.db.database import SessionLocal, engine, Base
from app.db import models

Base.metadata.create_all(bind=engine)
db = SessionLocal()

def seed_data():
    existing_quest = db.query(models.Quest).filter(
        models.Quest.qr_secret_token == "GOLYAHET_MEGNYITO_2026"
    ).first()
    
    if not existing_quest:
        demo_quest = models.Quest(
            title="Gólyahét Megnyitó",
            description="Látogass el a megnyitóra és olvasd be a projektor kódját!",
            type=models.QuestType.QR_EVENT,
            xp_reward=150,
            coin_reward=30,
            qr_secret_token="GOLYAHET_MEGNYITO_2026"
        )
        db.add(demo_quest)
        db.commit()
        print("Minta küldetés sikeresen létrehozva! QR token: GOLYAHET_MEGNYITO_2026")
    else:
        print("A minta küldetés már létezik.")
    
    db.close()

if __name__ == "__main__":
    seed_data()
