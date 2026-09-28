from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas
from app.db.session import get_db
from app.core.security import get_current_active_user, get_current_admin_user
from app.core.rate_limiter import RateLimiterDep

router = APIRouter()

# Diagnostic Centre Endpoints
@router.post("/centres/", response_model=schemas.CentreRead, dependencies=[Depends(RateLimiterDep(times=10, seconds=60))])
def create_centre(
    centre: schemas.CentreCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    db_centre = models.DiagnosticCentre(**centre.model_dump())
    db.add(db_centre)
    db.commit()
    db.refresh(db_centre)
    return db_centre

@router.get("/centres/", response_model=List[schemas.CentreRead])
def read_centres(
    skip: int = 0,
    limit: int = 100,
    location: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    query = db.query(models.DiagnosticCentre)
    if location:
        query = query.filter(models.DiagnosticCentre.location.ilike(f"%{location}%"))
    centres = query.offset(skip).limit(limit).all()
    return centres

@router.get("/centres/{centre_id}", response_model=schemas.CentreRead)
def read_centre(
    centre_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    centre = db.query(models.DiagnosticCentre).filter(models.DiagnosticCentre.id == centre_id).first()
    if centre is None:
        raise HTTPException(status_code=404, detail="Centre not found")
    return centre

# Diagnostic Test Endpoints
@router.post("/tests/", response_model=schemas.TestRead)
def create_test(
    test: schemas.TestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    # Verify centre exists
    centre = db.query(models.DiagnosticCentre).filter(models.DiagnosticCentre.id == test.centre_id).first()
    if not centre:
        raise HTTPException(status_code=404, detail="Centre not found")
    
    db_test = models.DiagnosticTest(**test.model_dump())
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

@router.get("/tests/", response_model=List[schemas.TestRead])
def read_tests(
    skip: int = 0,
    limit: int = 100,
    centre_id: int = None,
    name: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    query = db.query(models.DiagnosticTest)
    if centre_id:
        query = query.filter(models.DiagnosticTest.centre_id == centre_id)
    if name:
        query = query.filter(models.DiagnosticTest.name.ilike(f"%{name}%"))
    if min_price is not None:
        query = query.filter(models.DiagnosticTest.price >= min_price)
    if max_price is not None:
        query = query.filter(models.DiagnosticTest.price <= max_price)
    tests = query.offset(skip).limit(limit).all()
    return tests

@router.get("/tests/{test_id}", response_model=schemas.TestRead)
def read_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    test = db.query(models.DiagnosticTest).filter(models.DiagnosticTest.id == test_id).first()
    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")
    return test