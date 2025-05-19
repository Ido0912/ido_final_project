import cv2
import os
import time
import tkinter as tk
from datetime import datetime
from PIL import Image, ImageTk
import threading


class FrameCapturer:
    def __init__(self, user_name, root):
        self.output_folder = rf'C:\Users\reuve\PycharmProjects\pythonProject33\train_data\{user_name}'
        os.makedirs(self.output_folder, exist_ok=True)
        self.root = root
        self.cap = cv2.VideoCapture(0)
        self.is_capturing = False
        self.time_left = 30
        self.label_face_detect = tk.Label(root, text="Face detection in progress...", font=("Arial", 14))
        self.label_face_detect.pack(pady=10)

        self.label_move_head = tk.Label(root, text="Move your head in all directions and look at the camera",
                                        font=("Arial", 12))
        self.label_move_head.pack(pady=10)
        self.timer_label = tk.Label(root, text=f"Time left: {self.time_left}s", font=("Arial", 16), fg="red")
        self.timer_label.pack(pady=10)
        self.video_label = tk.Label(root)
        self.video_label.pack()
        self.update_video()
        self.update_timer()
        self.start_capture()

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)
        self.root.after(20, self.update_video)

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"Time left: {self.time_left}s")
            self.root.after(1000, self.update_timer)
        else:
            self.close_window()

    def start_capture(self):
        if not self.is_capturing:
            self.is_capturing = True
            threading.Thread(target=self.capture_frames, daemon=True).start()

    def capture_frames(self, frame_rate=40, duration=12):
        if not self.cap.isOpened():
            return

        total_frames = frame_rate * duration
        frame_count = 0
        start_time = time.time()

        try:
            while frame_count < total_frames and self.is_capturing:
                ret, frame = self.cap.read()
                if not ret:
                    break

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                image_path = os.path.join(self.output_folder, f'image_{timestamp}.jpg')
                cv2.imwrite(image_path, frame)
                frame_count += 1

                elapsed_time = time.time() - start_time
                expected_time = frame_count / frame_rate
                sleep_time = max(0, expected_time - elapsed_time)
                time.sleep(sleep_time)

        finally:
            self.is_capturing = False

    def close_window(self):
        self.cap.release()
        self.root.destroy()

