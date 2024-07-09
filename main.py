from fastapi import FastAPI

from config.config import connect_to_mongo, close_mongo_connection

app=FastAPI()

@app.on_event("startup")
async def startup_db_client():
    connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    close_mongo_connection()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI application with MongoDB"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)