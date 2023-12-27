from pydantic import BaseModel
from typing import Any, Optional, Union, TypeVar


class HassMeta(BaseModel):
    version: str
    server: str


MessageType = TypeVar("MessageType")


class HassError(BaseModel):
    code: str
    message: str
    translation_key: Optional[str]
    translation_domain: Optional[str]
    translation_placeholders: Optional[dict[str, str]]


class Message[MessageType](BaseModel):
    id: int
    type: str
    success: bool
    data: Union[MessageType, HassError]

    @classmethod
    def create(cls, data: dict) -> "Message":
        if data["type"] == "result":
            if data["success"]:
                return Message[Any](
                    id=data["id"],
                    type=data["type"],
                    success=data["success"],
                    data=data["result"],
                )
            else:
                return Message[Any](
                    id=data["id"],
                    type=data["type"],
                    success=data["success"],
                    data=data["error"],
                )
        elif data["type"] == "event":
            return Message[Any](
                id=data["id"],
                type=data["type"],
                success=True,
                data=data["event"],
            )
        else:
            return Message[Any](id=-1, type="", success=False, data=None)
