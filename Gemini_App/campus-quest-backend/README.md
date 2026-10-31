# CampusQuest Backend (MVP)

Egyetemi gamifikációs platform MVP törzse, amely lehetővé teszi a hallgatók számára, hogy valós és online egyetemi feladatok (QR kódok, kérdőívek) teljesítésével XP-t és egyetemi érméket gyűjtsenek, szintet lépjenek és jutalmakat oldjanak fel.

## Fő technológiák
- **FastAPI** (Python 3.10+)
- **SQLAlchemy** (ORM)
- **SQLite** (helyi fejlesztéshez) / **PostgreSQL** (élesítéshez)
- **JWT (JSON Web Tokens)** + Passlib (bcrypt) a biztonságos hitelesítéshez

---

## Gyors indítás helyi környezetben

### 1. Klónozás és környezet létrehozása
```bash
git clone [https://github.com/](https://github.com/)<felhasznaloneved>/campus-quest-backend.git
cd campus-quest-backend

python -m venv venv

# Linux / macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
