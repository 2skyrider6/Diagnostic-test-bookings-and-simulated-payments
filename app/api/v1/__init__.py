from fastapi import APIRouter

from .endpoints import auth, centres_tests, bookings, payments

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(centres_tests.router, prefix="/centres-tests", tags=["centres-tests"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])