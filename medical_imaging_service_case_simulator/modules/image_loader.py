from __future__ import annotations

from io import BytesIO
from typing import Any, Dict, Tuple

import numpy as np
from PIL import Image


def normalize_to_uint8(img: np.ndarray) -> np.ndarray:
    """Normalize any numeric image to uint8 range [0, 255]."""
    arr = img.astype(np.float32)
    arr = np.nan_to_num(arr)

    min_val = float(np.min(arr))
    max_val = float(np.max(arr))

    if max_val - min_val < 1e-8:
        return np.zeros(arr.shape, dtype=np.uint8)

    arr = (arr - min_val) / (max_val - min_val)
    return (arr * 255).clip(0, 255).astype(np.uint8)


def _first_value(value: Any) -> float:
    """Return first value if a DICOM field is MultiValue-like, else scalar."""
    if isinstance(value, (list, tuple)):
        return float(value[0])
    try:
        # pydicom MultiValue behaves like a sequence
        return float(value[0])
    except Exception:
        return float(value)


def _apply_dicom_windowing(arr: np.ndarray, ds: Any) -> np.ndarray:
    """Apply simple DICOM window center/width if present."""
    if not hasattr(ds, "WindowCenter") or not hasattr(ds, "WindowWidth"):
        return arr

    try:
        center = _first_value(ds.WindowCenter)
        width = max(_first_value(ds.WindowWidth), 1.0)
    except Exception:
        return arr

    low = center - width / 2
    high = center + width / 2
    return np.clip(arr, low, high)


def load_dicom(uploaded_file: Any) -> Tuple[np.ndarray, Dict[str, str]]:
    """Load a DICOM file-like object and return a uint8 grayscale image plus metadata."""
    import pydicom

    raw = uploaded_file.read()
    ds = pydicom.dcmread(BytesIO(raw), force=True)

    arr = ds.pixel_array.astype(np.float32)

    slope = float(getattr(ds, "RescaleSlope", 1.0))
    intercept = float(getattr(ds, "RescaleIntercept", 0.0))
    arr = arr * slope + intercept

    arr = _apply_dicom_windowing(arr, ds)

    # MONOCHROME1 means low values should be displayed as white, so invert for visualization.
    if str(getattr(ds, "PhotometricInterpretation", "")).upper() == "MONOCHROME1":
        arr = np.max(arr) - arr

    image = normalize_to_uint8(arr)

    metadata = {
        "Modality": str(getattr(ds, "Modality", "N/A")),
        "PatientID": str(getattr(ds, "PatientID", "N/A")),
        "StudyDescription": str(getattr(ds, "StudyDescription", "N/A")),
        "SeriesDescription": str(getattr(ds, "SeriesDescription", "N/A")),
        "Manufacturer": str(getattr(ds, "Manufacturer", "N/A")),
        "Rows": str(getattr(ds, "Rows", image.shape[0])),
        "Columns": str(getattr(ds, "Columns", image.shape[1])),
    }

    return image, metadata


def load_standard_image(uploaded_file: Any) -> Tuple[np.ndarray, Dict[str, str]]:
    """Load a common image format and return a uint8 grayscale image plus metadata."""
    img = Image.open(uploaded_file).convert("L")
    arr = np.array(img)
    metadata = {
        "Format": str(getattr(img, "format", "standard image")),
        "Width": str(img.width),
        "Height": str(img.height),
    }
    return arr, metadata


def load_uploaded_image(uploaded_file: Any) -> Tuple[np.ndarray, Dict[str, str]]:
    """Load DICOM or standard image based on file extension."""
    name = uploaded_file.name.lower()

    if name.endswith(".dcm") or name.endswith(".dicom"):
        return load_dicom(uploaded_file)

    return load_standard_image(uploaded_file)
