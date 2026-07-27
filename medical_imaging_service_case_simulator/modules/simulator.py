from __future__ import annotations
import cv2
import numpy as np

def create_synthetic_phantom(size: int = 512) -> np.ndarray:
    #Create a simple grayscale phantom-like image for demo purposes
    img = np.zeros((size, size), dtype=np.uint8) + 35
    #Background gradient
    x = np.linspace(0, 30, size, dtype=np.float32)
    gradient = np.tile(x, (size, 1))
    img = np.clip(img.astype(np.float32) + gradient, 0, 255).astype(np.uint8)
    #Main circular phantom
    cv2.circle(img, (size // 2, size // 2), int(size*0.35), 125, -1)
    #Inserts with different contrasts
    cv2.circle(img, (int(size*0.38), int(size*0.42)), int(size*0.07), 180, -1)
    cv2.circle(img, (int(size*0.62), int(size*0.42)), int(size*0.07), 90, -1)
    cv2.rectangle(img, (int(size*0.40), int(siz*0.60)), (int(size*0.60), int(size*0.68)), 160, -1)

    # Fine line pairs
    for i in range(6):
        x0=int(size*0.35)+i*12
        cv2.line(img, (x0, int(size * 0.75)), (x0, int(size * 0.85)), 220, 2)

    return img

def apply_case(img: np.ndarray, case_name: str) -> np.ndarray:
    #Apply simulated image-quality issue
    arr=img.astype(np.float32)
    if case_name=="Normal":
        return arr.clip(0, 255).astype(np.uint8)
    if case_name=="Contrast scăzut":
        mean=arr.mean()
        out=(arr - mean)*0.45+mean
        return out.clip(0, 255).astype(np.uint8)
    if case_name=="Zgomot crescut":
        noise=np.random.normal(0, 18, arr.shape)
        out=arr+noise
        return out.clip(0, 255).astype(np.uint8)
    if case_name=="Blur / mișcare":
        kernel_size=17
        kernel=np.zeros((kernel_size, kernel_size))
        kernel[kernel_size // 2, :] = 1.0 / kernel_size
        out=cv2.filter2D(arr, -1, kernel)
        return out.clip(0, 255).astype(np.uint8)
    if case_name=="Neuniformitate":
        h, w=arr.shape
        x=np.linspace(0.55, 1.25, w, dtype=np.float32)
        field=np.tile(x, (h, 1))
        out=arr*field
        return out.clip(0, 255).astype(np.uint8)
    if case_name=="Artefact bandă":
        out = arr.copy()
        h, w = out.shape
        out[:, int(w * 0.48):int(w * 0.53)] *= 0.55
        return out.clip(0, 255).astype(np.uint8)

    return arr.clip(0, 255).astype(np.uint8)
