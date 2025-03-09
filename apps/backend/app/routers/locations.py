from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas import location as location_schema
from app.db.session import get_db
from app.crud.locations import get_location, get_all_locations, create_location as create_location_service

router = APIRouter(
    prefix="/locations",
    tags=["locations"]
)

@router.get("", response_model=List[location_schema.Location])
async def list_locations(db: Session = Depends(get_db)):
    """Get all available locations"""
    return get_all_locations(db)

@router.get("/{location_id}", response_model=location_schema.Location)
async def get_location_by_id(location_id: int, db: Session = Depends(get_db)):
    """Get a specific location by ID"""
    location = get_location(db, location_id)
    if not location:
        raise HTTPException(
            status_code=404,
            detail=f"Location with ID {location_id} not found"
        )
    return location 

@router.post("", response_model=location_schema.Location)
async def create_location(location: location_schema.LocationCreate, db: Session = Depends(get_db)):
    """Create a new location"""
    return create_location_service(db, location)