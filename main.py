import uvicorn
import logging

from fastapi import FastAPI, Depends

from controllers.users import create_user, login
from models.users import User
from models.login import Login

from utils.security import validate_token, validate_admin
from utils.mongodb import test_connection


from routes.catalogtypes import router as catalogtypes_router
from routes.catalogs import router as catalogs_router
from routes.box_details import router as box_details_router
from routes.order_statuses import router as order_statuses_router
from routes.orders import router as orders_router
from routes.order_details import router as order_details_router
from routes.inventory import router as inventory_router


app = FastAPI()

app.include_router(catalogtypes_router)
app.include_router(catalogs_router)
app.include_router(box_details_router)
app.include_router(order_statuses_router)
app.include_router(orders_router)
app.include_router(order_details_router)
app.include_router(inventory_router)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def read_root():
    return {"version": "0.0.0"}

@app.get("/health")
def health_check():
    try:
        return {
            "status": "healthy",
            "timestamp": "2025-08-10",
            "service": "kakarikostore-api",
            "environment": "production"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/ready")
def rediness_check():
    try:
        db_status = test_connection()
        return{
            "status" : "ready" if db_status else "not_ready",
            "database": "connected" if db_status else "disconnected",
            "service": "kakarikostore-api"
        }
    except Exception as e:
        return{"status": "not_ready", "error": str(e)}

@app.post("/users")
async def create_user_endpoint(user: User) -> User:
    return await create_user(user)

@app.post("/login")
async def login_access(l: Login) -> dict:
    return await login(l)


@app.get("/exampleadmin")
async def example_admin(admin_data: dict = Depends(validate_admin)):
    return {
        "message": "This is an example admin endpoint.",
        "admin": admin_data.get("role")
    }

@app.get("/exampleuser")
async def example_user(user_data: dict = Depends(validate_token)):
    return {
        "message": "This is an example user endpoint.",
        "email": user_data.get("email")
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
