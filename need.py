import cv2
import numpy as np
from tensorflow.keras.models import load_model

# הגדר את גודל התמונה עליו המודל אומן
IMG_SIZE = 50

# טען את המודל המאומן
model = load_model("face_recognition_model.h5")

# טען את הקובץ של גלאי הפנים (Haar Cascade)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


# פונקציה לחיתוך פנים
def crop_face(image_path):
    # קרא את התמונה
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read the image from path: {image_path}")

    # המרת התמונה לגרייסקייל לצורך זיהוי פנים
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # זיהוי פנים
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(faces) == 0:
        raise ValueError("No face detected in the image.")

    # השתמש בפנים הראשון שנמצא
    x, y, w, h = faces[0]
    cropped_face = img[y:y + h, x:x + w]
    return cropped_face


# פונקציה לעיבוד התמונה
def preprocess_image(image):
    # שנה את גודל התמונה לגודל המודל
    img = cv2.resize(image, (IMG_SIZE, IMG_SIZE))
    # נרמל את הערכים בין 0 ל-1
    img = img / 255.0
    # הוסף מימדים כדי להתאים למודל
    img = np.expand_dims(img, axis=-1)  # הוסף ערוץ גרייסקייל
    img = np.expand_dims(img, axis=0)  # הוסף מימד אצווה
    return img


# פונקציה לניבוי
def predict_image(image_path):
    try:
        # חיתוך פנים
        cropped_face = crop_face(image_path)
        # המרה לגרייסקייל
        gray_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2GRAY)
        # עיבוד התמונה
        preprocessed_img = preprocess_image(gray_face)
        # בצע ניבוי
        prediction = model.predict(preprocessed_img)
        # החזרת התוצאה עם קטגוריה
        classes = ["me", "not_me"]
        predicted_class = classes[np.argmax(prediction)]
        confidence = np.max(prediction)
        return predicted_class, confidence
    except Exception as e:
        return f"Error in prediction: {e}"


# נתיב לתמונה לבדיקה
image_path = r"C:\Users\reuve\PycharmProjects\pythonProject28\train_data\not_me\image_20241121_153217.jpg"  # עדכן לנתיב התמונה שלך

# בצע ניבוי
predicted_class, confidence = predict_image(image_path)

# הדפס את התוצאה
print(f"Predicted Class: {predicted_class} (Confidence: {confidence * 100:.2f}%)")