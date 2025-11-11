from fastapi import FastAPI, Form, UploadFile, Query, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from deepface import DeepFace
from typing import Annotated
import hashlib
import uuid
import json
import os

DISTANCE_THRESHOLD = 0.3
TEMP_DIR = "temp"
DATABASE = "database"
image_dir = lambda x: TEMP_DIR + f"/webcam{x}.png"
allowed_people: list[dict[str, str]] = []

app = FastAPI()
app.mount("/game", StaticFiles(directory="public"), name="public")


class ProcessFaceInput(BaseModel):
    cam_index: int
    image: UploadFile


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        allowed_people.clear()

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


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

    players = []

    for i, faces in enumerate(recognized):
        player = {
            "player_number": i,
            "similar_faces": [],
            "name": "",
            "code": "",
            "id": uuid.uuid4().hex.replace("-", ""),
        }

        for face in faces:
            if face["distance"] < DISTANCE_THRESHOLD:
                player["similar_faces"].append(face)

        if player["similar_faces"]:
            last_face = player["similar_faces"][-1]
            name = (
                str(last_face['identity'])
                .replace("\\", "/")
                .replace(".png", "")
                .replace("database/", "")
            )
            code = hashlib.sha256(name.encode("utf-8")).hexdigest()

            player["name"] = name
            player["code"] = code

            if not any(p["code"] == code for p in allowed_people):
                allowed_people.append({
                    "id": player["id"],
                    "code": code,
                    "name": name,
                })
            else:
                print(f"could not insert person: {player["name"]}, it already exists")

        players.append(player)

    allowed = any(len(p["similar_faces"]) > 0 for p in players)

    mapped_players = []
    for p in players:
        mapped_players.append({
            "player_number": p["player_number"] + 1,
            "name": p["name"],
            "code": p["code"],
            "id": p["id"],
        })

    return {
        "success": True,
        "allowed": allowed,
        "players": mapped_players,
    }


@app.get("/gate/open")
async def open_gate(connection_id: Annotated[str, Query()]):
    found_person = None

    for person in allowed_people:
        if connection_id == person["id"]:
            found_person = person

    if not found_person:
        return {
            "success": False,
            "message": "person not allowed"
        }

    json_message = json.dumps({
        "event": "connect",
        "status": "connected",
        "player_name": person["name"],
    })

    await manager.broadcast(json_message)

    return { "success": True, "name": person["name"] }


@app.websocket("/gate-ws")
async def gate_websocket(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            winner = tictactoe_loop(data)

            if not not winner:
                manager.disconnect(websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"")


# 1 2 3
# 4 5 6
# 7 8 9
winner_grid = [
    (1, 2, 3), (4, 5, 6), (7, 8, 9),  # lines
    (1, 4, 7), (2, 5, 8), (3, 6, 9),  # columns
    (1, 5, 9), (3, 5, 7)              # diagonals
]

def tictactoe_loop(data: dict[int, str]):
    try:
        data = { int(k): v for k, v in data.items() }
    except Exception:
        pass

    for a, b, c in winner_grid:
        if (data[a] == data[b] == data[c]) != '':
            body_json = json.dumps({
                "finished": True,
                "winner": data[a]
            })
            manager.broadcast(body_json)
            return data[a]

    body_json = json.dumps({
        "finished": False
    })
    manager.broadcast(body_json)
    return None
