from asgiref.sync import sync_to_async
from fastapi import APIRouter, Depends, HTTPException, Request

from api.dependencies import get_current_user
from api.schemas import MenuItemCreate, MenuItemOut
from core.models import MenuItem, Restaurant

router = APIRouter(prefix="/menu", tags=["menu"])


async def _get_restaurant(restaurant_id: int) -> Restaurant:
    try:
        return await sync_to_async(Restaurant.objects.get)(pk=restaurant_id)
    except Restaurant.DoesNotExist:
        raise HTTPException(status_code=404, detail="Restaurant not found")


@router.get("/{restaurant_id}/items/", response_model=list[MenuItemOut])
async def list_menu_items(restaurant_id: int):
    await _get_restaurant(restaurant_id)
    items = await sync_to_async(list)(
        MenuItem.objects.filter(restaurant_id=restaurant_id, is_available=True)
    )
    return items


@router.post("/{restaurant_id}/items/", response_model=MenuItemOut, status_code=201)
async def create_menu_item(
    restaurant_id: int,
    data: MenuItemCreate,
    request: Request,
    user=Depends(get_current_user),
):
    is_staff = await sync_to_async(lambda: user.is_staff)()
    if not is_staff:
        raise HTTPException(status_code=403, detail="Staff only")
    restaurant = await _get_restaurant(restaurant_id)
    item = await sync_to_async(MenuItem.objects.create)(
        restaurant=restaurant,
        name=data.name,
        description=data.description,
        price=data.price,
        category=data.category,
        is_available=data.is_available,
    )
    return item


@router.put("/{restaurant_id}/items/{item_id}/", response_model=MenuItemOut)
async def update_menu_item(
    restaurant_id: int,
    item_id: int,
    data: MenuItemCreate,
    request: Request,
    user=Depends(get_current_user),
):
    is_staff = await sync_to_async(lambda: user.is_staff)()
    if not is_staff:
        raise HTTPException(status_code=403, detail="Staff only")
    await _get_restaurant(restaurant_id)
    try:
        item = await sync_to_async(MenuItem.objects.get)(
            pk=item_id, restaurant_id=restaurant_id
        )
    except MenuItem.DoesNotExist:
        raise HTTPException(status_code=404, detail="Menu item not found")

    item.name = data.name
    item.description = data.description
    item.price = data.price
    item.category = data.category
    item.is_available = data.is_available
    await sync_to_async(item.save)()
    return item


@router.delete("/{restaurant_id}/items/{item_id}/", status_code=204)
async def delete_menu_item(
    restaurant_id: int,
    item_id: int,
    request: Request,
    user=Depends(get_current_user),
):
    is_staff = await sync_to_async(lambda: user.is_staff)()
    if not is_staff:
        raise HTTPException(status_code=403, detail="Staff only")
    await _get_restaurant(restaurant_id)
    try:
        item = await sync_to_async(MenuItem.objects.get)(
            pk=item_id, restaurant_id=restaurant_id
        )
    except MenuItem.DoesNotExist:
        raise HTTPException(status_code=404, detail="Menu item not found")
    await sync_to_async(item.delete)()
