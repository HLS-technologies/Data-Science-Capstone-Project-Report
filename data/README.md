# IBM Capstone course datasets and provenance

The folder contains five separate course exercise files. Their row counts and purposes differ; do not treat them as a single joined dataset.

| File | Rows | Purpose | Target/important fields |
|---|---:|---|---|
| `Spacex.csv` | 101 | IBM SQL EDA exercise | `Mission_Outcome`, `Landing_Outcome`, `PAYLOAD_MASS__KG_` |
| `dataset_part_2.csv` | 90 | Falcon 9 EDA and predictive modelling | `Class`: 1 = successful first-stage landing; 0 = unsuccessful first-stage landing |
| `dataset_part_3.csv` | 90 | One-hot encoded modelling predictors | Encoded features aligned by row to `dataset_part_2.csv` |
| `spacex_launch_dash.csv` | 56 | Plotly Dash exercise | `class`, launch site, payload mass, booster category |
| `spacex_launch_geo.csv` | 56 | Folium geographical exercise | `class`, latitude/longitude, launch site and launch attributes |

## Sources

- `Spacex.csv`: public mirror of the IBM SQL exercise materials: https://github.com/sk8807307/Applied-Data-Science-Capstone
- The four other IBM course exercise files: https://github.com/itsskofficial/ibm-data-science-capstone

These repositories are public mirrors of course-exercise files, not SpaceX production datasets. Check that the contents match the files supplied inside your own IBM Skills Network/Coursera labs before relying on exact outputs for final submission.

## Interpretation safeguards

- Do not combine the 101-row SQL table with the 90-row modelling data or the 56-row Dashboard/geo data as if they have identical records.
- `Mission_Outcome` means mission/payload outcome; `Landing_Outcome` means first-stage recovery outcome. They are different fields.
- The modelling target `Class` represents first-stage landing outcome and is distinct from overall mission success.
- `data/proximity_features.csv` contains the coordinate points selected for the IBM Folium lab. Distances generated from those points are geodesic straight-line distances, not driving distances or proof of physical access routes.
