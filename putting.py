import cv2
import os
import time
from datetime import datetime


choice = input("Enter 1 to save in 'me' folder or 0 to save in 'not_me' folder: ").strip()
if choice == '1':
    output_folder = r'C:\Users\reuve\PycharmProjects\pythonProject30\train_data\me'
elif choice == '0':
    output_folder = r'C:\Users\reuve\PycharmProjects\pythonProject30\train_data\not_me'
else:
    print("Invalid input. Exiting program.")
    exit()
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("eror opening camera")
    exit()
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("eror reading from the camera")
            break
        cv2.imshow('Camera', frame)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(output_folder, f'image_{timestamp}.jpg')
        cv2.imwrite(image_path, frame)
        print(f'the picture saves: {image_path}')
        time.sleep(1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("breaking")

finally:
    cap.release()
    cv2.destroyAllWindows()
