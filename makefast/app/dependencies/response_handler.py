from fastapi import status
from pydantic import BaseModel
from starlette.responses import JSONResponse
from typing import Union


class ResponseHandler:
    """
    A handler class for generating consistent JSON responses.
    """

    def send_success_response(
            self,
            data: Union[list, dict, BaseModel] = None,
            message: str = 'Request successful',
            status_code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        """
        Generate a JSON response for a successful request.

        Args:
            data (Union[list, dict, BaseModel], optional): The data to include in the response.
            message (str, optional): The message to include in the response. Defaults to 'Success!'.
            status_code (int, optional): The HTTP status code for the response. Defaults to 200.

        Returns:
            JSONResponse: The formatted JSON response.
        """
        return self._send_json_response(True, message, data, status_code)

    def send_unprocessable_response(
            self,
            message: str = 'Unprocessable entity',
            data: Union[list, dict, BaseModel] = None,
            status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY
    ) -> JSONResponse:
        """
        Generate a JSON response for an unprocessable entity request.

        Args:
            message (str, optional): The message to include in the response. Defaults to 'Unprocessable Entity'.
            data (Union[list, dict, BaseModel], optional): The data to include in the response.
            status_code (int, optional): The HTTP status code for the response. Defaults to 422.

        Returns:
            JSONResponse: The formatted JSON response.
        """
        return self._send_json_response(False, message, data, status_code)

    def send_error_response(
            self,
            message: str = 'Internal server error',
            data: Union[list, dict, BaseModel] = None,
            status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ) -> JSONResponse:
        """
        Generate a JSON response for an erroneous request.

        Args:
            message (str, optional): The message to include in the response. Defaults to 'Error!'.
            data (Union[list, dict, BaseModel], optional): The data to include in the response.
            status_code (int, optional): The HTTP status code for the response. Defaults to 400.

        Returns:
            JSONResponse: The formatted JSON response.
        """
        return self._send_json_response(False, message, data, status_code)

    def send_unauthenticated_response(
            self,
            message: str = 'Unauthenticated',
            data: Union[list, dict, BaseModel] = None,
            status_code: int = status.HTTP_401_UNAUTHORIZED
    ) -> JSONResponse:
        """
        Generate a JSON response for an unauthenticated request.

        Args:
            message (str, optional): The message to include in the response. Defaults to 'Unauthenticated'.
            data (Union[list, dict, BaseModel], optional): The data to include in the response.
            status_code (int, optional): The HTTP status code for the response. Defaults to 401.

        Returns:
            JSONResponse: The formatted JSON response.
        """
        return self._send_json_response(False, message, data, status_code)

    def send_expired_response(
            self,
            message: str = 'Expired or already verified',
            data: Union[list, dict, BaseModel] = None,
            status_code: int = status.HTTP_410_GONE
    ) -> JSONResponse:
        """
        Generate a JSON response for an expired or already verified request.

        Args:
            message (str, optional): The message to include in the response. Defaults to 'Unauthenticated'.
            data (Union[list, dict, BaseModel], optional): The data to include in the response.
            status_code (int, optional): The HTTP status code for the response. Defaults to 401.

        Returns:
            JSONResponse: The formatted JSON response.
        """
        return self._send_json_response(False, message, data, status_code)

    def send_server_busy_response(
            self,
            message: str = 'Too many requests',
            data: Union[list, dict, BaseModel] = None,
            status_code: int = status.HTTP_429_TOO_MANY_REQUESTS
    ) -> JSONResponse:
        """
        Generate a JSON response for a server busy request.

        Args:
            message (str, optional): The message to include in the response. Defaults to 'Unauthenticated'.
            data (Union[list, dict, BaseModel], optional): The data to include in the response.
            status_code (int, optional): The HTTP status code for the response. Defaults to 401.

        Returns:
            JSONResponse: The formatted JSON response.
        """
        return self._send_json_response(False, message, data, status_code)

    def send_access_denied_response(
            self,
            message: str = 'Access denied',
            data: Union[list, dict, BaseModel] = None,
            status_code: int = status.HTTP_403_FORBIDDEN
    ) -> JSONResponse:
        """
        Generate a JSON response for access denied response.

        Args:
            message (str, optional): The message to include in the response. Defaults to 'Unauthenticated'.
            data (Union[list, dict, BaseModel], optional): The data to include in the response.
            status_code (int, optional): The HTTP status code for the response. Defaults to 401.

        Returns:
            JSONResponse: The formatted JSON response.
        """
        return self._send_json_response(False, message, data, status_code)

    @staticmethod
    def _send_json_response(
            success: bool,
            message: str,
            data: Union[list, dict, BaseModel] = None,
            status_code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        """
        Generate a JSON response.

        Args:
            success (bool): Indicates if the request was successful.
            message (str): The message to include in the response.
            data (Union[list, dict, BaseModel], optional): The data to include in the response.
            status_code (int, optional): The HTTP status code for the response. Defaults to 200.

        Returns:
            JSONResponse: The formatted JSON response.
        """
        response_data = {
            "success": success,
            "message": message,
            "data": data,
        }
        return JSONResponse(content=response_data, status_code=status_code)


def get_response_handler():
    """
    Dependency function to retrieve the ResponseHandler instance.

    Returns:
        ResponseHandler: The response handler instance.
    """
    response_handler = ResponseHandler()
    return response_handler
