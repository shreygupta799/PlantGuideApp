from pydantic import BaseModel

class PlantRequest(BaseModel):
    name: str

class PlantResponse(BaseModel):
    name: str
    details: str
    sowing_season: str
    sowing_instructions: str
    care_instructions: str
    prerequisites: str