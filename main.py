import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from api.handlers import user_router
from api.login_handler import login_router

app = FastAPI(title="educational-portal")

main_api_router = APIRouter()

main_api_router.include_router(user_router, prefix="/user", tags=["user"])
main_api_router.include_router(login_router, prefix="/login", tags=["login"])
main_api_router.include_router(login_router, prefix="/add_task", tags=["add_task"])
app.include_router(main_api_router)

if __name__ == "__main__":
    # run app on the host and port
    uvicorn.run(app, host="0.0.0.0", port=8000)
