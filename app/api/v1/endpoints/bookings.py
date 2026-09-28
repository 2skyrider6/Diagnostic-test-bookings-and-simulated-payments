from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app import models, schemas
from app.db.session import get_db
from app.core.security import get_current_active_user
from app.services.email.service import email_service

router = APIRouter()

# Booking Endpoints
@router.post("/", response_model=schemas.BookingRead)
def create_booking(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Verify test exists
    test = db.query(models.DiagnosticTest).filter(models.DiagnosticTest.id == booking.test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Verify centre exists (through test)
    centre = db.query(models.DiagnosticCentre).filter(models.DiagnosticCentre.id == test.centre_id).first()
    if not centre:
        raise HTTPException(status_code=404, detail="Centre not found")
    
    # Check if appointment datetime is in the future
    if booking.appointment_datetime <= datetime.now():
        raise HTTPException(status_code=400, detail="Appointment must be in the future")
    
    # Create booking
    db_booking = models.Booking(
        user_id=current_user.id,
        test_id=booking.test_id,
        centre_id=test.centre_id,
        appointment_datetime=booking.appointment_datetime,
        amount=test.price,
        status=models.BookingStatus.PENDING
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    # Send booking confirmation email (non-blocking)
    try:
        booking_details = {
            "test_name": test.name,
            "centre_name": centre.name,
            "appointment_datetime": booking.appointment_datetime.strftime("%Y-%m-%d %H:%M"),
            "amount": float(test.price),
            "booking_id": db_booking.id
        }
        # In a real app, this would be done asynchronously
        # For now, we'll call it directly but it won't block the response if it fails
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.create_task(email_service.send_booking_confirmation(
            current_user.email,
            current_user.full_name,
            booking_details
        ))
    except Exception:
        # Don't fail the booking if email fails
        pass
    
    return db_booking

@router.get("/", response_model=List[schemas.BookingRead])
def read_bookings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    bookings = db.query(models.Booking).filter(models.Booking.user_id == current_user.id).offset(skip).limit(limit).all()
    return bookings

@router.get("/{booking_id}", response_model=schemas.BookingRead)
def read_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id,
        models.Booking.user_id == current_user.id
    ).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.put("/{booking_id}", response_model=schemas.BookingRead)
def update_booking(
    booking_id: int,
    booking_update: schemas.BookingUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id,
        models.Booking.user_id == current_user.id
    ).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Only allow updating certain fields for pending bookings
    if booking.status != models.BookingStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending bookings can be updated")
    
    # Update fields if provided
    update_data = booking_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(booking, field, value)
    
    db.commit()
    db.refresh(booking)
    return booking

@router.delete("/{booking_id}")
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id,
        models.Booking.user_id == current_user.id
    ).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Only allow cancelling pending or confirmed bookings
    if booking.status not in [models.BookingStatus.PENDING, models.BookingStatus.CONFIRMED]:
        raise HTTPException(status_code=400, detail="Only pending or confirmed bookings can be cancelled")
    
    booking.status = models.BookingStatus.CANCELLED
    db.commit()
    return {"message": "Booking cancelled successfully"}