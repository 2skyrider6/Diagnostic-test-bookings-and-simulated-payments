from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from datetime import datetime
import random
from app import models, schemas
from app.db.session import get_db
from app.core.security import get_current_active_user

router = APIRouter()

# Simulated Payment Service
@router.post("/", response_model=schemas.PaymentRead)
def process_payment(
    payment: schemas.PaymentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Verify booking exists and belongs to user
    booking = db.query(models.Booking).filter(
        models.Booking.id == payment.booking_id,
        models.Booking.user_id == current_user.id
    ).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Verify payment doesn't already exist
    existing_payment = db.query(models.Payment).filter(models.Payment.booking_id == payment.booking_id).first()
    if existing_payment:
        raise HTTPException(status_code=400, detail="Payment already processed for this booking")
    
    # Verify booking is pending
    if booking.status != models.BookingStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending bookings can be paid")
    
    # Verify amount matches
    if payment.amount != booking.amount:
        raise HTTPException(status_code=400, detail="Payment amount does not match booking amount")
    
    # Create payment record
    db_payment = models.Payment(
        booking_id=payment.booking_id,
        user_id=current_user.id,
        amount=payment.amount,
        status=models.PaymentStatus.PENDING,
        transaction_id=str(uuid.uuid4())
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    # Simulate payment processing in background
    background_tasks.add_task(simulate_payment_processing, db_payment.id)
    
    return db_payment

def simulate_payment_processing(payment_id: int):
    # This would normally be a database session, but for simplicity in background task
    # we'll create a new session
    from app.db.session import SessionLocal
    import time
    
    db = SessionLocal()
    try:
        payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
        if not payment:
            return
        
        # Simulate processing delay
        time.sleep(2)
        
        # Simulate random success/failure (70% success rate)
        if random.random() < 0.7:
            payment.status = models.PaymentStatus.SUCCESS
            # Update booking status
            booking = db.query(models.Booking).filter(models.Booking.id == payment.booking_id).first()
            if booking:
                booking.status = models.BookingStatus.CONFIRMED
        else:
            payment.status = models.PaymentStatus.FAILED
            # Update booking status
            booking = db.query(models.Booking).filter(models.Booking.id == payment.booking_id).first()
            if booking:
                booking.status = models.BookingStatus.FAILED
        
        db.commit()
    except Exception as e:
        print(f"Error processing payment: {e}")
        db.rollback()
    finally:
        db.close()

# Payment Webhook - Idempotent
@router.post("/webhook/")
def payment_webhook(
    payment_update: schemas.PaymentUpdate,
    db: Session = Depends(get_db)
):
    # Find payment by transaction_id
    payment = db.query(models.Payment).filter(
        models.Payment.transaction_id == payment_update.transaction_id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Idempotency check: if payment already has final status, don't process
    if payment.status in [models.PaymentStatus.SUCCESS, models.PaymentStatus.FAILED]:
        # Return success without making changes
        return {"message": "Webhook processed (idempotent)"}
    
    # Update payment status
    payment.status = payment_update.status
    
    # Update associated booking status
    booking = db.query(models.Booking).filter(models.Booking.id == payment.booking_id).first()
    if booking:
        if payment_update.status == models.PaymentStatus.SUCCESS:
            booking.status = models.BookingStatus.CONFIRMED
        elif payment_update.status == models.PaymentStatus.FAILED:
            booking.status = models.BookingStatus.FAILED
    
    db.commit()
    
    return {"message": "Webhook processed successfully"}

# Get payment status
@router.get("/{payment_id}", response_model=schemas.PaymentRead)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    payment = db.query(models.Payment).filter(
        models.Payment.id == payment_id,
        models.Payment.user_id == current_user.id
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment