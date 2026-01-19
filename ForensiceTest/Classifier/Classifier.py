import os
import numpy as np
import cv2
from PIL import Image


from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler


REAL_DIR = "./Real"
FAKE_DIR = "./Fake"

SUPPORTED_EXTS = [".jpg", ".jpeg", ".png", ".webp", ".avif"]


def load_gray(path):
    img = Image.open(path).convert("L")
    return np.array(img)


def fft_energy(img):
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    magnitude = np.abs(fshift)
    return np.mean(np.log(magnitude + 1))


def noise_strength(img):
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    noise = img.astype(np.float32) - blur.astype(np.float32)
    return np.mean(np.abs(noise))


def edge_density(img):
    edges = cv2.Sobel(img, cv2.CV_64F, 1, 1, ksize=3)
    return np.mean(np.abs(edges))


def histogram_entropy(img):
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    hist = hist / np.sum(hist)
    hist = hist + 1e-7
    return -np.sum(hist * np.log2(hist))


def extract_features(path):
    img = load_gray(path)

    return [
        fft_energy(img),
        noise_strength(img),
        edge_density(img),
        histogram_entropy(img)
    ]


def collect_dataset(folder, label):
    X = []
    y = []

    for file in os.listdir(folder):
        if any(file.lower().endswith(ext) for ext in SUPPORTED_EXTS):
            path = os.path.join(folder, file)
            try:
                features = extract_features(path)
                X.append(features)
                y.append(label)
            except Exception as e:
                print("Skipped", file, e)

    return X, y


if __name__ == "__main__":
    print("\nProject Aletheia ML Classifier\n")

    X_real, y_real = collect_dataset(REAL_DIR, 0)
    X_fake, y_fake = collect_dataset(FAKE_DIR, 1)

    X = np.array(X_real + X_fake)
    y = np.array(y_real + y_fake)

    print("Total images:", len(X))
    print("Real:", len(X_real), "Fake:", len(X_fake))

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    model = LogisticRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("\nAccuracy:", accuracy_score(y_test, y_pred))
    print("\nDetailed Report:\n")
    print(classification_report(y_test, y_pred, target_names=["Real", "Fake"]))
