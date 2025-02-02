import tkinter as tk
from tkinter import Label, messagebox
import time
import smtplib
import random
import cv2
from PIL import Image, ImageTk
import numpy as np
from tensorflow.keras.models import load_model
import dlib
from scipy.spatial import distance
from hash import SHA256
from client import SecureClient
import os


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
sha256 = SHA256()
HOST = '127.0.0.1'
PORT = 8443
client = SecureClient(HOST, PORT, 'C:\\Users\\reuve\\PycharmProjects\\pythonProject30\\server.crt')
client.run()
send_str = ""
idle_time = 0
end_screen = None  # משתנה גלובלי למסך הראשי
overlay_window = None


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
    send_code_screen = tk.Frame(root, bg="#f5f5f5")
    send_code_screen.pack(fill="both", expand=True)
    send_label = tk.Label(send_code_screen, text="Send!",
                          font=("Arial", 18, "bold"), fg="#2a2a2a", bg="#f5f5f5")
    send_label.pack(pady=40)
    password_label = tk.Label(send_code_screen, text="Enter Password:",
                              font=("Arial", 16, "bold"), fg="#2a2a2a", bg="#f5f5f5")
    password_label.pack(pady=20)
    send_password_entry = tk.Entry(send_code_screen, show="*", font=("Arial", 16), bd=3, relief="solid", width=15)
    send_password_entry.pack(pady=20)
    submit_button = tk.Button(send_code_screen, text="Submit", font=("Arial", 18, "bold"), fg="white",
                              bg="#e74c3c", width=15, height=1, relief="raised", bd=4,
                              command=lambda: submit_send_code(send_password_entry))
    submit_button.pack(pady=15)
    resend_button = tk.Button(send_code_screen, text="Send Again", font=("Arial", 18, "bold"), fg="white",
                              bg="#e74c3c", width=15, height=1, relief="raised", bd=4, command=send_code_to_email)
    resend_button.pack(pady=15)
    change_method_button = tk.Button(send_code_screen, text="Change Method", font=("Arial", 18, "bold"), fg="white",
                                     bg="#e74c3c", width=15, height=1, relief="raised", bd=4,
                                     command=perform_face_recognition)
    change_method_button.pack(pady=15)
    send_code_screen.rowconfigure(5, weight=1)


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
    correct_password = "23719aa47cfdfc024ce5977fc6f963148809647abe152ac71d073237e865739d"
    result = str(sha256.compute_hash(entered_password.encode('utf-8')))
    if result == correct_password:
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
    success_screen = tk.Frame(root, bg="#f5f5f5")
    success_screen.pack(fill="both", expand=True)
    success_label = tk.Label(success_screen,
                             text="First identification completed!\nTo complete the login,\nchoose either Face Recognition or Email Identification",
                             font=("Arial", 18, "bold"), fg="#2a2a2a", bg="#f5f5f5", wraplength=600, justify="center")
    success_label.pack(pady=40)
    face_recognition_button = tk.Button(success_screen, text="Face Recognition", font=("Arial", 18, "bold"), fg="white",
                                        bg="#e74c3c", width=25, height=1, relief="raised", bd=4,
                                        command=perform_face_recognition)
    face_recognition_button.pack(pady=15)
    email_button = tk.Button(success_screen, text="Send Code to Email", font=("Arial", 18, "bold"), fg="white",
                             bg="#e74c3c", width=25, height=1, relief="raised", bd=4, command=send_code_to_email)
    email_button.pack(pady=15)
    success_screen.rowconfigure(5, weight=1)


def lock_application():
    with open(LOCK_FILE, "w") as file:
        file.write(str(time.time()))
    client.client_socket.close()
    root.destroy()
    client.send_message("---")
    messagebox.showerror(
        "Too Many Attempts",
        f"You have exceeded the maximum number of attempts.\nThe application is now locked for {LOCK_TIME} seconds.",
    )
    os._exit(0)


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


def reset_timer(event=None):
    """איפוס הטיימר כאשר העכבר זז - סגירת חלון האזהרה אם קיים"""
    global idle_time, overlay_window
    idle_time = 0
    # אם חלון האזהרה פתוח - נסגור אותו
    if overlay_window and overlay_window.winfo_exists():
        overlay_window.destroy()
        overlay_window = None  # מאפסים את המשתנה כדי לאפשר פתיחה מחדש

def update_timer():
    """מעקב אחר חוסר פעילות והפעלת אזהרה / סגירה בהתאם"""
    global idle_time
    idle_time += 1

    # אם אין תזוזה למשך 30 שניות - הצגת חלון האזהרה
    if idle_time == 30 and (overlay_window is None or not overlay_window.winfo_exists()):
        show_overlay_window()

    # אם אין תזוזה למשך 60 שניות - סגירת המערכת
    elif idle_time == 60:
        close_all()

    # קריאה חוזרת כל שנייה
    root.after(1000, update_timer)

def show_overlay_window():
    """הצגת חלון overlay שיתעדכן עם הזמן הנותר"""
    global overlay_window
    if overlay_window and overlay_window.winfo_exists():
        return  # אם החלון כבר קיים, לא לפתוח שוב
    overlay_window = tk.Toplevel(root)
    overlay_window.geometry("500x200")
    overlay_window.configure(bg="black")
    overlay_window.overrideredirect(True)
    overlay_window.attributes("-topmost", True)
    message_label = tk.Label(overlay_window, text=f"Due to non-use the system is about to close",
                                    font=("Arial", 18, "bold"), fg="white", bg="black")
    message_label.pack(expand=True)
    time_remaining_label = tk.Label(overlay_window, text=f"Closing in {60 - idle_time} seconds",
                                    font=("Arial", 18, "bold"), fg="white", bg="black")
    time_remaining_label.pack(expand=True)
    overlay_window.after(1000, update_overlay_time, time_remaining_label)

def update_overlay_time(time_remaining_label):
    """עדכון הזמן הנותר בהודעת ה-overlay"""
    global idle_time
    remaining_time = 60 - idle_time
    time_remaining_label.config(text=f"Closing in {remaining_time} seconds")
    if remaining_time > 0:
        overlay_window.after(1000, update_overlay_time, time_remaining_label)  # עדכון כל שנייה
    else:
        close_all()  # סוגרים את התוכנית כשהזמן מגיע ל-0

def open_end_screen():
    """פתיחת מסך הפעולות הראשי"""
    global end_screen
    if end_screen and end_screen.winfo_exists():
        return  # לא לפתוח שוב אם כבר קיים
    root.withdraw()
    end_screen = tk.Toplevel(root, bg="#f5f5f5")
    end_screen.title("Safe - What to do?")
    end_screen.geometry("650x550")
    end_screen.after(1, center_window, end_screen, 650, 550)
    root.bind_all("<Motion>", reset_timer)
    header_label = tk.Label(end_screen, text="What do you want to do in the safe?", font=("Arial", 24, "bold"),
                            fg="black", bg="#f5f5f5")
    header_label.pack(pady=40)
    add_info_button = tk.Button(end_screen, text="Add Information", font=("Arial", 18, "bold"), bg="#e74c3c", fg="white",
                                width=25, height=1, relief="raised", bd=4, command=open_add_info_screen)
    add_info_button.pack(pady=15)
    other_action_button = tk.Button(end_screen, text="Other Action", font=("Arial", 18, "bold"), bg="#e74c3c", fg="white",
                                    width=25, height=1, relief="raised", bd=4, command=open_other_action_screen)
    other_action_button.pack(pady=15)
    exit_button = tk.Button(end_screen, text="Exit", font=("Arial", 18, "bold"), bg="black", fg="white", width=25, height=1,
                            relief="raised", bd=4, command=close_all)
    exit_button.pack(pady=20)
    update_timer()


def close_all():
    client.client_socket.close()
    root.destroy()
    client.send_message("---")
    os._exit(0)


def open_add_info_screen():
    add_info_screen = tk.Toplevel(root, bg="#f5f5f5")
    add_info_screen.title("Add Information")
    add_info_screen.grab_set()
    mikud(add_info_screen)
    tk.Label(add_info_screen, text="Add Your Information", font=("Arial", 24, "bold"), fg="black", bg="#f5f5f5",
             width=25, height=2).pack(pady=20)
    tk.Label(add_info_screen, text="Content:", font=("Arial", 18, "bold"), fg="black", bg="#f5f5f5").pack(pady=5)
    content_entry = tk.Entry(add_info_screen, font=("Arial", 18), width=30)
    content_entry.pack(pady=5)
    tk.Label(add_info_screen, text="Username:", font=("Arial", 18, "bold"), fg="black", bg="#f5f5f5").pack(pady=5)
    username_entry = tk.Entry(add_info_screen, font=("Arial", 18), width=30)
    username_entry.pack(pady=5)
    tk.Label(add_info_screen, text="Password:", font=("Arial", 18, "bold"), fg="black", bg="#f5f5f5").pack(pady=5)
    password_entry = tk.Entry(add_info_screen, font=("Arial", 18), show="*", width=30)
    password_entry.pack(pady=5)

    def submit_information():
        content = content_entry.get()
        username = username_entry.get()
        password = password_entry.get()

        if content and username and password:
            client.send_message("send")
            time.sleep(0.5)  # המתנה לתשובה מהשרת

            word_options = client.important.splitlines()
            word_options = word_options[1:]
            str = ""
            for i in range(len(word_options)):
                word = word_options[i].decode()  # המרת bytes ל-str
                str = str + word
            if content in str:
                messagebox.showerror("Error", f"The content '{content}' already exists.")
                content_entry.delete(0, tk.END)
                username_entry.delete(0, tk.END)
                password_entry.delete(0, tk.END)
            else:
                messagebox.showinfo("Information Added", f"Insert {content} + {username} + {password}")
                send_str = f"insert {content} {username} {password}"
                client.send_message(send_str)
                add_info_screen.destroy()  # חזרה למסך הסיום
        else:
            messagebox.showerror("Error", "Please fill out all fields.")

    submit_button = tk.Button(add_info_screen, text="Submit", font=("Arial", 18, "bold"), bg="#e74c3c", fg="white", width=25,
                              height=1, relief="raised", bd=4, command=submit_information)
    submit_button.pack(pady=20)
    back_button = tk.Button(add_info_screen, text="Back", font=("Arial", 18, "bold"), bg="black", fg="white", width=25,
                            height=1, relief="raised", bd=4, command=add_info_screen.destroy)
    back_button.pack(pady=10)
    add_info_screen.after(1, lambda: center_window(add_info_screen, add_info_screen.winfo_width(),
                                                   add_info_screen.winfo_height()))


def open_other_action_screen():
    global other_action_screen
    other_action_screen = tk.Toplevel(root, bg="#f5f5f5")
    mikud(other_action_screen)
    other_action_screen.grab_set()
    tk.Label(other_action_screen, text="Additional Actions", font=("Arial", 24, "bold"), fg="black", bg="#f5f5f5").pack(pady=20)
    update_button = tk.Button(other_action_screen, text="Update", font=("Arial", 14, "bold"), bg="#e74c3c", fg="white",
                              width=25, height=2, relief="raised", bd=4, command=open_update_screen)
    update_button.pack(pady=10)
    show_button = tk.Button(other_action_screen, text="Show", font=("Arial", 14, "bold"), bg="#e74c3c", fg="white", width=25,
                            height=2, relief="raised", bd=4, command=open_show_screen)
    show_button.pack(pady=10)
    delete_button = tk.Button(other_action_screen, text="Delete", font=("Arial", 14, "bold"), bg="#e74c3c", fg="white",
                              width=25, height=2, relief="raised", bd=4, command=open_delete_screen)
    delete_button.pack(pady=10)
    back_button = tk.Button(other_action_screen, text="Back", font=("Arial", 14, "bold"), bg="black", fg="white", width=25,
                            height=2, relief="raised", bd=4, command=other_action_screen.destroy)
    back_button.pack(pady=10)
    other_action_screen.after(1, lambda: center_window(other_action_screen, other_action_screen.winfo_width(),
                                                       other_action_screen.winfo_height()))

def open_update_screen():
    # Create the Update Information screen
    update_screen = tk.Toplevel(root, bg="#f5f5f5")
    update_screen.title("Update Information")
    update_screen.grab_set()
    mikud(update_screen)
    client.send_message("send")
    time.sleep(0.5)

    # Check if there is any content to update
    word_options = client.important.splitlines()
    word_options = word_options[1:]

    # If there is no content to update, display a message and close the screen
    if not word_options:
        messagebox.showinfo("No Content to Update", "There is no content available to update.")
        update_screen.destroy()  # Close the update screen
        return

    client.set_import()

    tk.Label(update_screen, text="Update Information", font=("Arial", 24, "bold"), fg="black", bg="#f5f5f5",
             width=25, height=2).pack(pady=20)
    tk.Label(update_screen, text="Select a content", font=("Arial", 18, "bold"), fg="black", bg="#f5f5f5").pack(pady=5)
    selected_word = tk.StringVar(update_screen)
    selected_word.set(word_options[0])  # ברירת מחדל
    word_menu = tk.OptionMenu(update_screen, selected_word, *word_options)
    word_menu.config(font=("Arial", 18, "bold"), width=25)
    word_menu.pack(pady=5)
    tk.Label(update_screen, text="Select 'Password' or 'Username':", font=("Arial", 18, "bold"), fg="black",
             bg="#f5f5f5").pack(pady=5)
    type_options = ["password", "username"]
    selected_type = tk.StringVar(update_screen)
    selected_type.set(type_options[0])  # ברירת מחדל
    type_menu = tk.OptionMenu(update_screen, selected_type, *type_options)
    type_menu.config(font=("Arial", 18, "bold"), width=25)
    type_menu.pack(pady=5)
    tk.Label(update_screen, text="Enter the new value", font=("Arial", 18, "bold"), fg="black", bg="#f5f5f5").pack(
        pady=5)
    password_entry = tk.Entry(update_screen, font=("Arial", 18, "bold"), width=25, show="*")
    password_entry.pack(pady=5)

    # Submit button to handle the update
    def submit_update():
        selected_word_value = selected_word.get()
        selected_word_value = selected_word_value.replace("'","")
        selected_word_value = selected_word_value[1:]
        print(selected_word_value)
        selected_type_value = selected_type.get()
        new_password = password_entry.get()
        if new_password:
            messagebox.showinfo("Update Successful", f"Updated {selected_type_value} for {selected_word_value}.")
            # Here, send the updated info to the server or process as needed
            send_str = "update " + selected_word_value + " " + selected_type_value + " " + new_password
            client.send_message(send_str)
            update_screen.destroy()  # Close the update screen
            other_action_screen.grab_set()
        else:
            messagebox.showerror("Error", "Please enter a new password.")

    def back_to_previous():
        update_screen.destroy()
        other_action_screen.grab_set()

    submit_button = tk.Button(update_screen, text="Update", font=("Arial", 18, "bold"), bg="#e74c3c", fg="white",
                              width=25, height=1, relief="raised", bd=4, command=submit_update)
    submit_button.pack(pady=10)
    back_button = tk.Button(update_screen, text="Back", font=("Arial", 18, "bold"), bg="black", fg="white",
                            width=25, height=1, relief="raised", bd=4, command=back_to_previous)
    back_button.pack(pady=10)
    update_screen.after(1,
                        lambda: center_window(update_screen, update_screen.winfo_width(), update_screen.winfo_height()))


def open_show_screen():
    # Create the Show Information screen
    show_screen = tk.Toplevel(root, bg="#f5f5f5")
    show_screen.title("Show Information")
    show_screen.grab_set()
    mikud(show_screen)
    client.send_message("send")
    time.sleep(0.5)
    # Check if there is any content to show
    word_options = client.important.splitlines()
    word_options = word_options[1:]

    # If there is no content to show, display a message and close the screen
    if not word_options:
        messagebox.showinfo("No Content to Show", "There is no content available to display.")
        show_screen.destroy()  # Close the show screen
        return

    client.set_import()
    tk.Label(show_screen, text="Choose information to see", font=("Arial", 24, "bold"), fg="black", bg="#f5f5f5", width=25,
             height=2).pack(pady=20)
    tk.Label(show_screen, text="Select a content", font=("Arial", 18, "bold"), fg="black", bg="#f5f5f5").pack(pady=5)
    selected_word = tk.StringVar(show_screen)
    selected_word.set(word_options[0])  # Default value
    word_menu = tk.OptionMenu(show_screen, selected_word, *word_options)
    word_menu.config(font=("Arial", 18, "bold"), width=25)
    word_menu.pack(pady=5)
    tk.Label(show_screen, text="Select 'Password' or 'Username':", font=("Arial", 18,  "bold"), fg="black", bg="#f5f5f5").pack(
        pady=5)
    type_options = ["password", "username"]
    selected_type = tk.StringVar(show_screen)
    selected_type.set(type_options[0])  # Default value
    type_menu = tk.OptionMenu(show_screen, selected_type, *type_options)
    type_menu.config(font=("Arial", 18, "bold"), width=25)
    type_menu.pack(pady=5)
    result_label = tk.Label(show_screen, text="", font=("Arial", 18, "bold"), fg="red", bg="#f5f5f5", height=2)
    result_label.pack(pady=5)

    # Function to handle the display of the selected information
    def show_information():
        selected_word_value = selected_word.get()
        selected_word_value = selected_word_value.replace("'", "")
        selected_word_value = selected_word_value[1:]
        selected_type_value = selected_type.get()

        # Send request to retrieve the information from the server
        send_str = f"show {selected_word_value} {selected_type_value}"
        client.send_message(send_str)
        time.sleep(0.5)  # Allow time for the server to respond

        # Display the result
        result_label.config(text=f"{selected_type_value.capitalize()}: {client.important.decode()}")
        show_screen.grab_set()
        client.set_import()

    def back_to_previous():
        show_screen.destroy()
        other_action_screen.grab_set()

    submit_button = tk.Button(show_screen, text="Show", font=("Arial", 18, "bold"), bg="#e74c3c", fg="white", width=25,
                              height=1, relief="raised", bd=4, command=show_information)
    submit_button.pack(pady=10)
    back_button = tk.Button(show_screen, text="Back", font=("Arial", 18,  "bold"), bg="black", fg="white", width=25, height=1,
                            relief="raised", bd=4, command=back_to_previous)
    back_button.pack(pady=10)
    show_screen.after(1, lambda: center_window(show_screen, show_screen.winfo_width(), show_screen.winfo_height()))


def open_delete_screen():
    # Create the Delete Information screen
    delete_screen = tk.Toplevel(root, bg="#f5f5f5")
    delete_screen.title("Delete Information")
    delete_screen.grab_set()
    mikud(delete_screen)  # מוודא שהמסך מתמקד
    client.send_message("send")
    time.sleep(0.5)

    # Check if there is any content to delete
    word_options = client.important.splitlines()
    word_options = word_options[1:]

    # If there are no items to delete, show a message and return to the Safe screen
    if not word_options:
        messagebox.showinfo("No Content to Delete", "There is no content available to delete.")
        delete_screen.destroy()  # Close the delete screen
        return

    client.set_import()

    # Dropdown menu for selecting a content
    tk.Label(delete_screen, text="Delete Information", font=("Arial", 24, "bold"), fg="black", bg="#f5f5f5",
             width=25, height=2).pack(pady=20)
    tk.Label(delete_screen, text="Select a content", font=("Arial", 18, "bold"), fg="black", bg="#f5f5f5").pack(pady=5)
    selected_word = tk.StringVar(delete_screen)
    selected_word.set(word_options[0])  # ברירת מחדל
    word_menu = tk.OptionMenu(delete_screen, selected_word, *word_options)
    word_menu.config(font=("Arial", 18, "bold"), width=25)
    word_menu.pack(pady=5)

    # Submit button to handle the delete action
    def submit_delete():
        selected_word_value = selected_word.get()
        selected_word_value = selected_word_value.replace("'", "")
        selected_word_value = selected_word_value[1:]
        print(selected_word_value)
        messagebox.showinfo("Delete Successful", f"Deleted {selected_word_value}.")
        send_str = "delete " + selected_word_value
        client.send_message(send_str)
        delete_screen.destroy()  # Close the delete screen
        other_action_screen.grab_set()

    def back_to_previous():
        delete_screen.destroy()
        other_action_screen.grab_set()

    submit_button = tk.Button(delete_screen, text="Delete", font=("Arial", 18, "bold"), bg="#e74c3c", fg="white",
                              width=25, height=1, relief="raised", bd=4, command=submit_delete)
    submit_button.pack(pady=10)
    back_button = tk.Button(delete_screen, text="Back", font=("Arial", 18, "bold"), bg="black", fg="white",
                            width=25, height=1, relief="raised", bd=4, command=back_to_previous)
    back_button.pack(pady=10)
    delete_screen.after(1,
                        lambda: center_window(delete_screen, delete_screen.winfo_width(), delete_screen.winfo_height()))


def perform_face_recognition():
    for widget in root.winfo_children():
        widget.pack_forget()
    face_recognition_screen = tk.Toplevel(root)
    face_recognition_screen.overrideredirect(True)
    mikud(face_recognition_screen)
    face_recognition_screen.geometry("650x550")
    face_recognition_screen.after(1, center_window, face_recognition_screen, 650, 550)
    face_recognition_screen.title("Face and Blink Recognition")
    camera_label = tk.Label(face_recognition_screen)
    camera_label.pack()
    cap = cv2.VideoCapture(0)
    frames_detected = 0
    required_frames = 5
    no_detection_start_time = None
    blink_start_time = None
    blink_detected = False
    face_detected = False
    running = True

    def update_frame():
        nonlocal frames_detected, no_detection_start_time, blink_start_time, blink_detected, face_detected, running
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
                    # ציור ריבוע סביב הפנים
                    color = (0, 255, 0) if predicted_class == "me" else (0, 0, 255)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

            if detected_in_this_frame:
                frames_detected += 1
                face_detected = True
                no_detection_start_time = None
                if blink_start_time is None:
                    blink_start_time = time.time()
            else:
                frames_detected = 0
                if no_detection_start_time is None:
                    no_detection_start_time = time.time()
                elif time.time() - no_detection_start_time > 5:
                    cap.release()
                    face_recognition_screen.destroy()
                    messagebox.showerror("Face Recognition Failed",
                                         "No face detected for 5 seconds. Returning to the previous screen.")
                    open_success_screen()
                    return

            if face_detected:
                blink_detected = detect_blink(frame)
                if blink_detected:
                    blink_start_time = time.time()
                elif blink_start_time and time.time() - blink_start_time > 5:
                    cap.release()
                    face_recognition_screen.destroy()
                    messagebox.showerror("Blink Detection Failed",
                                         "No blink detected for 5 seconds after face recognition. Returning to the previous screen.")
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

    close_label = tk.Button(face_recognition_screen, text="Change Method", font=("Arial", 18, "bold"), fg="white",
                            bg="#e74c3c", width=25, height=2, relief="raised", bd=4, command=close_and_switch_to_email)
    close_label.pack(pady=15)
    update_frame()


def mikud(root):
    root.overrideredirect(True)
    root.protocol("WM_DELETE_WINDOW", lambda: None)
    root.attributes("-topmost", True)


def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    win_x = (screen_width // 2) - (width // 2)
    win_y = (screen_height // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{win_x}+{win_y}")


check_lock_status()
root = tk.Tk()
root.title("Safe App")
mikud(root)
root.geometry("650x550")
root.after(1, center_window, root, 650, 550)
welcome_screen = tk.Frame(root, bg="#f5f5f5")
welcome_screen.pack(fill="both", expand=True)
welcome_label = tk.Label(welcome_screen, text="WELCOME TO SAFE", font=("Arial", 30, "bold"), fg="#2a2a2a", bg="#f5f5f5")
welcome_label.pack(pady=30, expand=True)
description_label = tk.Label(welcome_screen, text="The most secure password management and protection system", font=("Arial", 14), fg="#555", bg="#f5f5f5")
description_label.pack(pady=20, expand=True)
continue_button = tk.Button(welcome_screen, text="Continue", font=("Arial", 18, "bold"), fg="white",
                            bg="#e74c3c", width=18, height=1, relief="raised", bd=4, command=show_password_screen)
continue_button.pack(pady=40)
made_by_label = tk.Label(welcome_screen, text="This project was made by Ido", font=("Arial", 10), fg="#555", bg="#f5f5f5")
made_by_label.pack(side="bottom", pady=20)

password_screen = tk.Frame(root, bg="#f5f5f5")
root.config(bg="#f5f5f5")
warning_label = tk.Label(password_screen, text="⚠ Caution! Limited number of attempts!",
                         font=("Arial", 18, "bold"), fg="#e74c3c", bg="#f5f5f5")
warning_label.grid(row=0, column=0, pady=40, sticky="n")
password_label = tk.Label(password_screen, text="Enter Password:",
                          font=("Arial", 18, "bold"), fg="#2a2a2a", bg="#f5f5f5")
password_label.grid(row=1, column=0, pady=20)
password_entry = tk.Entry(password_screen, show="*", font=("Arial", 16), bd=3, relief="solid", width=15)
password_entry.grid(row=2, column=0, pady=20)
password_entry.bind("<Return>", check_password)
submit_button = tk.Button(password_screen, text="Submit", font=("Arial", 18, "bold"), fg="white",
                          bg="#e74c3c", width=18, height=1, relief="raised", bd=4, command=check_password)
submit_button.grid(row=3, column=0, pady=40)
password_screen.rowconfigure(5, weight=1)
root.mainloop()
