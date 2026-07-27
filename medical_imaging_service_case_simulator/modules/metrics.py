from __future__ import annotations

from typing import Dict, Tuple

import cv2
import numpy as np


def normalize_float(img: np.ndarray) -> np.ndarray:
    """Convert image to float32 in [0, 255]."""
    arr = img.astype(np.float32)
    arr = np.nan_to_num(arr)
    if arr.ndim == 3:
        arr = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    return arr


def estimate_noise(img: np.ndarray) -> float:
    """
    Estimate high-frequency noise as the standard deviation of the residual:
    image - GaussianBlur(image).
    """
    arr = normalize_float(img)
    blurred = cv2.GaussianBlur(arr, (5, 5), 0)
    residual = arr - blurred
    return float(np.std(residual))


def laplacian_sharpness(img: np.ndarray) -> float:
    """Sharpness estimate using variance of the Laplacian."""
    arr = normalize_float(img)
    return float(cv2.Laplacian(arr, cv2.CV_64F).var())


def integral_uniformity(img: np.ndarray) -> float:
    """
    Approximate integral uniformity on the central 80% crop:
    100 * (1 - (max - min) / (max + min))
    Higher is better.
    """
    arr = normalize_float(img)
    h, w = arr.shape[:2]

    y1, y2 = int(0.1 * h), int(0.9 * h)
    x1, x2 = int(0.1 * w), int(0.9 * w)
    crop = arr[y1:y2, x1:x2]

    c_min = float(np.percentile(crop, 1))
    c_max = float(np.percentile(crop, 99))
    denom = c_max + c_min

    if denom <= 1e-8:
        return 0.0

    value = 100.0 * (1.0 - ((c_max - c_min) / denom))
    return float(np.clip(value, 0, 100))


def approximate_cnr(img: np.ndarray) -> float:
    """
    Approximate CNR without manual ROI selection.
    Uses Otsu threshold to split image into two regions.
    """
    arr = normalize_float(img).astype(np.uint8)

    try:
        _, mask = cv2.threshold(arr, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        region_a = arr[mask > 0].astype(np.float32)
        region_b = arr[mask == 0].astype(np.float32)

        if len(region_a) < 20 or len(region_b) < 20:
            return 0.0

        mean_diff = abs(float(region_a.mean()) - float(region_b.mean()))
        pooled_std = float(np.sqrt((region_a.var() + region_b.var()) / 2.0))

        if pooled_std < 1e-8:
            return 0.0

        return mean_diff / pooled_std
    except Exception:
        return 0.0


def calculate_metrics(img: np.ndarray) -> Dict[str, float]:
    """Calculate simple global QA-style metrics."""
    arr = normalize_float(img)

    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr))
    p5 = float(np.percentile(arr, 5))
    p95 = float(np.percentile(arr, 95))

    contrast = p95 - p5
    noise = estimate_noise(arr)
    sharpness = laplacian_sharpness(arr)
    uniformity = integral_uniformity(arr)
    cnr = approximate_cnr(arr)

    snr = mean_val / std_val if std_val > 1e-8 else 0.0

    return {
        "Mean intensity": mean_val,
        "Standard deviation": std_val,
        "Percentile contrast P95-P5": contrast,
        "Estimated noise": noise,
        "SNR approximation": snr,
        "CNR approximation": cnr,
        "Uniformity approximation (%)": uniformity,
        "Sharpness / Laplacian variance": sharpness,
    }


def interpret_metrics(metrics: Dict[str, float]) -> Tuple[str, list[str], list[str]]:
    """
    Generate a QA-style interpretation.
    Thresholds are heuristic and educational, not clinical.
    """
    observations: list[str] = []
    recommendations: list[str] = []

    contrast = metrics["Percentile contrast P95-P5"]
    noise = metrics["Estimated noise"]
    sharpness = metrics["Sharpness / Laplacian variance"]
    uniformity = metrics["Uniformity approximation (%)"]
    snr = metrics["SNR approximation"]
    cnr = metrics["CNR approximation"]

    if contrast < 55:
        observations.append("Contrastul global pare scăzut.")
        recommendations.append("Verifică parametrii de achiziție, fereastra de vizualizare sau setările de post-procesare.")
    else:
        observations.append("Contrastul global pare acceptabil pentru o analiză demonstrativă.")

    if noise > 9:
        observations.append("Estimarea zgomotului este relativ ridicată.")
        recommendations.append("Compară cu o imagine de referință și verifică dacă există setări de achiziție/doză/calibrare care pot influența zgomotul.")
    else:
        observations.append("Nivelul estimat al zgomotului nu pare ridicat.")

    if sharpness < 80:
        observations.append("Imaginea poate fi blurată sau are puține detalii de margine.")
        recommendations.append("Verifică mișcarea pacientului, focalizarea, reconstrucția sau calitatea datelor brute, în funcție de modalitate.")
    else:
        observations.append("Sharpness-ul estimat este acceptabil.")

    if uniformity < 45:
        observations.append("Uniformitatea aproximativă este scăzută.")
        recommendations.append("Verifică posibile artefacte, neuniformitate de detector/câmp sau condiții de achiziție.")
    else:
        observations.append("Uniformitatea aproximativă este acceptabilă.")

    if snr < 1.5:
        observations.append("SNR-ul aproximativ este scăzut.")
        recommendations.append("Compară imaginea cu o achiziție de referință sau cu un phantom QA.")

    if cnr < 0.8:
        observations.append("CNR-ul aproximativ este scăzut.")
        recommendations.append("Dacă există regiuni de interes clinice/tehnice, calculează CNR pe ROI-uri definite manual pentru o interpretare mai robustă.")

    if not recommendations:
        recommendations.append("Nu s-au observat probleme evidente prin metricile globale. Pentru QA real, compară cu phantom și toleranțe ale producătorului.")

    if any(word in " ".join(observations).lower() for word in ["scăzut", "ridicată", "blurată"]):
        status = "Necesită verificare tehnică suplimentară"
    else:
        status = "Aspect global acceptabil"

    return status, observations, recommendations
