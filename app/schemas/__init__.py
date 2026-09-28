from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models import UserRole, BookingStatus, PaymentStatus

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserRead(UserBase):
    id: int
    is_active: bool
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Diagnostic Centre Schemas
class CentreBase(BaseModel):
    name: str
    location: str

class CentreCreate(CentreBase):
    pass

class CentreRead(CentreBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Diagnostic Test Schemas
class TestBase(BaseModel):
    name: str
    price: float

class TestCreate(TestBase):
    centre_id: int

class TestRead(TestBase):
    id: int
    centre_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Booking Schemas
class BookingBase(BaseModel):
    test_id: int
    appointment_datetime: datetime

class BookingCreate(BookingBase):
    pass

class BookingRead(BookingBase):
    id: int
    user_id: int
    centre_id: int
    amount: float
    status: BookingStatus
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    appointment_datetime: Optional[datetime] = None

# Payment Schemas
class PaymentBase(BaseModel):
    amount: float

class PaymentCreate(PaymentBase):
    booking_id: int

class PaymentRead(PaymentBase):
    id: int
    booking_id: int
    user_id: int
    status: PaymentStatus
    transaction_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class PaymentUpdate(BaseModel):
    status: PaymentStatus
    transaction_id: Optional[str] = None