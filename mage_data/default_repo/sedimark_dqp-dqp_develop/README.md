
SEDIMARK
=======
This repository contains information for the SEDIMARK data quality pipeline.

## 📥 Installation <span id='installation'>

First, download and install the Python 3.9 or later [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/distribution/#download-section).

Then run the following commands to create a conda environment named `sedimark-dqp` with Python 3.9, and activate it and then install the dqp module.

```bash
conda create -n sedimark-dqp python=3.9
conda activate sedimark-dqp
pip install -e .
```

Then there might be a need to additionally install the following packages: pycaret, torch, torchvision, tqdm, notebook, which can be installed with pip install.


### 📥 Description of Notebook <span id='notebooks'>

[`Data Deduplication.ipynb`]: This notebook demonstrates using libraries [dedupe](https://pypi.org/project/dedupe/#:~:text=dedupe%20is%20a%20python%20library,spreadsheet%20of%20names%20and%20addresses) and [recordLinkage](https://recordlinkage.readthedocs.io/en/latest/) to perform fuzzy matching, deduplication and entity resolution quickly on structured data.

[`Anomaly Detection.ipynb`]: This notebook demonstrates the usage of pycaret and sklearn for anomaly detection.

[`Missing Value Imputation.ipynb`]: This notebook demonstrates different methods to impute missing values in the datasets.

[`Data Loading.ipynb`]: This notebook demonstrates how to define the classes for loading the data to the pipeline modules and what features are required.

[`Profiling.ipynb`]: This notebook demonstrates how to do the data profiling and annotate the datasets with the data quality metrics.






