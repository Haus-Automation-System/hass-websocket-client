from pydantic import BaseModel


class HassMeta(BaseModel):
    version: str
    server: str
