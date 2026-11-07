# Data

The project uses the Global Carbon Project fossil CO₂ emissions dataset, version **GCB2022v27**.

Authoritative source:  
https://doi.org/10.5281/zenodo.7215364

## Required raw files
Place the following files in a local `data/raw/` directory before running the notebooks:

- `GCB2022v27_MtCO2_flat.csv`
- `GCB2022v27_MtCO2_flat_metadata.json`
- `GCB2022v27_percapita_flat.csv`
- `GCB2022v27_percapita_flat_metadata.json`
- `GCB2022v27_sources_flat.csv`
- `GCP fossilCO2 2022v27.pdf`

The primary modelling table is `GCB2022v27_MtCO2_flat.csv`.

The raw files are kept outside the repository to avoid unnecessary duplication and to preserve a clear provenance trail to the authoritative dataset release.
