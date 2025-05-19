import os
import cv2
import threading
from facerecognition.mechine import FaceRecognitionTrainer


class FaceCropper:
    def __init__(self):
        self.input_folder = ""
        self.output_folder = ""
        self.user_name = ""
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.processing_thread = None
        self.is_training = False

    def set_info(self, user_name):
        self.user_name = user_name
        self.input_folder = rf"C:\Users\reuve\PycharmProjects\pythonProject33\train_data\{user_name}"
        self.output_folder = rf"C:\Users\reuve\PycharmProjects\pythonProject33\cropped_data\{user_name}"
        os.makedirs(self.output_folder, exist_ok=True)

    def process_image(self, img_path, filename):
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

        for i, (x, y, w, h) in enumerate(faces):
            face = img[y:y + h, x:x + w]
            new_size = (300, 300)
            face_resized = cv2.resize(face, new_size, interpolation=cv2.INTER_CUBIC)

            output_path = os.path.join(self.output_folder, f"{os.path.splitext(filename)[0]}_face_{i}.jpg")
            cv2.imwrite(output_path, face_resized)

    def process_images(self):
        for filename in os.listdir(self.input_folder):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                img_path = os.path.join(self.input_folder, filename)
                self.process_image(img_path, filename)

        print("✅ כל הפנים נשמרו בתיקייה החדשה!")
        self.start_training()

    def start_processing_in_thread(self):
        self.processing_thread = threading.Thread(target=self.process_images)
        self.processing_thread.start()

    def is_processing(self):
        return (self.processing_thread and self.processing_thread.is_alive()) or self.is_training

    def start_training(self):
        def train_model():
            self.is_training = True
            trainer = FaceRecognitionTrainer(self.user_name)
            trainer.train()
            self.is_training = False
            print(f"🎉 המודל עבור {self.user_name} נשמר בהצלחה!")

        training_thread = threading.Thread(target=train_model)
        training_thread.start()
