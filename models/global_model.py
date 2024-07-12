from pydantic import BaseModel


class Plant(BaseModel):
    name: str
    details: str
    sowing_season: str
    sowing_instructions: str
    care_instructions: str
    prerequisites: str
