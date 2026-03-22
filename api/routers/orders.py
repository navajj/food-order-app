from decimal import Decimal

from asgiref.sync import sync_to_async
from django.db import transaction
from fastapi import APIRouter, Depends, HTTPException, Request

from api.dependencies import get_current_customer, get_current_user
from api.schemas import OrderCreate, OrderOut, OrderItemOut, OrderStatusUpdate
from core.models import Customer, MenuItem, Order, OrderItem, Restaurant

router = APIRouter(prefix="/orders", tags=["orders"])


def _serialize_order(order: Order, items: list[OrderItem]) -> dict:
    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "restaurant_id": order.restaurant_id,
        "restaurant_name": order.restaurant.name,
        "status": order.status,
        "total": order.total,
        "notes": order.notes,
        "items": [
            {
                "id": item.id,
                "menu_item_id": item.menu_item_id,
                "menu_item_name": item.menu_item.name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
            }
            for item in items
        ],
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }


@router.post("/", response_model=OrderOut, status_code=201)
async def create_order(
    data: OrderCreate,
    request: Request,
    customer: Customer = Depends(get_current_customer),
):
    try:
        restaurant = await sync_to_async(Restaurant.objects.get)(
            pk=data.restaurant_id, is_active=True
        )
    except Restaurant.DoesNotExist:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    if not data.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")

    # Fetch menu items and calculate total
    menu_item_ids = [i.menu_item_id for i in data.items]
    menu_items_qs = await sync_to_async(list)(
        MenuItem.objects.filter(
            pk__in=menu_item_ids, restaurant=restaurant, is_available=True
        )
    )
    menu_items_map = {mi.id: mi for mi in menu_items_qs}

    for item_data in data.items:
        if item_data.menu_item_id not in menu_items_map:
            raise HTTPException(
                status_code=400,
                detail=f"Menu item {item_data.menu_item_id} not found or unavailable",
            )

    total = Decimal("0")
    for item_data in data.items:
        mi = menu_items_map[item_data.menu_item_id]
        total += mi.price * item_data.quantity

    @sync_to_async
    def _create():
        with transaction.atomic():
            order = Order.objects.create(
                customer=customer,
                restaurant=restaurant,
                total=total,
                notes=data.notes,
            )
            order_items = []
            for item_data in data.items:
                mi = menu_items_map[item_data.menu_item_id]
                order_items.append(
                    OrderItem(
                        order=order,
                        menu_item=mi,
                        quantity=item_data.quantity,
                        unit_price=mi.price,
                    )
                )
            OrderItem.objects.bulk_create(order_items)
            # Refresh to get created items with IDs
            created_items = list(
                OrderItem.objects.filter(order=order).select_related("menu_item")
            )
            # Access restaurant name while in sync context
            _ = order.restaurant.name
            return order, created_items

    order, items = await _create()
    return _serialize_order(order, items)


@router.get("/", response_model=list[OrderOut])
async def list_orders(
    request: Request,
    customer: Customer = Depends(get_current_customer),
):
    @sync_to_async
    def _fetch():
        orders = list(
            Order.objects.filter(customer=customer).select_related("restaurant")
        )
        result = []
        for order in orders:
            items = list(
                OrderItem.objects.filter(order=order).select_related("menu_item")
            )
            result.append(_serialize_order(order, items))
        return result

    return await _fetch()


@router.get("/{order_id}/", response_model=OrderOut)
async def get_order(
    order_id: int,
    request: Request,
    user=Depends(get_current_user),
):
    @sync_to_async
    def _fetch():
        try:
            order = Order.objects.select_related("restaurant", "customer").get(
                pk=order_id
            )
        except Order.DoesNotExist:
            return None, None, False

        is_owner = order.customer.user_id == user.id
        is_staff = user.is_staff
        if not is_owner and not is_staff:
            return order, None, False

        items = list(
            OrderItem.objects.filter(order=order).select_related("menu_item")
        )
        return order, items, True

    order, items, authorized = await _fetch()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if not authorized:
        raise HTTPException(status_code=403, detail="Not authorized")
    return _serialize_order(order, items)


@router.patch("/{order_id}/status/", response_model=OrderOut)
async def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    request: Request,
    user=Depends(get_current_user),
):
    is_staff = await sync_to_async(lambda: user.is_staff)()
    if not is_staff:
        raise HTTPException(status_code=403, detail="Staff only")

    valid_statuses = [c[0] for c in Order.Status.choices]
    if data.status not in valid_statuses:
        raise HTTPException(
            status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}"
        )

    @sync_to_async
    def _update():
        try:
            order = Order.objects.select_related("restaurant").get(pk=order_id)
        except Order.DoesNotExist:
            return None, None
        order.status = data.status
        order.save(update_fields=["status", "updated_at"])
        items = list(
            OrderItem.objects.filter(order=order).select_related("menu_item")
        )
        return order, items

    order, items = await _update()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return _serialize_order(order, items)
