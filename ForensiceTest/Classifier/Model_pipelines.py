import os
import numpy as np
import cv2
from PIL import Image

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report

from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier


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
                X.append(extract_features(path))
                y.append(label)
            except Exception as e:
                print("Skipped", file)

    return X, y


if __name__ == "__main__":
    print("\nPROJECT ALETHEIA MULTI MODEL TRAINING\n")

    X_real, y_real = collect_dataset(REAL_DIR, 0)
    X_fake, y_fake = collect_dataset(FAKE_DIR, 1)

    X = np.array(X_real + X_fake)
    y = np.array(y_real + y_fake)

    print("Total images:", len(X))
    print("Real:", len(X_real), "Fake:", len(X_fake))

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    models = {
        "Logistic Regression": (
            LogisticRegression(max_iter=500),
            {
                "model__C": [0.01, 0.1, 1, 10]
            }
        ),

        "Ridge Classifier": (
            RidgeClassifier(),
            {
                "model__alpha": [0.1, 1, 10]
            }
        ),

        "Support Vector Machine": (
            SVC(),
            {
                "model__C": [0.1, 1, 10],
                "model__kernel": ["linear", "rbf"]
            }
        ),

        "Random Forest": (
            RandomForestClassifier(),
            {
                "model__n_estimators": [50, 100],
                "model__max_depth": [None, 5, 10]
            }
        )
    }

    for name, (model, params) in models.items():
        print("\nTraining", name)

        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("model", model)
        ])

        grid = GridSearchCV(
            pipeline,
            params,
            cv=5,
            scoring="accuracy",
            n_jobs=-1
        )

        grid.fit(X_train, y_train)

        best_model = grid.best_estimator_
        y_pred = best_model.predict(X_test)

        print("Best Parameters:", grid.best_params_)
        print("Accuracy:", accuracy_score(y_test, y_pred))
        print("Report:")
        print(classification_report(y_test, y_pred, target_names=["Real", "Fake"]))

    print("\nALL MODELS TRAINED AND EVALUATED")
