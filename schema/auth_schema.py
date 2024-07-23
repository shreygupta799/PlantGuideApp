from pydantic import BaseModel
from typing import List
from schema.global_schema import PlantRequest

class UserResponse(BaseModel):
    username: str
    password: str


class UesrRequest(BaseModel):
    username: str
    password: str
    
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class Saved(BaseModel):
    username: str
    saved_plant: List[str]
    password:str
    full_name:str
    
class Register(BaseModel):
    username: str
    full_name: str
    password: str