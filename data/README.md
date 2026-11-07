# Data

The project uses the Global Carbon Project fossil CO₂ emissions dataset, version **GCB2022v27**.

Authoritative source:  
https://doi.org/10.5281/zenodo.7215364

## Required file to run the notebooks
Download and place this file in a local `data/raw/` directory:

- `GCB2022v27_MtCO2_flat.csv`

Both project notebooks read this file using the relative path:

`../data/raw/GCB2022v27_MtCO2_flat.csv`

## Supporting provenance files
The official GCB2022v27 release also contains supporting files used for documentation and provenance:

- `GCB2022v27_MtCO2_flat_metadata.json`
- `GCB2022v27_percapita_flat.csv`
- `GCB2022v27_percapita_flat_metadata.json`
- `GCB2022v27_sources_flat.csv`
- `GCP fossilCO2 2022v27.pdf`

These supporting files are not required for the current notebook execution path.

The raw dataset is not duplicated in this repository. Keeping the data linked to the authoritative Zenodo release preserves the provenance trail while the repository documents the exact file name and placement needed for reproduction.
