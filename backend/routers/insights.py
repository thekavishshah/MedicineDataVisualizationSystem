from fastapi import APIRouter, HTTPException, Query
from database import get_cursor

router = APIRouter()


# CATEGORY ENDPOINTS

@router.get("/categories/distribution")
async def get_category_distribution():
    """Medicine distribution across all categories."""
    try:
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    c.name AS category,
                    COUNT(m.medicine_id) AS count,
                    ROUND(COUNT(m.medicine_id) * 100.0 / SUM(COUNT(m.medicine_id)) OVER(), 2) AS percentage
                FROM category c
                LEFT JOIN medicine m ON c.category_id = m.category_id
                GROUP BY c.category_id, c.name
                ORDER BY count DESC
            """)
            return {"data": cursor.fetchall()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories/classification")
async def get_category_by_classification():
    """Category breakdown by Prescription vs Over-the-Counter."""
    try:
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    c.name AS category,
                    m.classification,
                    COUNT(*) AS count
                FROM medicine m
                JOIN category c ON m.category_id = c.category_id
                GROUP BY c.name, m.classification
                ORDER BY c.name, m.classification
            """)
            results = cursor.fetchall()
            
            categories = {}
            for row in results:
                cat = row["category"]
                if cat not in categories:
                    categories[cat] = {"category": cat, "Prescription": 0, "Over-the-Counter": 0}
                categories[cat][row["classification"]] = row["count"]
            
            return {"data": list(categories.values())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories/{category_name}")
async def get_category_details(category_name: str):
    """Detailed info for a specific category."""
    try:
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    c.name AS category,
                    c.description,
                    COUNT(m.medicine_id) AS medicine_count,
                    COUNT(DISTINCT m.manufacturer_id) AS manufacturer_count
                FROM category c
                LEFT JOIN medicine m ON c.category_id = m.category_id
                WHERE c.name = %s
                GROUP BY c.category_id, c.name, c.description
            """, (category_name,))
            category_info = cursor.fetchone()
            
            if not category_info:
                raise HTTPException(status_code=404, detail=f"Category '{category_name}' not found")
            
            cursor.execute("""
                SELECT man.name AS manufacturer, COUNT(*) AS count
                FROM medicine m
                JOIN manufacturer man ON m.manufacturer_id = man.manufacturer_id
                JOIN category c ON m.category_id = c.category_id
                WHERE c.name = %s
                GROUP BY man.name
                ORDER BY count DESC
                LIMIT 5
            """, (category_name,))
            top_manufacturers = cursor.fetchall()
            
            cursor.execute("""
                SELECT m.dosage_form, COUNT(*) AS count
                FROM medicine m
                JOIN category c ON m.category_id = c.category_id
                WHERE c.name = %s
                GROUP BY m.dosage_form
                ORDER BY count DESC
            """, (category_name,))
            dosage_forms = cursor.fetchall()
            
            return {
                "category": category_info,
                "top_manufacturers": top_manufacturers,
                "dosage_forms": dosage_forms
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# MANUFACTURER ENDPOINTS

@router.get("/manufacturers/ranking")
async def get_manufacturer_ranking(limit: int = Query(default=10, ge=1, le=50)):
    """Top manufacturers ranked by medicine count."""
    try:
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    man.name AS manufacturer,
                    COUNT(m.medicine_id) AS medicine_count,
                    COUNT(DISTINCT m.category_id) AS category_count,
                    ROUND(COUNT(m.medicine_id) * 100.0 / (SELECT COUNT(*) FROM medicine), 2) AS market_share
                FROM manufacturer man
                LEFT JOIN medicine m ON man.manufacturer_id = m.manufacturer_id
                GROUP BY man.manufacturer_id, man.name
                ORDER BY medicine_count DESC
                LIMIT %s
            """, (limit,))
            return {"data": cursor.fetchall()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/manufacturers/{manufacturer_name}")
async def get_manufacturer_details(manufacturer_name: str):
    """Detailed info for a specific manufacturer."""
    try:
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    man.name AS manufacturer,
                    COUNT(m.medicine_id) AS medicine_count,
                    COUNT(DISTINCT m.category_id) AS category_count
                FROM manufacturer man
                LEFT JOIN medicine m ON man.manufacturer_id = m.manufacturer_id
                WHERE man.name = %s
                GROUP BY man.manufacturer_id, man.name
            """, (manufacturer_name,))
            manufacturer_info = cursor.fetchone()
            
            if not manufacturer_info:
                raise HTTPException(status_code=404, detail=f"Manufacturer '{manufacturer_name}' not found")
            
            cursor.execute("""
                SELECT c.name AS category, COUNT(*) AS count
                FROM medicine m
                JOIN category c ON m.category_id = c.category_id
                JOIN manufacturer man ON m.manufacturer_id = man.manufacturer_id
                WHERE man.name = %s
                GROUP BY c.name
                ORDER BY count DESC
            """, (manufacturer_name,))
            categories = cursor.fetchall()
            
            cursor.execute("""
                SELECT m.classification, COUNT(*) AS count
                FROM medicine m
                JOIN manufacturer man ON m.manufacturer_id = man.manufacturer_id
                WHERE man.name = %s
                GROUP BY m.classification
            """, (manufacturer_name,))
            classifications = cursor.fetchall()
            
            return {
                "manufacturer": manufacturer_info,
                "categories": categories,
                "classifications": classifications
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# OVERVIEW ENDPOINT

@router.get("/overview")
async def get_insights_overview():
    """High-level dataset overview for dashboard."""
    try:
        with get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS count FROM medicine")
            total_medicines = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) AS count FROM manufacturer")
            total_manufacturers = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) AS count FROM category")
            total_categories = cursor.fetchone()["count"]
            
            cursor.execute("""
                SELECT classification, COUNT(*) AS count 
                FROM medicine 
                GROUP BY classification
            """)
            classification_split = {row["classification"]: row["count"] for row in cursor.fetchall()}
            
            cursor.execute("""
                SELECT c.name, COUNT(*) AS count
                FROM medicine m
                JOIN category c ON m.category_id = c.category_id
                GROUP BY c.name
                ORDER BY count DESC
                LIMIT 1
            """)
            top_category = cursor.fetchone()
            
            cursor.execute("""
                SELECT man.name, COUNT(*) AS count
                FROM medicine m
                JOIN manufacturer man ON m.manufacturer_id = man.manufacturer_id
                GROUP BY man.name
                ORDER BY count DESC
                LIMIT 1
            """)
            top_manufacturer = cursor.fetchone()
            
            return {
                "total_medicines": total_medicines,
                "total_manufacturers": total_manufacturers,
                "total_categories": total_categories,
                "classification_split": classification_split,
                "top_category": top_category,
                "top_manufacturer": top_manufacturer
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
