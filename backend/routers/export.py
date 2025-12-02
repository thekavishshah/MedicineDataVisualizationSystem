from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Any, List
from datetime import datetime
from database import get_cursor
import io

router = APIRouter()

def get_filtered_medicines(filters: Dict[str, Any] = None):
    """Fetch medicines from database with optional filters."""
    where = []
    params = {}
    
    if filters:
        if filters.get("q"):
            where.append("(m.name ILIKE %(q)s OR m.indication ILIKE %(q)s)")
            params["q"] = f"%{filters['q']}%"
        if filters.get("category"):
            where.append("c.name ILIKE %(category)s")
            params["category"] = f"%{filters['category']}%"
        if filters.get("manufacturer"):
            where.append("ma.name ILIKE %(manufacturer)s")
            params["manufacturer"] = f"%{filters['manufacturer']}%"
        if filters.get("classification"):
            where.append("m.classification = %(classification)s")
            params["classification"] = filters["classification"]
    
    where_sql = "WHERE " + " AND ".join(where) if where else ""
    
    sql = f"""
        SELECT
            m.name AS medicine_name,
            c.name AS category,
            ma.name AS manufacturer,
            m.dosage_form,
            m.strength,
            m.indication,
            m.classification
        FROM medicine m
        LEFT JOIN manufacturer ma ON ma.manufacturer_id = m.manufacturer_id
        LEFT JOIN category c ON c.category_id = m.category_id
        {where_sql}
        ORDER BY m.name;
    """
    
    with get_cursor() as cur:
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql.replace("WHERE ", ""))
        return cur.fetchall()

def generate_statistics(medicines: List[Dict], filters: Dict[str, Any]) -> Dict[str, Any]:
    """Generate statistics from medicine data."""
    total = len(medicines)
    
    categories = {}
    manufacturers = {}
    classifications = {}
    
    for med in medicines:
        cat = med.get("category") or "Unknown"
        categories[cat] = categories.get(cat, 0) + 1
        
        mfr = med.get("manufacturer") or "Unknown"
        manufacturers[mfr] = manufacturers.get(mfr, 0) + 1
        
        cls = med.get("classification") or "Unknown"
        classifications[cls] = classifications.get(cls, 0) + 1
    
    return {
        "total_medicines": total,
        "filters_applied": filters or {},
        "export_timestamp": datetime.now().isoformat(),
        "category_distribution": categories,
        "manufacturer_distribution": manufacturers,
        "classification_distribution": classifications,
        "top_5_categories": sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5],
        "top_5_manufacturers": sorted(manufacturers.items(), key=lambda x: x[1], reverse=True)[:5]
    }

@router.post("/pdf")
async def export_to_pdf(
    filters: Dict[str, Any] = {},
    include_details: bool = Query(False),
    include_charts: bool = Query(True),
    chart_images: Optional[List[str]] = None
):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER
        
        medicines = get_filtered_medicines(filters)
        statistics = generate_statistics(medicines, filters)
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        elements = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        elements.append(Paragraph("Medicine Data Export Report", title_style))
        elements.append(Spacer(1, 12))
        
        filter_text = "None"
        if filters:
            active_filters = [f"{k}: {v}" for k, v in filters.items() if v]
            if active_filters:
                filter_text = ", ".join(active_filters)
        
        info_text = f"""
        <b>Export Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Total Medicines:</b> {statistics['total_medicines']}<br/>
        <b>Filters Applied:</b> {filter_text}
        """
        elements.append(Paragraph(info_text, styles['Normal']))
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph("Summary Statistics", heading_style))
        elements.append(Spacer(1, 12))
        
        if statistics['top_5_categories']:
            elements.append(Paragraph("<b>Top 5 Categories</b>", styles['Heading3']))
            cat_data = [['Category', 'Count']]
            cat_data.extend(statistics['top_5_categories'])
            
            cat_table = Table(cat_data, colWidths=[4*inch, 1.5*inch])
            cat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(cat_table)
            elements.append(Spacer(1, 20))
        
        if statistics['top_5_manufacturers']:
            elements.append(Paragraph("<b>Top 5 Manufacturers</b>", styles['Heading3']))
            mfr_data = [['Manufacturer', 'Medicines Count']]
            mfr_data.extend(statistics['top_5_manufacturers'])
            
            mfr_table = Table(mfr_data, colWidths=[4*inch, 1.5*inch])
            mfr_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(mfr_table)
            elements.append(Spacer(1, 20))
        
        if statistics.get('classification_distribution'):
            elements.append(Paragraph("<b>Classification Distribution</b>", styles['Heading3']))
            cls_data = [['Classification', 'Count']]
            for cls, count in statistics['classification_distribution'].items():
                cls_data.append([cls, count])
            
            cls_table = Table(cls_data, colWidths=[4*inch, 1.5*inch])
            cls_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(cls_table)
            elements.append(Spacer(1, 20))
        
        if medicines and len(medicines) > 0:
            elements.append(PageBreak())
            elements.append(Paragraph("Medicine Data", heading_style))
            elements.append(Spacer(1, 12))
            
            table_data = [['Name', 'Category', 'Manufacturer', 'Classification']]
            for med in medicines:
                table_data.append([
                    str(med.get('medicine_name', 'N/A'))[:30],
                    str(med.get('category', 'N/A'))[:20],
                    str(med.get('manufacturer', 'N/A'))[:20],
                    str(med.get('classification', 'N/A'))
                ])
            
            data_table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.2*inch])
            data_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)])
            ]))
            elements.append(data_table)
        
        doc.build(elements)
        
        buffer.seek(0)
        filename = f"medicine_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting to PDF: {str(e)}")
