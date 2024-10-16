from typing import Dict, Any
from fastapi import APIRouter, Depends
from app.dependencies.response_handler import ResponseHandler, get_response_handler
from app.models.user import User
    
router = APIRouter()
    
    
class UserRoute:
    @staticmethod
    @router.get("/user", response_model=Dict[str, Any])
    async def index(response_handler: ResponseHandler = Depends(get_response_handler)):
        print(await User.all())
        return response_handler.send_success_response(message="This is the index method of UserRoute")
