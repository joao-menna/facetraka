from fastapi import FastAPI, Form, UploadFile
from pydantic import BaseModel
from deepface import DeepFace
from typing import Annotated
import os

DISTANCE_THRESHOLD = 0.3
TEMP_DIR = "temp"
DATABASE = "database"
image_dir = lambda x: TEMP_DIR + f"/webcam{x}.png"

app = FastAPI()


class ProcessFaceInput(BaseModel):
    cam_index: int
    image: UploadFile


@app.post("/face/process")
async def process_face(body: Annotated[ProcessFaceInput, Form()]):
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(DATABASE, exist_ok=True)

    image_bytes = await body.image.read()
    image_path = image_dir(body.cam_index)

    with open(image_path, "wb") as file:
        file.write(image_bytes)

    recognized = DeepFace.find(
        img_path=image_path,
        db_path=DATABASE,
        enforce_detection=False,
        threshold=0.85,
        batched=True,
        silent=True,
    )

    similar_faces = []

    for i in recognized:
        for j in i:
            if j["distance"] < DISTANCE_THRESHOLD:
                similar_faces.append(j)

    return {
        "success": True,
        "allowed": len(similar_faces) > 0,
    }
