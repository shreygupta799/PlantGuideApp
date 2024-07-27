from fastapi import APIRouter, HTTPException
from configuration import secretENV
from schema.global_schema import PlantRequest, PlantResponse
from configuration.config import db
import google.generativeai as genai
import json
import logging




routerPlant = APIRouter()


@routerPlant.get("/")
async def read_root():
    logger.info("Root endpoint called")
    print("Roots endpoint called")
    return {"message": "Welcome to the FastAPI application with MongoDB"}


@routerPlant.post("/plant", response_model=PlantResponse)
async def get_plant_info(plant_request: PlantRequest):
    plant_name = plant_request.name
    logger.info(f"Received request for plant: {plant_name}")

    plant_data = await db.client.global_database.plant_details.find_one({"name": plant_name})

    if plant_data:
        logger.info(f"Plant {plant_name} found in database: {plant_data}")
        return PlantResponse(**plant_data)
    logger.info(f"Plant {plant_name} not found in database: {plant_data}")

    plant_info_template = """
    Provide comprehensive information about the plant {plant_name}. Include the following details:
    1. General description of the plant.
    2. The best sowing season for this plant.
    3. Step-by-step instructions on how to sow the seeds.
    4. Detailed care instructions for the plant.
    5. Any prerequisites or conditions that need to be met before sowing the seeds.

    Return the information in the following dictionary format:
    {{
        "name": "plant_name",
        "details": "General description of the plant",
        "sowing_season": "Best sowing season",
        "sowing_instructions": "Step-by-step instructions on how to sow the seeds",
        "care_instructions": "Detailed care instructions",
        "prerequisites": "Prerequisites or conditions that need to be met before sowing the seeds"
    }}
    """

    genai.configure(api_key=secretENV.API_KEY)

    prompt = plant_info_template.format(plant_name=plant_name)

    model = genai.GenerativeModel('gemini-1.5-flash',generation_config={"response_mime_type": "application/json"})
    response =  model.generate_content(prompt)

    #try:
    response = json.loads(response.text)
    #except json.JSONDecodeError as e:
        #logger.error(f"Failed to decode JSON response: {e}")
        #raise HTTPException(status_code=500, detail="Failed to decode response from GeminiAI")

    
    logger.info(f"Received response from GeminiAI for plant: {plant_name}")
    logger.info(f"Response: {response}")
    plant_info = {
            "name": plant_name,
            "details": response["details"],
            "sowing_season": response["sowing_season"],
            "sowing_instructions": response["sowing_instructions"],
            "care_instructions": response["care_instructions"],
            "prerequisites": response["prerequisites"]
        }
    await db.client.global_database.plant_details.insert_one(plant_info)
    logger.info(f"Inserted plant information for {plant_name} into database")
    return PlantResponse(**plant_info)


@routerPlant.get("/funfact")
async def get_fun_fact():
    
    # Create a prompt for the Gemini model
    funfact_template = """
    Generate a fun fact about plantation, plants, or farming. The fun fact should be concise and informative, ideally two or three lines long.
    """
    
    genai.configure(api_key=secretENV.API_KEY)


    model = genai.GenerativeModel('gemini-1.5-flash',generation_config={"response_mime_type": "application/json"})
    response =  model.generate_content(funfact_template)

    #try:
    response = json.loads(response.text)
    # Log the generated fun fact
    logger.info(f"Generated fun fact: {response}")
    
    return {"fun_fact": response}
    
      
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)