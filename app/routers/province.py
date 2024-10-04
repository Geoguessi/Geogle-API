from fastapi import APIRouter, HTTPException
from app.services.province_service import get_provinces

router = APIRouter()

@router.get("/provinces")
def provinces():
    return get_provinces()