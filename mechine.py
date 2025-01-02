import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam


DATA_DIR_ME = r"C:\Users\reuve\PycharmProjects\pythonProject30\cropped_data\me"
DATA_DIR_NOT_ME = r"C:\Users\reuve\PycharmProjects\pythonProject30\cropped_data\not_me"
IMG_SIZE = 50


def load_data():
    data = []
    labels = []
    for img_name in os.listdir(DATA_DIR_ME):
        img_path = os.path.join(DATA_DIR_ME, img_name)
        try:
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
            data.append(img)
            labels.append(0)
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
    for img_name in os.listdir(DATA_DIR_NOT_ME):
        img_path = os.path.join(DATA_DIR_NOT_ME, img_name)
        try:
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
            data.append(img)
            labels.append(1)
        except Exception as e:
            print(f"Error loading {img_path}: {e}")

    return np.array(data), np.array(labels)



data, labels = load_data()
data = data / 255.0
data = data.reshape(-1, IMG_SIZE, IMG_SIZE, 1)

labels = np.array([np.eye(2)[label] for label in labels])
print("Labels shape after transformation:", labels.shape)
X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=42)
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 1), padding='same'),
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
model.summary()
model.fit(X_train, y_train, epochs=12, validation_data=(X_test, y_test), batch_size=32)
model.save("face_recognition_model.h5")
print("Model saved successfully!")
