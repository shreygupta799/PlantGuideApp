from fastapi import FastAPI
from configuration.config import connect_to_mongo, close_mongo_connection
from routes.plants import routerPlant
from routes.auth import router

app = FastAPI()


app.include_router(routerPlant,tags=["plants"])
app.include_router(router, tags=["auth"])

@app.on_event("startup")
async def startup_db_client():
    connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    close_mongo_connection()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000,reload=True, debug=True)
