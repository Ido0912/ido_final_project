import cv2
import dlib
from scipy.spatial import distance

def calculate_ear(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

cap = cv2.VideoCapture(0)

blink_count = 0  # מונה למצמוצים
blink_threshold = 2  # מספר המצמוצים הנדרש לסיום

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)
        left_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
        right_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]

        left_ear = calculate_ear(left_eye)
        right_ear = calculate_ear(right_eye)
        ear = (left_ear + right_ear) / 2.0

        if ear < 0.2:  # סף למצמוץ
            cv2.putText(frame, "Blink Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            blink_count += 1

            # מניעת ספירה כפולה באותו מצמוץ
            while ear < 0.2:
                ret, frame = cap.read()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = detector(gray)
                for face in faces:
                    landmarks = predictor(gray, face)
                    left_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
                    right_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]
                    left_ear = calculate_ear(left_eye)
                    right_ear = calculate_ear(right_eye)
                    ear = (left_ear + right_ear) / 2.0

        if blink_count >= blink_threshold:
            print("זוהו 2 מצמוצים! התוכנית תיסגר עכשיו.")
            cap.release()
            cv2.destroyAllWindows()
            exit()

    cv2.imshow("Liveness Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
