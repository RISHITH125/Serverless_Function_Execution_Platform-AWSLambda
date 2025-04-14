from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
from execution_engine.core.pool_manager import WarmPoolManager
from app.controllers import auth, function , function_execution
from app.database.mongodb import create_indexes


config_path = Path(__file__).parent / "execution_engine_config.json"

with config_path.open("r", encoding="utf-8") as f:
    execution_engine_config = json.load(f)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(function.router)
app.include_router(function_execution.router)


@app.on_event("startup")
async def startup():
    await create_indexes()
    config =execution_engine_config
    app.state.pool= WarmPoolManager(config)    
    # await app.state.pool._initialize_pools()

@app.on_event("shutdown")
async def shutdown():
    await app.state.pool.shutdown()

@app.get("/hello")
async def read_root():
    return {"message": "Backend is working 🚀"}
