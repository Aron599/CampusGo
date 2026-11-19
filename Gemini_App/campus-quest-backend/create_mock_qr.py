from pathlib import Path
import qrcode

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

# Ezt a szöveget fogja tartalmazni a mock QR-kód (később lehet quest ID vagy titkos kód is)
qr_content = "CAMPUS_QUEST_1"

img = qrcode.make(qr_content)
output_path = ASSETS_DIR / "mock_qr.png"
img.save(output_path)

print(f"Mock QR-kód elkészült: {output_path}")