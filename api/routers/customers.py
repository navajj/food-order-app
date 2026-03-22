from asgiref.sync import sync_to_async
from fastapi import APIRouter, Depends, Request

from api.dependencies import get_current_customer
from api.schemas import CustomerOut, CustomerUpdate
from core.models import Customer

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/me/", response_model=CustomerOut)
async def get_profile(
    request: Request,
    customer: Customer = Depends(get_current_customer),
):
    return customer


@router.put("/me/", response_model=CustomerOut)
async def update_profile(
    data: CustomerUpdate,
    request: Request,
    customer: Customer = Depends(get_current_customer),
):
    if data.phone is not None:
        customer.phone = data.phone
    if data.address is not None:
        customer.address = data.address
    await sync_to_async(customer.save)()
    return customer
