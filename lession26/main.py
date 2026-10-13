from contextlib import asynccontextmanager
 
from fastapi import FastAPI
 
from database import init_db
from routers import categories, recipes
 
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
 
 
app = FastAPI(title="Online Recipe Book API", lifespan=lifespan)
app.include_router(categories.router)
app.include_router(recipes.router)
 
 
@app.get("/")
def root():
    return {"message": "Online Recipe Book API is running"}