import os
import cv2

# תיקיות קלט ופלט
input_folder = r"C:\Users\reuve\PycharmProjects\pythonProject30\train_data\me"
output_folder = r"C:\Users\reuve\PycharmProjects\pythonProject30\cropped_data\me"
os.makedirs(output_folder, exist_ok=True)

# טעינת מודל זיהוי פנים
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

for filename in os.listdir(input_folder):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        img_path = os.path.join(input_folder, filename)
        img = cv2.imread(img_path)

        # המרת תמונה לגווני אפור לזיהוי פנים
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

        for i, (x, y, w, h) in enumerate(faces):
            face = img[y:y + h, x:x + w]  # חיתוך הפנים

            # הגדלת התמונה כך שהפנים ימלאו יותר את הפריים
            new_size = (300, 300)  # גודל חדש (אפשר לשנות לפי צורך)
            face_resized = cv2.resize(face, new_size, interpolation=cv2.INTER_CUBIC)

            # שמירת התמונה
            output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_face_{i}.jpg")
            cv2.imwrite(output_path, face_resized)

print("✅ כל הפנים נשמרו מוגדלים בתיקייה החדשה!")
