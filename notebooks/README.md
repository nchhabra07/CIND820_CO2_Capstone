# Notebooks

Run the detailed analysis notebooks in this order:

1. `01_data_understanding.ipynb`
2. `02_model_preparation.ipynb`

For the Milestone 3 live proof of concept, use:

3. `03_poc_pipeline_demo.ipynb`

The first notebook performs dataset audit, profiling, EDA, and modelling-period assessment.  
The second notebook constructs the one-year-ahead forecasting dataset, evaluates baselines and candidate models, performs chronological stability checks, and runs final diagnostics.  
The third notebook is a compact executed demonstration that calls the reusable functions in `../src/co2_pipeline.py` and shows the functional path from data ingestion through initial model evaluation.

Compiled HTML exports are stored in `notebooks/compiled/` for reproducible viewing without executing the notebooks.
