from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import auth, function
from app.database.mongodb import create_indexes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(function.router)

@app.on_event("startup")
async def startup():
    await create_indexes()

@app.get("/hello")
async def read_root():
    return {"message": "Backend is working 🚀"}
