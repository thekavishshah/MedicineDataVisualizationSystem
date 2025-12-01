from fastapi import APIRouter
from database import get_cursor

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/insights")
def get_insights():
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS medicine_count FROM medicine;")
        medicine_count = cur.fetchone()

    return {
        "medicine_total": medicine_count["medicine_count"]
    }
