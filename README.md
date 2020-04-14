# Project - CLEF-HIPE-2020

😎

## How to install required libraries

1. [Install](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) (or update) conda:
        
        # (Optional) Update previous conda instllation
        conda update conda
       

2. Run this from the root folder


        conda env create --file environment.yml
        # (Optional) or if you need to update/add one of the conda packages, run this:
        conda env update --file environment.yml


3. Activate the conda environment
    

        conda activate hipe
        # To deactivate:
        conda deactivate hipe

## Downloading the data

```bash
$ cd data
$ sudo chmod +x download_data.sh && ./download_data.sh
```

