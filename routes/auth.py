import logging
from fastapi import  Depends, HTTPException, status,APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from utility_function import authenticate_user, create_access_token, get_current_user, get_password_hash, verify_password   
from schema.auth_schema import Register, UserResponse, Token, Saved, UesrRequest
from schema.global_schema import PlantRequest
from configuration.config import db

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info(f"User with username {form_data.username} is trying to login")
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await create_access_token(
        data={"sub": user["username"]})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=Saved)
async def register_user(user: Register):
    hashed_password = get_password_hash(user.password)
    user_data = {
        "username": user.username,
        "full_name": user.full_name,
        "password": hashed_password,
        "saved_plants": [],
    }
    db.client.global_database.saved_plant.insert_one(user_data)
    return user_data


@router.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.post("/save_plant")
async def save_plant(plant: PlantRequest, current_user: dict = Depends(get_current_user)):
    #plant_dict = plant.dict()
    db.client.global_database.saved_plant.update_one(
        {"username": current_user["username"]},
        {"$addToSet": {"saved_plants": plant}}
    )
    return {"message": "Plant information saved successfully"}


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)