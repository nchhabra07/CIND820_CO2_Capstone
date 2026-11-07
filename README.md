# CIND820 Capstone Project
## Forecasting Country-Level Fossil CO₂ Emissions Using Machine Learning

This repository contains the code and reproducibility materials for a CIND820 Big Data Analytics capstone project at Toronto Metropolitan University.

### Project objective
The project evaluates whether historical country/entity-level fossil CO₂ emissions can be used to forecast `Total` fossil CO₂ emissions one year ahead.

For predictor year *t*, the target is the same entity's `Total` emissions at year *t+1*.

### Research questions
1. What temporal and source-composition patterns in historical fossil CO₂ emissions are associated with year-to-year changes in country-level total emissions?
2. To what extent can historical emissions information be used to forecast a country's total fossil CO₂ emissions one year ahead?
3. Which historical emissions characteristics contribute most strongly to one-year-ahead forecasts, and how much additional predictive value do they provide beyond a simple persistence baseline?

### Dataset
The analysis uses the Global Carbon Project fossil CO₂ emissions dataset, version **GCB2022v27**.

Authoritative source:  
https://doi.org/10.5281/zenodo.7215364

Primary table: `GCB2022v27_MtCO2_flat.csv`

Verified dataset characteristics:
- 63,104 rows
- 11 columns
- 232 country/entity series
- 1750–2021
- 272 annual observations per entity in the raw rectangular panel
- No duplicate Country–Year combinations
- No negative numerical emissions values

The raw dataset is not required to be stored directly in this repository. See `data/README.md` for download and placement instructions.

### Repository structure
```text
CIND820_CO2_Capstone/
├── data/
│   └── README.md
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   └── 02_model_preparation.ipynb
├── outputs/
├── README.md
├── requirements.txt
└── .gitignore
```

### Notebook execution order
#### 1. `01_data_understanding.ipynb`
Covers:
- dataset structure and integrity checks
- missing-data profiling
- zero-value analysis
- numerical distributions and skewness
- boxplots and extreme-value assessment
- temporal modelling-period assessment
- correlation analysis
- bivariate analysis
- data constraints and modelling implications

#### 2. `02_model_preparation.ipynb`
Covers:
- 1960+ modelling window
- one-year-ahead target construction
- lagged predictor construction
- leakage safeguards
- complete-case modelling data
- chronological train/validation/test split
- persistence baseline
- Linear Regression
- Random Forest Regression
- Gradient Boosting Regression
- limited hyperparameter tuning
- temporal stability analysis
- final held-out test
- VIF/multicollinearity analysis
- feature-set sensitivity
- Ridge robustness analysis
- residual diagnostics
- performance by emissions scale

### Forecasting design
The main predictors are historical values available at predictor year *t*:

- `Total_lag1`
- `Coal_lag1`
- `Oil_lag1`
- `Gas_lag1`
- `Cement_lag1`
- `Flaring_lag1`
- `Per_Capita_lag1`

These values are used to forecast `Target_Total_next_year` at *t+1*. This avoids using target-year source values to predict the same year's Total emissions.

### Modelling period
The modelling period begins in **1960**.

This choice was based on data profiling:
- approximately **90.1% core-variable completeness**
- approximately **8.3% zero Total observations**
- retention of more than six decades of forecasting history

Later start dates improve completeness only modestly while discarding substantial historical information.

### Chronological split
Predictor years:
- Training: 1960–2014
- Validation: 2015–2017
- Test: 2018–2020

Target years:
- Training: 1961–2015
- Validation: 2016–2018
- Test: 2019–2021

Random train/test shuffling is not used because the task is a time-ordered forecasting problem.

### Models
- Persistence baseline
- Linear Regression
- Random Forest Regression
- Gradient Boosting Regression
- Ridge Regression as a robustness/sensitivity check

### Evaluation metrics
- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- R²

### Final held-out test
| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Persistence | 8.049 | 40.145 | 0.9978 |
| Linear Regression | 7.524 | 31.973 | 0.9986 |

Linear Regression improved aggregate test performance relative to persistence by approximately:
- **6.53% MAE**
- **20.36% RMSE**

An important qualification is that persistence had the smaller individual absolute error for **73.58%** of test observations. Linear Regression's aggregate advantage was driven mainly by reducing some larger errors, especially among high-emission observations.

### Robustness findings
- Predictor variables show strong multicollinearity, especially when `Total_lag1` is combined with source components.
- VIF analysis therefore limits independent/causal interpretation of ordinary least-squares coefficients.
- Components-only and combined feature sets have similar average validation performance.
- Ridge regularization provides only modest changes and is treated as a robustness check rather than a replacement champion.
- Results vary across historical validation windows, supporting the use of repeated chronological evaluation.

### Environment
Recommended:
- Python 3.13.x
- Jupyter Notebook
- VS Code or another Jupyter-compatible environment

Install dependencies:

```bash
pip install -r requirements.txt
```

### Reproducibility
1. Clone this repository.
2. Download GCB2022v27 from the Zenodo source above.
3. Place the required raw files under `data/raw/` as described in `data/README.md`.
4. Install `requirements.txt`.
5. Run `01_data_understanding.ipynb`.
6. Run `02_model_preparation.ipynb`.

### GenAI declaration
ChatGPT was used as a support tool for project organization, concept explanation, Python troubleshooting, and report-language refinement. It was not used to fabricate source data or analytical results. Numerical findings were produced from executed project code and reviewed by the student.

### Primary dataset citation
Andrew, R. M., & Peters, G. P. (2022). *The Global Carbon Project's fossil CO₂ emissions dataset (Version 2022v27)* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.7215364
