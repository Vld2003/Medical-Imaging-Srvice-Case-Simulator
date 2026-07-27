from __future__ import annotations

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from modules.image_loader import load_uploaded_image, normalize_to_uint8
from modules.metrics import calculate_metrics, interpret_metrics
from modules.report import build_html_report
from modules.simulator import apply_case, create_synthetic_phantom


st.set_page_config(
    page_title="Medical Imaging Service Case Simulator",
    page_icon="🩻",
    layout="wide",
)


def enhance_contrast_clahe(img: np.ndarray) -> np.ndarray:
    """Apply CLAHE for visual contrast enhancement."""
    arr = normalize_to_uint8(img)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(arr)


def plot_histogram(img: np.ndarray):
    """Create a matplotlib histogram figure."""
    fig, ax = plt.subplots()
    ax.hist(img.ravel(), bins=64)
    ax.set_title("Intensity histogram")
    ax.set_xlabel("Intensity")
    ax.set_ylabel("Pixel count")
    return fig


def metrics_to_dataframe(metrics: dict[str, float]) -> pd.DataFrame:
    return pd.DataFrame(
        [{"Metric": key, "Value": round(value, 3)} for key, value in metrics.items()]
    )


st.title("🩻 Medical Imaging Service Case Simulator")
st.caption(
    "Aplicație educațională pentru analiză simplă de calitate a imaginii și raport QA-style. "
    "Nu este instrument clinic validat."
)

with st.sidebar:
    st.header("Input")
    input_mode = st.radio(
        "Alege sursa imaginii:",
        ["Încarcă imagine / DICOM", "Folosește phantom demo"],
    )

    uploaded_file = None
    selected_case = "Normal"

    if input_mode == "Încarcă imagine / DICOM":
        uploaded_file = st.file_uploader(
            "Încarcă fișier",
            type=["dcm", "dicom", "png", "jpg", "jpeg", "bmp", "tif", "tiff"],
        )
        selected_case = st.selectbox(
            "Simulează o problemă peste imaginea încărcată:",
            ["Normal", "Contrast scăzut", "Zgomot crescut", "Blur / mișcare", "Neuniformitate", "Artefact bandă"],
        )
    else:
        selected_case = st.selectbox(
            "Alege scenariul demonstrativ:",
            ["Normal", "Contrast scăzut", "Zgomot crescut", "Blur / mișcare", "Neuniformitate", "Artefact bandă"],
        )

    st.divider()
    st.markdown("### Praguri euristice")
    st.write(
        "Interpretarea este orientativă. Pentru QA real se folosesc phantom, protocoale, toleranțe "
        "și documentația producătorului."
    )


image = None
metadata = {}
file_name = selected_case

if input_mode == "Încarcă imagine / DICOM":
    if uploaded_file is not None:
        try:
            image, metadata = load_uploaded_image(uploaded_file)
            image = apply_case(image, selected_case)
            file_name = uploaded_file.name
            metadata["Simulated case"] = selected_case
        except Exception as exc:
            st.error(f"Nu am putut încărca fișierul: {exc}")
    else:
        st.info("Încarcă o imagine sau un fișier DICOM pentru analiză.")
else:
    image = create_synthetic_phantom()
    image = apply_case(image, selected_case)
    metadata = {
        "Source": "Synthetic phantom",
        "Simulated case": selected_case,
        "Rows": str(image.shape[0]),
        "Columns": str(image.shape[1]),
    }


if image is not None:
    metrics = calculate_metrics(image)
    status, observations, recommendations = interpret_metrics(metrics)
    enhanced = enhance_contrast_clahe(image)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Imagine analizată")
        st.image(image, caption=f"Input: {file_name}", use_container_width=True, clamp=True)

    with col2:
        st.subheader("Contrast enhancement demo")
        st.image(enhanced, caption="CLAHE - doar pentru vizualizare", use_container_width=True, clamp=True)

    st.divider()

    col3, col4 = st.columns([1, 1])

    with col3:
        st.subheader("Metrici calculate")
        df = metrics_to_dataframe(metrics)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with col4:
        st.subheader("Histogramă")
        st.pyplot(plot_histogram(image), use_container_width=True)

    st.divider()

    st.subheader("Interpretare tehnică")
    st.markdown(f"**Status:** {status}")

    st.markdown("**Observații:**")
    for item in observations:
        st.write(f"- {item}")

    st.markdown("**Recomandări:**")
    for item in recommendations:
        st.write(f"- {item}")

    st.divider()

    with st.expander("Metadata"):
        st.json(metadata)

    report_html = build_html_report(
        file_name=file_name,
        metadata=metadata,
        metrics=metrics,
        status=status,
        observations=observations,
        recommendations=recommendations,
    )

    st.download_button(
        label="Descarcă raport HTML",
        data=report_html,
        file_name="medical_imaging_qa_report.html",
        mime="text/html",
    )

    st.warning(
        "Disclaimer: aplicația este educațională/portofoliu. Nu este dispozitiv medical, "
        "nu oferă diagnostic și nu se folosește pentru decizii clinice."
    )
