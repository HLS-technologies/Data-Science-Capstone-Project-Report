# IBM Applied Data Science Capstone — SpaceX Falcon 9 First-Stage Landing Prediction

**Project repository:** https://github.com/HLS-technologies/Data-Science-Capstone-Project-Report

This repository contains the notebooks, applications, and reproducible evidence for the IBM Applied Data Science Capstone. The analysis predicts the binary first-stage landing outcome (Class: 1 = successful landing, 0 = unsuccessful landing). This target is distinct from overall mission success or payload delivery.

## Repository contents

| Rubric area | Artifact | Purpose |
|---|---|---|
| SpaceX API collection | [SpaceX_API_Data_Collection.ipynb](SpaceX_API_Data_Collection.ipynb) | Retrieve and normalize historical launch records |
| Web scraping | [Web_Scraping_Falcon9_Launch_Records.ipynb](Web_Scraping_Falcon9_Launch_Records.ipynb) | Extract launch history from HTML tables |
| Data wrangling | [Data_Wrangling_Completed.ipynb](Data_Wrangling_Completed.ipynb) | Missing-value treatment, target validation, feature selection and encoding |
| SQL EDA | [EDA_SQL_Analysis_Completed.ipynb](EDA_SQL_Analysis_Completed.ipynb) | SQL queries for launch sites, payloads, outcomes, ranking and yearly trends |
| EDA visualization | IBM_Capstone_EDA_Visualization_Completed.ipynb | Six required plots and supporting summary tables |
| Machine learning | IBM_Capstone_ML_Completed.ipynb | Logistic Regression, SVM, Decision Tree, KNN, tuning, test metrics, confusion matrix |
| Folium map | IBM_Capstone_Folium_Completed.ipynb and build_folium_map.py | Interactive launch-site map, launch markers, popups, clustering, layer controls |
| Plotly Dash | spacex_dash_app.py | Launch-site dropdown, payload range slider, success pie chart, payload/outcome scatter |
| Shared data handling | src/capstone_data.py | Schema normalization and validation |

## Course datasets and dataset scope

The repository keeps five separate IBM course exercise snapshots. They serve different exercises and must not be merged as if they were one table:

- `data/Spacex.csv`: **101-row SQL exercise dataset**, with separate `Mission_Outcome` and `Landing_Outcome` fields. Used by `EDA_SQL_Analysis_Completed.ipynb`.
- `data/dataset_part_2.csv`: **90 Falcon 9 records** with binary `Class` target (1 = successful first-stage landing; 0 = unsuccessful first-stage landing). Used for EDA and modelling.
- `data/dataset_part_3.csv`: **90-row one-hot encoded feature matrix** aligned by row to `dataset_part_2.csv`.
- `data/spacex_launch_dash.csv`: **56 dashboard exercise records**.
- `data/spacex_launch_geo.csv`: **56 geographical exercise records**.

The course snapshots were retrieved from public mirrors of IBM exercise materials. The source locations and dataset-specific scope are documented in `data/README.md`. Verify these copies against the files in your own IBM Skills Network/Coursera labs before final academic submission. The SQL, modelling, dashboard, and geographical record counts intentionally differ.

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

Run: `python build_folium_map.py`.

Open `outputs/spacex_launch_sites_map.html` in a browser. The map includes launch-site reference markers, clustered launch records, green/red first-stage outcome markers, pop-ups, layer controls, fullscreen/minimap, mouse coordinates, and measurement controls. The IBM lab's selected coastline, railway, highway, and city points are stored in `data/proximity_features.csv`; the script calculates geodesic straight-line distances from the launch-site coordinates. These are not road-network or driving distances.

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
