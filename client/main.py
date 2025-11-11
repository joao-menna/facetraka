from cv2 import VideoCapture, imwrite
from time import sleep
import requests
import dotenv
import os

dotenv.load_dotenv()

TEMP_DIR = "temp"
WEBCAM_IMAGE = TEMP_DIR + "/webcam.png"
WAIT_TIME = 3.0

server_url = os.getenv("SERVER_URL")

def main():
    os.makedirs(TEMP_DIR, exist_ok=True)

    cam = VideoCapture(0)

    if not server_url:
        print("client needs to have a SERVER_URL")
        exit(1)

    while True:
        print("trying to read camera")
        ret, frame = cam.read()

        if ret:
            print("read camera successfully")
            imwrite(WEBCAM_IMAGE, frame)
            check_face()
        else:
            print("Failed to capture image.")

        sleep(WAIT_TIME)


def check_face():
    files = { "image": open(WEBCAM_IMAGE, "rb") }
    data = { "cam_index": 0 }
    response = requests.post(f"{server_url}/face/process", data=data, files=files)

    process_json = response.json()

    if not process_json["allowed"]:
        print("face(s) not allowed")
        return

    for player in process_json["players"]:
        if not player["code"]:
            continue

        player_id = player["id"]
        response = requests.get(f"{server_url}/gate/open?connection_id={player_id}")

        gate_response = response.json()

        if not gate_response["success"]:
            return

        name = gate_response["name"]
        print(f"player {name} connected!")


if __name__ == "__main__":
    main()
