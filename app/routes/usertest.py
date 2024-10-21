from fastapi import APIRouter, Depends
from app.dependencies.response_handler import ResponseHandler, get_response_handler
from app.schemes import Usertestreq
from app.schemes import Usertestres

router = APIRouter()


class UsertestRoute:
    @staticmethod
    @router.get("/usertest", response_model=Usertestres)
    async def index(
        data: Usertestreq,
        response_handler: ResponseHandler = Depends(get_response_handler)
    ):
        return response_handler.send_success_response(message="This is the index method of UsertestRoute")
