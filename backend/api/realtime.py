"""
Real-Time Data Collection API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.database import get_db
from backend.models.collection_log import DataCollectionLog
from backend.services.data_collector import DataCollectorService, collection_status, trigger_collection

router = APIRouter()


@router.get("/status")
async def get_realtime_status():
    """Get real-time data collection status"""
    
    status = collection_status()
    return status


@router.post("/collect")
async def trigger_data_collection(db: Session = Depends(get_db)):
    """Trigger manual data collection"""
    
    try:
        result = await trigger_collection()
        return {
            "status": "success",
            "message": "Data collection triggered successfully",
            "records_collected": result.get("records_collected", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data collection failed: {str(e)}")


@router.get("/logs")
async def get_collection_logs(
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, regex="^(pending|success|failed)$"),
    db: Session = Depends(get_db)
):
    """Get data collection logs"""
    
    query = db.query(DataCollectionLog)
    
    if status:
        query = query.filter(DataCollectionLog.status == status)
    
    logs = query.order_by(DataCollectionLog.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "source": log.source,
            "status": log.status,
            "records_collected": log.records_collected,
            "message": log.message,
            "started_at": log.started_at.isoformat() if log.started_at else None,
            "completed_at": log.completed_at.isoformat() if log.completed_at else None,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]


@router.get("/settings")
async def get_collection_settings():
    """Get data collection settings"""
    
    from backend.config import settings
    
    return {
        "polling_interval": settings.POLLING_INTERVAL,
        "data_source": settings.DATA_SOURCE,
        "mock_data_enabled": settings.MOCK_DATA_ENABLED,
        "api_configured": bool(settings.API_KEY)
    }


@router.post("/settings/interval")
async def update_polling_interval(
    interval_seconds: int = Query(..., ge=60, le=3600),
    db: Session = Depends(get_db)
):
    """Update the polling interval"""
    
    from backend.config import settings
    from backend.services.data_collector import update_interval
    
    # Update config
    settings.POLLING_INTERVAL = interval_seconds
    
    # Update scheduler
    update_interval(interval_seconds)
    
    return {
        "status": "success",
        "polling_interval": interval_seconds,
        "message": f"Polling interval updated to {interval_seconds} seconds"
    }