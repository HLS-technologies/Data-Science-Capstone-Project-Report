# IBM Applied Data Science Capstone — SpaceX Falcon 9 First-Stage Landing Prediction

**Project repository:** https://github.com/HLS-technologies/Data-Science-Capstone-Project-Report

This repository contains the notebooks, applications, and reproducible evidence for the IBM Applied Data Science Capstone. The analysis predicts the binary first-stage landing outcome (Class: 1 = successful landing, 0 = unsuccessful landing). This target is distinct from overall mission success or payload delivery.

## Repository contents

| Rubric area | Artifact | Purpose |
|---|---|---|
| SpaceX API collection | Course collection notebook / API lab | Retrieve and normalize historical launch records |
| Web scraping | Course web-scraping lab | Extract the historical Falcon 9 launch table |
| Data wrangling | data/dataset_part_2.csv, data/dataset_part_3.csv | Cleaned target data and one-hot encoded model features |
| EDA visualization | IBM_Capstone_EDA_Visualization_Completed.ipynb | Six required plots and supporting summary tables |
| Machine learning | IBM_Capstone_ML_Completed.ipynb | Logistic Regression, SVM, Decision Tree, KNN, tuning, test metrics, confusion matrix |
| Folium map | IBM_Capstone_Folium_Completed.ipynb and build_folium_map.py | Interactive launch-site map, launch markers, popups, clustering, layer controls |
| Plotly Dash | spacex_dash_app.py | Launch-site dropdown, payload range slider, success pie chart, payload/outcome scatter |
| Shared data handling | src/capstone_data.py | Schema normalization and validation |

## Course datasets

The data directory contains four separate IBM exercise datasets:

- dataset_part_2.csv: 90 Falcon 9 records with the binary Class target.
- dataset_part_3.csv: 90 one-hot encoded records aligned by row to dataset_part_2.csv.
- spacex_launch_dash.csv: 56 dashboard exercise records.
- spacex_launch_geo.csv: 56 geographical exercise records.

These are separate course datasets and must not be combined as if they were one table. The CSVs were retrieved from a public mirror of the IBM course exercise materials: https://github.com/itsskofficial/ibm-data-science-capstone. Confirm that their contents match the versions in your own IBM Skills Network/Coursera labs before final academic submission.

## Run locally

Use Python 3.11.

Create a virtual environment, activate it, then run:
python -m pip install --upgrade pip
pip install -r requirements.txt

### Machine learning notebook

Open and run IBM_Capstone_ML_Completed.ipynb from the repository root, from top to bottom. It writes the model comparison, test metrics, selected-model summary, and selected-model confusion matrix under outputs/.

### EDA visualization notebook

Open and run IBM_Capstone_EDA_Visualization_Completed.ipynb. It generates six plots and the orbit, year, and launch-site summary tables under outputs/eda/.

### Folium map

Run: python build_folium_map.py

Open outputs/spacex_launch_sites_map.html in a browser. The map includes launch-site reference markers, clustered historical launch markers, outcome colors, popups, layer controls, full-screen control, mini map, and distance measurement. Nearest railway/highway/city/coastline distances are not reported unless source-verified feature coordinates are supplied.

### Plotly Dash application

Run: python spacex_dash_app.py

Open http://127.0.0.1:8050. Select a launch site and payload range. Both the successful-landing pie chart and payload-versus-outcome scatter plot update from the selected filters.

### Capture dashboard evidence

Install Chromium for Playwright, then run:
python -m playwright install chromium
python scripts/capture_dash_evidence.py

The script saves default and filtered application screenshots in outputs/screenshots/.

## Automated validation

The GitHub Actions workflow .github/workflows/capstone-validation.yml installs dependencies, validates data and chart generation, executes the machine-learning, EDA, and Folium notebooks, captures the Dash screenshots, and publishes generated evidence under outputs/.

Generated results must be interpreted from the committed execution outputs. Do not insert performance figures from a different notebook run or a different version of the course dataset.
