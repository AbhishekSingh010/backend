
from fastapi import FastAPI
from routes import chat,user
from routes import auth
from routes import prediction
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "https://potato-frontend-xi.vercel.app",
                   "http://127.0.0.1:3000"],
    # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])

app.include_router(user.router, prefix="/user", tags=["User"])

app.include_router(prediction.router,prefix="/prediction",tags=["Prediction"])

app.include_router(chat.router, prefix="/Ai", tags=["Chat"])
