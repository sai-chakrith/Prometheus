"""
Export routes - Export query results to various formats
"""
import logging
from fastapi import APIRouter
from fastapi.responses import StreamingResponse, Response
from typing import List
import pandas as pd
import io

from models.schemas import ExportRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/export", tags=["Export"])


@router.post("/csv")
async def export_csv(export_data: ExportRequest):
    """Export sources to CSV"""
    logger.info(f"Exporting {len(export_data.sources)} results to CSV")
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame(export_data.sources)
        
        # Create CSV in memory
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        stream.seek(0)
        
        return StreamingResponse(
            iter([stream.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=prometheus_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
    
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        raise


@router.post("/excel")
async def export_excel(export_data: ExportRequest):
    """Export sources to Excel"""
    logger.info(f"Exporting {len(export_data.sources)} results to Excel")
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame(export_data.sources)
        
        # Create Excel in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Results', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Results']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        return Response(
            content=output.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=prometheus_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            }
        )
    
    except Exception as e:
        logger.error(f"Excel export error: {e}")
        raise


@router.post("/json")
async def export_json(export_data: ExportRequest):
    """Export sources to JSON"""
    logger.info(f"Exporting {len(export_data.sources)} results to JSON")
    
    try:
        import json
        
        # Create JSON
        json_data = json.dumps({
            "exported_at": pd.Timestamp.now().isoformat(),
            "total_results": len(export_data.sources),
            "results": export_data.sources
        }, indent=2)
        
        return Response(
            content=json_data,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=prometheus_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
            }
        )
    
    except Exception as e:
        logger.error(f"JSON export error: {e}")
        raise
