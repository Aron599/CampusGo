from pathlib import Path
import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(prefix="/qr", tags=["QR Scanner"])

ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"


def decode_qr_from_bytes(image_bytes: bytes) -> str:
    """Dekodolja a QR-kodot nyers kepbajtokbol."""
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="A kep nem olvashato vagy hibas formatumu.")

    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)

    if not data:
        raise HTTPException(status_code=404, detail="Nem talalhato ervenyes QR-kod a kepen.")

    return data


@router.get("/scan-mock")
def scan_mock_qr(filename: str = "mock_qr.png"):
    """Beolvassa a statikus mock QR-kepet az assets mappabol."""
    safe_name = Path(filename).name
    image_path = ASSETS_DIR / safe_name

    if not image_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"A(z) '{safe_name}' fajl nem talalhato az assets mappaban."
        )

    decoded_text = decode_qr_from_bytes(image_path.read_bytes())

    return {
        "source": "mock",
        "filename": safe_name,
        "qr_data": decoded_text,
    }


@router.post("/scan-upload")
async def scan_uploaded_qr(file: UploadFile = File(...)):
    """Beolvas egy feltoltott QR-kepet."""
    image_bytes = await file.read()
    decoded_text = decode_qr_from_bytes(image_bytes)

    return {
        "source": "upload",
        "filename": file.filename,
        "qr_data": decoded_text,
    }