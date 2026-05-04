from fastapi import FastAPI, HTTPException, Depends,APIRouter

from utils.auth_utils import get_current_user



router=APIRouter()

@router.get("/profile")
def user_profile(user=Depends(get_current_user)):
  
  return {"message":f"Welcome {user['user_id']},{user['username']}!"}

