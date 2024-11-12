from fastapi import APIRouter, Depends, HTTPException, status
from database import users_collection
from models import User, UserInDB
from schemas import SignupRequest, LoginRequest, ProfileResponse
from auth.jwt_handler import create_access_token
from auth.oauth2 import get_current_user
from passlib.context import CryptContext

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/signup")
async def signup(request: SignupRequest):
    user = users_collection.find_one({"email": request.email})
    username = users_collection.find_one({"username": request.username})
    if user or username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered." if user else "Username is already taken."
        )

    hashed_password = pwd_context.hash(request.password)
    user_data = UserInDB(**request.dict(), hashed_password=hashed_password).dict()
    user_data.pop("password", None)
    users_collection.insert_one(user_data)
    return {"msg": "User registered successfully"}

@router.post("/login")
async def login(request: LoginRequest):
    user = users_collection.find_one({"email": request.email})
    if not user or not pwd_context.verify(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token(data={"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/profile", response_model=ProfileResponse)
async def profile(current_user: User = Depends(get_current_user)):
    user =  users_collection.find_one({"email": current_user["sub"]})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"username": user["username"], "email": user["email"]}
