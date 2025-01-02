import cv2
import numpy as np
from tensorflow.keras.models import load_model

# הגדר את גודל התמונה עליו המודל אומן
IMG_SIZE = 50

# טען את המודל המאומן
model = load_model("face_recognition_model.h5")

# טען את הקובץ של גלאי הפנים (Haar Cascade)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


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
def predict_face(face):
    try:
        # המרה לגרייסקייל אם נדרש
        if len(face.shape) == 3:  # אם התמונה צבעונית
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        # עיבוד התמונה
        preprocessed_img = preprocess_image(face)
        # בצע ניבוי
        prediction = model.predict(preprocessed_img)
        # החזרת התוצאה עם קטגוריה
        classes = ["me", "not_me"]
        predicted_class = classes[np.argmax(prediction)]
        confidence = np.max(prediction)
        return predicted_class, confidence
    except Exception as e:
        return None, 0


# הפעלת המצלמה
cap = cv2.VideoCapture(0)  # 0 הוא מזהה המצלמה הראשית

if not cap.isOpened():
    print("Error: Cannot open the camera.")
    exit()

print("Starting the camera... Press 'q' to quit.")

# משתנה לספירת פריימים בהם זוהית
frames_detected = 0
required_frames = 5  # מספר פריימים רצופים נדרשים לזיהוי

while True:
    # קריאת פריים מהמצלמה
    ret, frame = cap.read()
    if not ret:
        print("Error: Cannot read from the camera.")
        break

    # המרת התמונה לגרייסקייל לזיהוי פנים
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # זיהוי פנים
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    detected_in_this_frame = False

    for (x, y, w, h) in faces:
        # חיתוך הפנים
        face = frame[y:y + h, x:x + w]

        # ניבוי
        predicted_class, confidence = predict_face(face)

        # אם זוהית כ-"me" עם ביטחון גבוה
        if predicted_class == "me" and confidence > 0.90:
            detected_in_this_frame = True

        # ציור ריבוע סביב הפנים
        color = (0, 255, 0) if predicted_class == "me" else (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

    # עדכון מספר פריימים רצופים בהם זוהית
    if detected_in_this_frame:
        frames_detected += 1
    else:
        frames_detected = 0

    # אם זוהית בפריימים רצופים כנדרש
    if frames_detected >= required_frames:
        print("זוהה! נסגר לאחר זיהוי רציף.")
        cap.release()
        cv2.destroyAllWindows()
        exit()

    # הצגת הווידאו בזמן אמת
    cv2.imshow("Camera", frame)

    # סיום התוכנית אם המשתמש לוחץ על 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# שחרור המצלמה וסגירת כל החלונות
cap.release()
cv2.destroyAllWindows()
