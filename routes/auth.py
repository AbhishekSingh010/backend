from fastapi import FastAPI, HTTPException, Depends,APIRouter
from pydantic_models import LoginRequest,RegisterRequest

from db import get_connection

from utils.auth_utils import (
  hash_password,
  verify_password,
  create_access_token,
)

router=APIRouter()



@router.post("/register")
def user_register(data: RegisterRequest):
  username = data.username
  password = data.password
  conn=get_connection()
  cursor=conn.cursor()

  cursor.execute("SELECT * FROM users WHERE username=%s",(username,))
  if cursor.fetchone():
    cursor.close()
    conn.close()
    raise HTTPException(status_code=400,detail="Username already exists")
  
  hashed_password=hash_password(password)
  cursor.execute("INSERT INTO USERS (USERNAME,PASSWORD) VALUES (%s,%s)",(username,hashed_password))
  conn.commit()
  cursor.close()
  conn.close()
  return {"message":"User registered successfully"}
  
  
  

@router.post("/login")
def user_login(data: LoginRequest):
  username = data.username
  password = data.password

  conn=get_connection()
  cursor=conn.cursor()
  cursor.execute(
    "SELECT id,password FROM users WHERE username=%s",(username,)
  )
  user=cursor.fetchone()
  cursor.close()  
  conn.close()
  
  if not user :
    raise HTTPException(status_code=401,detail="Invalid username or password")
  
  user_id=user[0]
  hashed_password=user[1]
  if not verify_password(password,hashed_password):
    raise HTTPException(status_code=401,detail="Invalid username or password")
  
  access_token=create_access_token(user_id,username)
  return {"access_token":access_token,"token_type":"bearer"}








