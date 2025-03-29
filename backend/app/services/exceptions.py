from typing import Any

from pydantic_core import ErrorDetails, to_jsonable_python


class ServiceError(Exception):
    pass


class NotFoundError(ServiceError):
    def __init__(self, *, input_data: Any = None, message: str = "Not found") -> None:
        self.message = message
        self.input_data = input_data

    def errors(self) -> list[ErrorDetails]:
        return [
            ErrorDetails(type="not_found", msg=self.message, loc=("path",), input=to_jsonable_python(self.input_data))
        ]
