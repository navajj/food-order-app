from asgiref.sync import sync_to_async
from fastapi import APIRouter, HTTPException

from api.schemas import RestaurantOut
from core.models import Restaurant

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.get("/", response_model=list[RestaurantOut])
async def list_restaurants():
    restaurants = await sync_to_async(list)(
        Restaurant.objects.filter(is_active=True)
    )
    return restaurants


@router.get("/{restaurant_id}/", response_model=RestaurantOut)
async def get_restaurant(restaurant_id: int):
    try:
        restaurant = await sync_to_async(Restaurant.objects.get)(pk=restaurant_id)
    except Restaurant.DoesNotExist:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant
