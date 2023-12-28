from pydantic import BaseModel
from typing import Any, Literal, Optional, Union, TypeVar
from typing_extensions import TypedDict


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


class HassEntityAttributes(TypedDict):
    friendly_name: Optional[str]
    icon: Optional[str]
    unit_of_measurement: Optional[str]
    entity_picture: Optional[str]
    supported_features: Optional[int]
    hidden: Optional[bool]
    assumed_state: Optional[bool]
    device_class: Optional[str]
    state_class: Optional[str]
    restored: Optional[bool]


class HassEntityContext(TypedDict):
    id: str
    parent_id: Optional[str]
    user_id: Optional[str]


class HassEntity(TypedDict):
    entity_id: str
    state: Any
    attributes: HassEntityAttributes
    last_changed: str
    last_updated: str
    context: HassEntityContext


class HassServiceField(TypedDict):
    name: Optional[str]
    description: str
    example: Any


class HassService(TypedDict):
    name: Optional[str]
    description: str
    fields: dict[str, HassServiceField]


class HassServiceTarget(TypedDict):
    entity_id: Optional[Union[list[str], str]]
    device_id: Optional[Union[list[str], str]]
    area_id: Optional[Union[list[str], str]]


class HassUnits(TypedDict):
    length: str
    mass: str
    volume: str
    temperature: str
    pressure: str
    wind_speed: str
    accumulated_precipitation: str


class HassConfig(TypedDict):
    latitude: float
    longitude: float
    elevation: float
    unit_system: HassUnits
    location_name: str
    time_zone: str
    components: list[str]
    config_dir: str
    allowlist_external_dirs: list[str]
    allowlist_external_urls: list[str]
    version: str
    config_source: str
    recovery_mode: bool
    safe_mode: bool
    state: Literal["NOT_RUNNING", "STARTING", "RUNNING", "STOPPING", "FINAL_WRITE"]
    external_url: Union[str, None]
    internal_url: Union[str, None]
    currency: str
    country: Union[str, None]
    language: str


class HassPanel(TypedDict):
    component_name: str
    icon: Union[str, None]
    title: Union[str, None]
    config: Union[dict, None]
    url_path: str
    require_admin: bool
    config_panel_domain: Union[str, None]


class HassEvent(TypedDict):
    event_type: str
    data: dict[str, Any]


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
