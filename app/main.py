from fastapi import FastAPI,HTTPException
from app.routers import place, province, provinceDashboard, province_place


app = FastAPI()

app.include_router(place.router)
app.include_router(province.router)
app.include_router(provinceDashboard.router)
app.include_router(province_place.router)

