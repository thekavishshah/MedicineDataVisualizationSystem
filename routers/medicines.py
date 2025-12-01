from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from database import get_cursor

router = APIRouter()


@router.get("/", tags=["Medicines"])
def search_medicines(
    q: Optional[str] = Query(None),
    manufacturer: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = 50
):
    where = []
    params = {}

    if q:
        where.append("(m.name ILIKE %(q)s OR m.indication ILIKE %(q)s)")
        params["q"] = f"%{q}%"

    if manufacturer:
        where.append("ma.name ILIKE %(manufacturer)s")
        params["manufacturer"] = f"%{manufacturer}%"

    if category:
        where.append("c.name ILIKE %(category)s")
        params["category"] = f"%{category}%"

    where_sql = "WHERE " + " AND ".join(where) if where else ""

    sql = f"""
        SELECT
            m.medicine_id,
            m.name,
            m.indication,
            ma.name AS manufacturer_name,
            c.name AS category_name
        FROM medicine m
        LEFT JOIN manufacturer ma ON ma.manufacturer_id = m.manufacturer_id
        LEFT JOIN category c ON c.category_id = m.category_id
        {where_sql}
        ORDER BY m.name
        LIMIT %(limit)s;
    """

    params["limit"] = limit

    with get_cursor() as cur:
        cur.execute(sql, params)
        return {"results": cur.fetchall()}



@router.get("/{medicine_id}", tags=["Medicines"])
def get_medicine(medicine_id: int):
    # Get basic medicine info
    sql_main = """
        SELECT
            m.medicine_id,
            m.name,
            m.dosage_form,
            m.strength,
            m.indication,
            m.classification,
            ma.name AS manufacturer_name,
            c.name AS category_name
        FROM medicine m
        LEFT JOIN manufacturer ma ON ma.manufacturer_id = m.manufacturer_id
        LEFT JOIN category c ON c.category_id = m.category_id
        WHERE m.medicine_id = %(id)s;
    """

    # Get ingredients
    sql_ing = """
        SELECT
            i.name,
            mi.strength
        FROM medicine_ingredient mi
        JOIN ingredient i ON i.ingredient_id = mi.ingredient_id
        WHERE mi.medicine_id = %(id)s;
    """

    with get_cursor() as cur:
        # Fetch main medicine info
        cur.execute(sql_main, {"id": medicine_id})
        med = cur.fetchone()

        if not med:
            raise HTTPException(404, "Medicine not found")

        # Fetch ingredients
        cur.execute(sql_ing, {"id": medicine_id})
        ingredients = cur.fetchall()

        med["ingredients"] = ingredients

    return med
