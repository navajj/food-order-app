from fastapi import FastAPI

from api.routers import customers, menu, orders, restaurants

app = FastAPI(title="Food Order API", root_path="/api")

app.include_router(restaurants.router)
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(customers.router)
