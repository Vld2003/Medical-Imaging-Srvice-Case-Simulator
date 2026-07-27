# Medical Imaging Service Case Simulator

Educational Streamlit app for basic medical image quality analysis and QA-style reporting.

## What it does

- Loads JPG/PNG/TIFF/BMP or DICOM images
- Displays image and histogram
- Calculates simple QA indicators:
  - mean intensity
  - standard deviation
  - percentile contrast
  - estimated noise
  - SNR approximation
  - CNR approximation
  - uniformity approximation
  - sharpness via variance of Laplacian
- Simulates common service/application-support image-quality cases:
  - low contrast
  - high noise
  - blur
  - non-uniformity
- Generates a downloadable HTML technical report

## Important note

This project is educational and portfolio-oriented. It is not a validated medical device,
not a diagnostic tool, and must not be used for clinical decisions.

## How to run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Suggested CV description

Personal Project – Medical Imaging Service Case Simulator  
Developed a Python/Streamlit educational tool that loads medical images, computes image-quality indicators
such as contrast, noise, SNR/CNR, uniformity and sharpness, simulates common QA/service image-quality issues,
and generates technical reports for application-support scenarios.
