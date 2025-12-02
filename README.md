# Medicine Data Visualization System (MDVS)

A full-stack web application for exploring and analyzing medicine data with interactive visualizations and multi-format export capabilities.

---

## Features

### Search & Filter
Real time medicine search with advanced filtering by category, manufacturer, and price range.

### Interactive Visualizations
D3.js powered charts showing category distributions, manufacturer rankings, and statistical insights.

### Detailed Medicine Information
Complete medicine profiles including dosage, uses, side effects, ingredients, and manufacturer details.

### Multi-Format Export
Export data in **PDF** format with customizable options for details, statistics, and chart visualizations.

---

## Tech Stack

**Backend:** FastAPI • SQLAlchemy • PostgreSQL • Pandas • ReportLab  
**Frontend:** HTML5 • CSS3 • JavaScript • D3.js • React  
**Server:** Uvicorn

---

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 13+
- Git

### Installation

**1. Clone and setup backend**
```bash
git clone https://github.com/thekavishshah/MedicineAnalysis.git
cd MedicineAnalysis/backend

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

**2. Configure database**

Edit `backend/database.py`:
```python
SQLALCHEMY_DATABASE_URL = "postgresql://username:password@localhost/medicine_db"
```

**3. Initialize database**
```bash
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
```

**4. Run the application**

Terminal 1 (Backend):
```bash
cd backend
uvicorn main:app --reload --port 8000
```

Terminal 2 (Frontend):
```bash
cd frontend
python -m http.server 8080
```

**5. Open in browser**
```
http://localhost:8080
```

---

## Project Structure

```
MedicineAnalysis/
├── backend/
│   ├── routers/
│   │   ├── export.py          # Export endpoints (CSV, JSON, Excel, PDF)
│   │   └── medicines.py       # Medicine CRUD operations
│   ├── models/
│   │   └── medicine.py        # Database models
│   ├── database.py            # Database configuration
│   ├── main.py                # FastAPI application
│   └── requirements.txt
│
└── frontend/
    ├── css/
    │   └── styles.css
    ├── js/
    │   ├── main.js            # Tab navigation
    │   ├── medicines_search.js # Search functionality
    │   ├── insights.js        # Visualizations
    │   └── export.js          # Export functionality
    └── index.html
```

---

## API Endpoints

### Medicines
- `GET /api/medicines` - Get all medicines (supports filters)
- `GET /api/medicines/{id}` - Get medicine by ID
- `POST /api/medicines` - Create new medicine
- `PUT /api/medicines/{id}` - Update medicine
- `DELETE /api/medicines/{id}` - Delete medicine

### Export
- `POST /api/export/pdf` - Export to PDF with charts


## Database Schema

**Entities:** Medicine • Manufacturer • Category • Ingredient

**Relationships:**
- Manufacturer → Medicine (1:N)
- Category → Medicine (1:N)
- Medicine ↔ Ingredient (M:N via MedicineIngredient)

**Key Constraints:**
- Unique names for Manufacturer, Category, Ingredient
- Medicine requires ManufacturerID and CategoryID (NOT NULL)
- Composite primary key for MedicineIngredient

---
