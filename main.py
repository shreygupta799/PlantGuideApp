from fastapi import FastAPI
from configuration.config import connect_to_mongo, close_mongo_connection
from routes.plants import router

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    close_mongo_connection()

app.include_router(router, prefix="/api", tags=["plants"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
