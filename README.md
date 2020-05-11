# Project - CLEF-HIPE-2020

😎

## How to install required libraries

1. [Install](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) (or update) conda:

```bash        
# (Optional) Update previous conda instllation
$ conda update conda
```

2. Run this from the root folder

```bash
$ conda env create --file environment.yml

# (Optional) or if you need to UPDATE/add one of the conda packages, run this:
$ conda env update --file environment.yml
```

3. Activate the conda environment 🎉
    
```bash
$ conda activate hipe
```

4. (Optional) 

```bash
# To deactivate the conda environment
$ conda deactivate

# Or to remove it completely
$ conda remove --name hipe --all
```

## Downloading the data

```bash
# From the root folder of the repository
$ cd data
$ sudo chmod +x download_data.sh && ./download_data.sh
```

## How to run

```bash
# To preprocess the data (assuming we are using the 'hipe' env by conda)
(hipe) $ python code/preprocess_data.py
```

# Preprocessing Pipeline

Ordered list of steps included in the pipeline:

1. [x] Load the data into `pandas.DataFrame` for each document (ignore comments and blank lines)
2. [x] Preprocess
    1. [x] if the last row of a dataframe is a '¬': **remove it**
    2. [x] Join hyphenated tokens: if there is a `¬` token, **merge** the row above and below into one, remove the crochet row
3. [ ] Create Spacy output

---

# Report draft 

* we've found **a lot** of OCR errors, considered [this](http://ipsitransactions.org/journals/papers/tar/2016jan/p3.pdf) but will do manual autocorrect on everything first. In other words, we ignore the "# segment" lines completely