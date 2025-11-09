from deepface import DeepFace
from cv2 import VideoCapture, imwrite
from time import sleep
import os

TEMP_DIR = "temp"
WEBCAM_IMAGE = TEMP_DIR + "/webcam.png"
DATABASE = "database"

def main():
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(DATABASE, exist_ok=True)

    cam = VideoCapture(0)

    while True:
        ret, frame = cam.read()

        if ret:
            imwrite(WEBCAM_IMAGE, frame)
            recognized = DeepFace.find(
                img_path=WEBCAM_IMAGE,
                db_path=DATABASE,
                enforce_detection=False,
                threshold=0.85,
                batched=True,
                silent=True,
            )

            similar_faces = []

            for i in recognized:
                for j in i:
                    if j["distance"] < 0.3:
                        similar_faces.append(j)
            
            if len(similar_faces) > 0:
                print("allowed")
            else:
                print("not allowed")
        else:
            print("Failed to capture image.")

        sleep(2.0)


if __name__ == "__main__":
    main()
