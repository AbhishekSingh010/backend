from fastapi import HTTPException,  Depends
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta,timezone
import hashlib


from dotenv import load_dotenv
import os

load_dotenv()
# config
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60



security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# utility functions
def hash_password(password:str):
  hashed = hashlib.sha256(password.encode()).hexdigest()
  return pwd_context.hash(hashed) 

def verify_password(plain_password:str,hashed_password:str):
  hashed = hashlib.sha256(plain_password.encode()).hexdigest()
  return pwd_context.verify(hashed, hashed_password)

def create_access_token(user_id,username:str):
  expire=datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  payload={"sub":user_id,"username":username,"exp":expire}
  return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
  token=credentials.credentials
  try:
    payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    user_id=payload.get("sub")
    username=payload.get("username")
    if username is None and user_id is None:
      raise HTTPException(status_code=401,detail="Invalid token")
    return {"user_id": user_id, "username": username}
  except JWTError:
    raise HTTPException(status_code=401,detail="Invalid token")
  
  


  