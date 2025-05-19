import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam


class FaceRecognitionTrainer:
    def __init__(self, user_name, img_size=50, test_size=0.2, batch_size=32, epochs=12):
        self.user_name = user_name
        self.img_size = img_size
        self.test_size = test_size
        self.batch_size = batch_size
        self.epochs = epochs

        self.data_dir_me = rf"C:\Users\reuve\PycharmProjects\pythonProject33\cropped_data\{user_name}"
        self.data_dir_not_me = r"C:\Users\reuve\PycharmProjects\pythonProject33\cropped_data\not_me"
        self.model_save_path = rf"C:\Users\reuve\PycharmProjects\pythonProject33\models\face_recognition_{user_name}.h5"

        os.makedirs(os.path.dirname(self.model_save_path), exist_ok=True)

    def load_data(self):
        data, labels = [], []
        for img_name in os.listdir(self.data_dir_me):
            img_path = os.path.join(self.data_dir_me, img_name)
            try:
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                img = cv2.resize(img, (self.img_size, self.img_size))
                data.append(img)
                labels.append(0)
            except Exception as e:
                print(f"Error loading {img_path}: {e}")

        for img_name in os.listdir(self.data_dir_not_me):
            img_path = os.path.join(self.data_dir_not_me, img_name)
            try:
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                img = cv2.resize(img, (self.img_size, self.img_size))
                data.append(img)
                labels.append(1)
            except Exception as e:
                print(f"Error loading {img_path}: {e}")

        return np.array(data), np.array(labels)

    def build_model(self):
        model = Sequential([
            Conv2D(32, (3, 3), activation='relu', input_shape=(self.img_size, self.img_size, 1), padding='same'),
            MaxPooling2D(pool_size=(2, 2)),
            Conv2D(64, (3, 3), activation='relu', padding='same'),
            MaxPooling2D(pool_size=(2, 2)),
            Conv2D(128, (3, 3), activation='relu', padding='same'),
            MaxPooling2D(pool_size=(2, 2)),
            Conv2D(64, (3, 3), activation='relu', padding='same'),
            MaxPooling2D(pool_size=(2, 2)),
            Conv2D(32, (3, 3), activation='relu', padding='same'),
            MaxPooling2D(pool_size=(2, 2)),
            Flatten(),
            Dense(1024, activation='relu'),
            Dropout(0.8),
            Dense(2, activation='softmax')
        ])
        model.compile(optimizer=Adam(learning_rate=0.001), loss='categorical_crossentropy', metrics=['accuracy'])
        return model

    def train(self):
        data, labels = self.load_data()
        data = data / 255.0
        data = data.reshape(-1, self.img_size, self.img_size, 1)
        labels = np.array([np.eye(2)[label] for label in labels])

        X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=self.test_size, random_state=42)

        model = self.build_model()
        model.summary()
        model.fit(X_train, y_train, epochs=self.epochs, validation_data=(X_test, y_test), batch_size=self.batch_size)

        model.save(self.model_save_path)
        print(f"Model saved successfully at {self.model_save_path}")
