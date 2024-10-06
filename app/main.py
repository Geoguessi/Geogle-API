from fastapi import FastAPI,HTTPException
from app.routers import place, province, provinceDashboard, province_place
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(place.router)
app.include_router(province.router)
app.include_router(provinceDashboard.router)
app.include_router(province_place.router)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000", 
    "https://geogle.kitton.dev", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def main():
    return {"message": "Hello World"}