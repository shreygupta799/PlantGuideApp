
from fastapi import FastAPI
from configuration.config import connect_to_mongo, close_mongo_connection
from routes.plants import router as plant_router


app=FastAPI()

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_db_client():
   await close_mongo_connection()

app.include_router(plant_router, prefix="/api", tags=["plant"])


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI application with mongoDB"}




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)