import tkinter as tk
from tkinter import Label, messagebox
import time
import os
import smtplib
import random
import cv2
from PIL import Image, ImageTk
import numpy as np
from tensorflow.keras.models import load_model
import dlib
from scipy.spatial import distance


attempts = 0
incorrect_attempts = 0
MAX_ATTEMPTS = 10
LOCK_TIME = 120
LOCK_FILE = "lock_file.txt"
sender_email = "reuveniido3@gmail.com"
receiver_email = "reuveniido10@gmail.com"
password = ""
IMG_SIZE = 50
model = load_model("face_recognition_model.h5")
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
predictor_path = "shape_predictor_68_face_landmarks.dat"
face_detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor(predictor_path)


def calculate_ear(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear


def detect_blink(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detector(gray)
    for face in faces:
        shape = shape_predictor(gray, face)
        shape_np = np.array([[p.x, p.y] for p in shape.parts()])
        left_eye = shape_np[36:42]
        right_eye = shape_np[42:48]
        left_ear = calculate_ear(left_eye)
        right_ear = calculate_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        return avg_ear < 0.25
    return False


def generate_random_password():
    global password
    password = ""
    for i in range(6):
        num = str(random.randint(0, 9))
        password = password + num + " "
    return password.strip()


def send_code_to_email():
    success_screen.pack_forget()
    generated_password = generate_random_password()
    message = f"""From: From Person <reuveniido3@gmail.com>
To: To Person <reuveniido10@gmail.com>
Subject: Password

Your new password is: {generated_password}
"""
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(sender_email, "dbrj lpbp fnkj qslo")
        server.sendmail(sender_email, receiver_email, message)
        server.close()
        print("Password sent to email!")
    except Exception as exception:
        print(f"Error: {exception}")
    send_code_screen = tk.Frame(root)
    send_code_screen.pack()
    send_label = tk.Label(send_code_screen, text="Send!", font=("Arial", 14))
    send_label.pack(pady=20)
    password_label = tk.Label(send_code_screen, text="Enter Password:")
    password_label.pack(pady=10)
    send_password_entry = tk.Entry(send_code_screen, show="*")
    send_password_entry.pack(pady=10)
    submit_button = tk.Button(send_code_screen, text="Submit", command=lambda: submit_send_code(send_password_entry))
    submit_button.pack(pady=10)
    resend_button = tk.Button(send_code_screen, text="Send Again", command=send_code_to_email)
    resend_button.pack(pady=10)
    change_method_button = tk.Button(send_code_screen, text="Change Method", command=perform_face_recognition)
    change_method_button.pack(pady=10)


def submit_send_code(password_entry):
    global password, incorrect_attempts
    entered_password = password_entry.get()
    if entered_password == password.replace(" ", ""):
        for widget in root.winfo_children():
            widget.pack_forget()
        open_end_screen()
    else:
        password_entry.delete(0, tk.END)
        incorrect_attempts += 1
        if incorrect_attempts >= 3:
            send_code_to_email()
            messagebox.showinfo("Password Changed", f"too much attempts. the password is changed!")
            incorrect_attempts = 0
        else:
            messagebox.showerror("Error", f"Incorrect password. there are {3-incorrect_attempts} before the password is changed!")


def open_next_screen():
    messagebox.showinfo("Next Step", "You have passed the password verification! Proceeding to next step.")


def switch_to_email_verification(current_screen):
    current_screen.pack_forget()
    send_code_to_email()


def check_lock_status():
    if os.path.exists(LOCK_FILE):
        with open(LOCK_FILE, "r") as file:
            lock_time = float(file.read().strip())
        current_time = time.time()
        if current_time - lock_time < LOCK_TIME:
            remaining_time = int(LOCK_TIME - (current_time - lock_time))
            messagebox.showerror(
                "Application Locked",
                f"The application is locked due to too many attempts.\nTry again in {remaining_time} seconds.",
            )
            exit()
        else:
            os.remove(LOCK_FILE)


def show_password_screen():
    welcome_screen.pack_forget()
    password_screen.pack()


def check_password(event=None):
    global attempts
    entered_password = password_entry.get()
    correct_password = "12345"
    if entered_password == correct_password:
        password_screen.pack_forget()
        open_success_screen()
    else:
        attempts += 1
        password_entry.delete(0, tk.END)
        if attempts >= MAX_ATTEMPTS:
            lock_application()
        elif attempts % 3 == 0:
            messagebox.showwarning(
                "Incorrect Password", f"Incorrect password! Attempts left: {MAX_ATTEMPTS - attempts}"
            )


def open_success_screen():
    global success_screen
    password_entry.unbind("<Return>")
    success_screen = tk.Frame(root)
    success_screen.pack()
    success_label = tk.Label(success_screen, text="Identification 1 completed! Choose another way of identification",
                             font=("Arial", 14))
    success_label.pack(pady=20)
    email_button = tk.Button(success_screen, text="Send Code to Email", command=send_code_to_email)
    email_button.pack(pady=10)
    face_recognition_button = tk.Button(success_screen, text="Face Recognition", command=perform_face_recognition)
    face_recognition_button.pack(pady=10)


def lock_application():
    with open(LOCK_FILE, "w") as file:
        file.write(str(time.time()))
    messagebox.showerror(
        "Too Many Attempts",
        f"You have exceeded the maximum number of attempts.\nThe application is now locked for {LOCK_TIME} seconds.",
    )
    exit()

def preprocess_image(image):
    img = cv2.resize(image, (IMG_SIZE, IMG_SIZE))
    img = img / 255.0
    img = np.expand_dims(img, axis=-1)
    img = np.expand_dims(img, axis=0)
    return img

def predict_face(face):
    if len(face.shape) == 3:
        face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    preprocessed_img = preprocess_image(face)
    prediction = model.predict(preprocessed_img)
    classes = ["me", "not_me"]
    predicted_class = classes[np.argmax(prediction)]
    confidence = np.max(prediction)
    return predicted_class, confidence


def open_end_screen():
    root.withdraw()
    end_screen = tk.Toplevel(root)
    end_screen.title("Success")
    tk.Label(end_screen, text="Face recognition completed successfully!", font=("Arial", 16)).pack(pady=20)
    tk.Button(end_screen, text="Exit", command=root.quit).pack(pady=10)


def perform_face_recognition():
    for widget in root.winfo_children():
        widget.pack_forget()
    face_recognition_screen = tk.Toplevel(root)
    face_recognition_screen.title("Face and Blink Recognition")
    camera_label = tk.Label(face_recognition_screen)
    camera_label.pack()
    cap = cv2.VideoCapture(0)
    frames_detected = 0
    required_frames = 5
    no_detection_start_time = None
    no_blink_start_time = None
    blink_detected = False
    running = True

    def update_frame():
        nonlocal frames_detected, no_detection_start_time, no_blink_start_time, blink_detected, running
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(frame_rgb))
            camera_label.imgtk = img
            camera_label.configure(image=img)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            detected_in_this_frame = False
            for (x, y, w, h) in faces:
                face = frame[y:y + h, x:x + w]
                predicted_class, confidence = predict_face(face)
                if predicted_class == "me" and confidence > 0.90:
                    detected_in_this_frame = True
            if detected_in_this_frame:
                frames_detected += 1
                no_detection_start_time = None
            else:
                frames_detected = 0
                if no_detection_start_time is None:
                    no_detection_start_time = time.time()
                elif time.time() - no_detection_start_time > 5:
                    cap.release()
                    face_recognition_screen.destroy()
                    messagebox.showerror("Face Recognition Failed", "No face detected for 5 seconds. Returning to the previous screen.")
                    open_success_screen()
                    return
            blink_detected = detect_blink(frame)
            if blink_detected:
                no_blink_start_time = None
            else:
                if no_blink_start_time is None:
                    no_blink_start_time = time.time()
                elif time.time() - no_blink_start_time > 5:
                    cap.release()
                    face_recognition_screen.destroy()
                    messagebox.showerror("Blink Detection Failed", "No blink detected for 5 seconds. Returning to the previous screen.")
                    open_success_screen()
                    return
            if frames_detected >= required_frames and blink_detected:
                cap.release()
                face_recognition_screen.destroy()
                open_end_screen()
                return

        if running:
            face_recognition_screen.after(10, update_frame)

    def close_and_switch_to_email():
        nonlocal running
        running = False
        cap.release()
        face_recognition_screen.destroy()
        send_code_to_email()

    close_label = Label(face_recognition_screen, text="Change Method", bg="white", fg="black", font=("Arial", 16), width=20)
    close_label.pack(pady=10)
    close_label.bind("<Button-1>", lambda e: close_and_switch_to_email())
    update_frame()


check_lock_status()
root = tk.Tk()
root.title("Safe App")
root.geometry("300x300")
welcome_screen = tk.Frame(root)
welcome_screen.pack()
welcome_label = tk.Label(welcome_screen, text="WELCOME TO SAFE", font=("Arial", 16))
welcome_label.pack(pady=20)
continue_button = tk.Button(welcome_screen, text="Continue", command=show_password_screen)
continue_button.pack()
password_screen = tk.Frame(root)
password_label = tk.Label(password_screen, text="Enter Password:")
password_label.pack(pady=10)
password_entry = tk.Entry(password_screen, show="*")
password_entry.pack(pady=10)
password_entry.bind("<Return>", check_password)
submit_button = tk.Button(password_screen, text="Submit", command=check_password)
submit_button.pack()
root.mainloop()
