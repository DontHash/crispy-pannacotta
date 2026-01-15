
import os
import numpy as np
import cv2
import matplotlib.pyplot as plt

from PIL import Image
import pillow_avif





REAL_DIR = "./Real"
AI_DIR = "./AI"
OUTPUT_DIR = "./Forensic_Reports"

SUPPORTED_EXTS = [".jpg", ".jpeg", ".png", ".webp", ".avif"]

os.makedirs(OUTPUT_DIR, exist_ok=True)




def load_image_gray(path):
    try:
        img = Image.open(path).convert("L") 
        return np.array(img)
    except Exception as e:
        print(f"[!] Failed to load {path}: {e}")
        return None


def find_image(folder, index):
    for ext in SUPPORTED_EXTS:
        path = os.path.join(folder, f"{index}{ext}")
        if os.path.exists(path):
            return path
    return None



def fft_spectrum(img):
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    return 20 * np.log(np.abs(fshift) + 1)


def noise_residual(img):
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    return cv2.subtract(img, blur)


def edge_density(img):
    edges = cv2.Sobel(img, cv2.CV_64F, 1, 1, ksize=3)
    return np.abs(edges)


def intensity_histogram(img):
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    return hist / hist.sum()



def generate_pair_report(real_path, ai_path, index):
    print(f"[*] Analyzing Pair {index}")

    real_img = load_image_gray(real_path)
    ai_img = load_image_gray(ai_path)

    if real_img is None or ai_img is None:
        print(f"[!] Skipping pair {index} due to load failure")
        return

 
    real_fft = fft_spectrum(real_img)
    ai_fft = fft_spectrum(ai_img)

    real_noise = noise_residual(real_img)
    ai_noise = noise_residual(ai_img)

    real_edges = edge_density(real_img)
    ai_edges = edge_density(ai_img)

    real_hist = intensity_histogram(real_img)
    ai_hist = intensity_histogram(ai_img)


    plt.style.use("dark_background")
    fig, axs = plt.subplots(5, 2, figsize=(14, 20))

    # Row 1: Original Images
    axs[0, 0].imshow(real_img, cmap='gray')
    axs[0, 1].imshow(ai_img, cmap='gray')

    # Row 2: FFT
    axs[1, 0].imshow(real_fft, cmap='inferno')
    axs[1, 1].imshow(ai_fft, cmap='inferno')

    # Row 3: Noise Residual
    axs[2, 0].imshow(real_noise, cmap='gray')
    axs[2, 1].imshow(ai_noise, cmap='gray')

    # Row 4: Edge Density
    axs[3, 0].imshow(real_edges, cmap='gray')
    axs[3, 1].imshow(ai_edges, cmap='gray')

    # Row 5: Histogram
    axs[4, 0].plot(real_hist, color='cyan')
    axs[4, 1].plot(ai_hist, color='magenta')

    labels = [
        "Spatial Domain",
        "Frequency Spectrum (FFT)",
        "Noise Residual",
        "Edge Density",
        "Intensity Histogram"
    ]

    for i in range(5):
        axs[i, 0].set_ylabel(labels[i], fontsize=11)
        axs[i, 0].axis("off")
        axs[i, 1].axis("off")

    axs[0, 0].set_title("REAL IMAGE", color="#00ff99", fontsize=14)
    axs[0, 1].set_title("AI IMAGE", color="#ff3366", fontsize=14)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, f"Forensic_Report_{index}.png")
    plt.savefig(out_path, dpi=300)
    plt.close()

    print(f"[✓] Report Saved: {out_path}")



if __name__ == "__main__":
    print("\n[✓] PROJECT ALETHEIA INITIALIZED")
    print("Current Working Directory:", os.getcwd())

    for i in range(1, 10):
        real_path = find_image(REAL_DIR, i)
        ai_path = find_image(AI_DIR, i)

        if real_path is None or ai_path is None:
            print(f"[!] Missing files for pair {i}")
            print(f"    REAL: {real_path}")
            print(f"    AI  : {ai_path}")
            continue

        generate_pair_report(real_path, ai_path, i)

    print("\n[✓] ALL FORENSIC REPORTS GENERATED")
