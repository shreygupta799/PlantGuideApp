# routes/plants.py
from fastapi import APIRouter, HTTPException
from configuration import secretENV
from schema.global_schema import PlantRequest, PlantResponse
from configuration.config import db
import google.generativeai as genai
import json

router = APIRouter()


@router.post("/plant", response_model=PlantResponse)
async def get_plant_info(plant_request: PlantRequest):
    plant_name = plant_request.name
    plant_data = db.client.global_database.plant_details.find_one({"name": plant_name})

    if plant_data:
        return PlantResponse(**plant_data)

    plant_info_template = """
    Provide comprehensive information about the plant {plant_name}. Include the following details:
    1. General description of the plant.
    2. The best sowing season for this plant.
    3. Step-by-step instructions on how to sow the seeds.
    4. Detailed care instructions for the plant.
    5. Any prerequisites or conditions that need to be met before sowing the seeds.

    Return the information in the following JSON format:
    {
        "name": "{plant_name}",
        "details": "General description of the plant",
        "sowing_season": "Best sowing season",
        "sowing_instructions": "Step-by-step instructions on how to sow the seeds",
        "care_instructions": "Detailed care instructions",
        "prerequisites": "Prerequisites or conditions that need to be met before sowing the seeds"
    }
    """

    genai.configure(api_key=secretENV.API_KEY)

    prompt = plant_info_template.format(plant_name=plant_name)

    model = genai.GenerativeModel(name='gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
    response = model.generate_content(prompt)
    json_data = json.loads(response.text)

    if json_data.status_code == 200:

        plant_info = {
            "name": plant_name,
            "details": json_data["details"],
            "sowing_season": json_data["sowing_season"],
            "sowing_instructions": json_data["sowing_instructions"],
            "care_instructions": json_data["care_instructions"],
            "prerequisites": json_data["prerequisites"]
        }
        db.client.global_database.plant_details.insert_one(plant_info)
        return PlantResponse(**plant_info)

    else:
        raise HTTPException(status_code=500, detail="Failed to get plant information ")


