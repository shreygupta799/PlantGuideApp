import base64
import logging
import re
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import ExpiredSignatureError, jwt, exceptions as jwt_exceptions
from datetime import datetime, timedelta
from passlib.context import CryptContext
from configuration import secretENV
from configuration.config import db
from schema.auth_schema import Saved




pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = secretENV.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Utility functions
def verify_password(plain_password:str, hashed_password:str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password:str):
    return pwd_context.hash(password)


# Auth functions
async def authenticate_user(username: str, password: str):
    user =await db.client.global_database.saved_plant.find_one({"username": username})
    if not user or not verify_password(password, user['password']):
        return False
    return user


async def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire_minutes = int(secretENV.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})    
    encoded_jwt = jwt.encode(to_encode, secretENV.SECRET_KEY, algorithm=secretENV.ALGORITHM)
    return encoded_jwt


# Dependency to get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    expired_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    logging.info(f"Received token: {token}")
    token = token.replace("Bearer ", "", 1)

# Validate token format
    if not re.match(r'^[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+$', token):
        logging.error("Invalid token format")
        raise credentials_exception

# Attempt to decode each part for debugging
    parts = token.split('.')
    for part in parts:
        try:
            decoded_part = base64.urlsafe_b64decode(part + "==")  # Padding might be required
            logging.info(f"Decoded part: {decoded_part}")
        except Exception as e:
            logging.error(f"Error decoding part: {e}")
            raise credentials_exception

    try:
        logging.info(f"Decoding token: {token}")
        payload = jwt.decode(token, secretENV.SECRET_KEY, algorithms=[secretENV.ALGORITHM])
        logging.debug(f"Decoded JWT payload: {payload}")
        username: str = payload.get("sub")
        if username is None:
            logging.error("Username not found in token payload")
            raise credentials_exception
    except ExpiredSignatureError:
        logging.error("Token has expired")
        raise expired_token_exception    
    except jwt_exceptions.JWTError as e:
        logging.error(f"JWT decoding error: {e}")
        raise credentials_exception
    user = await db.client.global_database.saved_plant.find_one({"username": username})
    if user is None:
        logging.error(f"User not found in database for username: {username}")
        raise credentials_exception
    
    return Saved(username=user['username'], saved_plant=user['saved_plants'], full_name=user['full_name'], password=user['password'])

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

