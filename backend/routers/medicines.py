from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from database import get_cursor

router = APIRouter()

class MedicineCreate(BaseModel):
    name: str
    strength: str
    category_id: Optional[int] = None
    manufacturer_id: Optional[int] = None
    dosage_form: Optional[str] = None
    indication: Optional[str] = None
    classification: Optional[str] = "Prescription"

class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    strength: Optional[str] = None
    category_id: Optional[int] = None
    manufacturer_id: Optional[int] = None
    dosage_form: Optional[str] = None
    indication: Optional[str] = None
    classification: Optional[str] = None

@router.get("/")
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
            m.dosage_form,
            m.strength,
            m.classification,
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

@router.get("/filters")
def get_filter_options():
    with get_cursor() as cur:
        cur.execute("SELECT manufacturer_id, name FROM manufacturer ORDER BY name")
        manufacturers = cur.fetchall()
        
        cur.execute("SELECT category_id, name FROM category ORDER BY name")
        categories = cur.fetchall()
        
        cur.execute("SELECT DISTINCT dosage_form FROM medicine WHERE dosage_form IS NOT NULL ORDER BY dosage_form")
        dosage_forms = [row["dosage_form"] for row in cur.fetchall()]
        
        cur.execute("SELECT DISTINCT classification FROM medicine WHERE classification IS NOT NULL ORDER BY classification")
        classifications = [row["classification"] for row in cur.fetchall()]
        
        return {
            "manufacturers": manufacturers,
            "categories": categories,
            "dosage_forms": dosage_forms,
            "classifications": classifications
        }

@router.get("/all")
def get_all_medicines(limit: int = 1000):
    sql = """
        SELECT
            m.medicine_id,
            m.name,
            m.indication,
            m.dosage_form,
            m.strength,
            m.classification,
            ma.name AS manufacturer_name,
            c.name AS category_name
        FROM medicine m
        LEFT JOIN manufacturer ma ON ma.manufacturer_id = m.manufacturer_id
        LEFT JOIN category c ON c.category_id = m.category_id
        ORDER BY m.name
        LIMIT %s;
    """
    
    with get_cursor() as cur:
        cur.execute(sql, (limit,))
        return {"results": cur.fetchall()}

@router.get("/{medicine_id}")
def get_medicine(medicine_id: int):
    sql_main = """
        SELECT
            m.medicine_id,
            m.name,
            m.dosage_form,
            m.strength,
            m.indication,
            m.classification,
            m.manufacturer_id,
            m.category_id,
            ma.name AS manufacturer_name,
            c.name AS category_name
        FROM medicine m
        LEFT JOIN manufacturer ma ON ma.manufacturer_id = m.manufacturer_id
        LEFT JOIN category c ON c.category_id = m.category_id
        WHERE m.medicine_id = %(id)s;
    """

    sql_ing = """
        SELECT
            i.name,
            mi.strength
        FROM medicine_ingredient mi
        JOIN ingredient i ON i.ingredient_id = mi.ingredient_id
        WHERE mi.medicine_id = %(id)s;
    """

    with get_cursor() as cur:
        cur.execute(sql_main, {"id": medicine_id})
        med = cur.fetchone()

        if not med:
            raise HTTPException(404, "Medicine not found")

        cur.execute(sql_ing, {"id": medicine_id})
        ingredients = cur.fetchall()
        med["ingredients"] = ingredients

    return med

@router.post("/")
def create_medicine(medicine: MedicineCreate):
    """Insert a new medicine into the database."""
    sql = """
        INSERT INTO medicine (name, strength, category_id, manufacturer_id, dosage_form, indication, classification)
        VALUES (%(name)s, %(strength)s, %(category_id)s, %(manufacturer_id)s, %(dosage_form)s, %(indication)s, %(classification)s)
        RETURNING medicine_id;
    """
    
    with get_cursor() as cur:
        cur.execute(sql, {
            "name": medicine.name,
            "strength": medicine.strength,
            "category_id": medicine.category_id,
            "manufacturer_id": medicine.manufacturer_id,
            "dosage_form": medicine.dosage_form,
            "indication": medicine.indication,
            "classification": medicine.classification
        })
        result = cur.fetchone()
        
    return {"message": "Medicine created successfully", "medicine_id": result["medicine_id"]}

@router.put("/{medicine_id}")
def update_medicine(medicine_id: int, medicine: MedicineUpdate):
    """Update an existing medicine."""
    with get_cursor() as cur:
        cur.execute("SELECT medicine_id FROM medicine WHERE medicine_id = %s", (medicine_id,))
        if not cur.fetchone():
            raise HTTPException(404, "Medicine not found")
        
        updates = []
        params = {"id": medicine_id}
        
        if medicine.name is not None:
            updates.append("name = %(name)s")
            params["name"] = medicine.name
        if medicine.strength is not None:
            updates.append("strength = %(strength)s")
            params["strength"] = medicine.strength
        if medicine.category_id is not None:
            updates.append("category_id = %(category_id)s")
            params["category_id"] = medicine.category_id
        if medicine.manufacturer_id is not None:
            updates.append("manufacturer_id = %(manufacturer_id)s")
            params["manufacturer_id"] = medicine.manufacturer_id
        if medicine.dosage_form is not None:
            updates.append("dosage_form = %(dosage_form)s")
            params["dosage_form"] = medicine.dosage_form
        if medicine.indication is not None:
            updates.append("indication = %(indication)s")
            params["indication"] = medicine.indication
        if medicine.classification is not None:
            updates.append("classification = %(classification)s")
            params["classification"] = medicine.classification
        
        if not updates:
            raise HTTPException(400, "No fields to update")
        
        sql = f"UPDATE medicine SET {', '.join(updates)} WHERE medicine_id = %(id)s"
        cur.execute(sql, params)
        
    return {"message": "Medicine updated successfully"}

@router.delete("/{medicine_id}")
def delete_medicine(medicine_id: int):
    """Delete a medicine from the database."""
    with get_cursor() as cur:
        cur.execute("SELECT medicine_id FROM medicine WHERE medicine_id = %s", (medicine_id,))
        if not cur.fetchone():
            raise HTTPException(404, "Medicine not found")
        
        cur.execute("DELETE FROM medicine_ingredient WHERE medicine_id = %s", (medicine_id,))
        cur.execute("DELETE FROM medicine WHERE medicine_id = %s", (medicine_id,))
        
    return {"message": "Medicine deleted successfully"}
