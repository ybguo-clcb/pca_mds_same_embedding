# PCA and Classical MDS: Theory and Experiments

This repository contains the article in mds_pca_similarity.md and the comparison codes in mds_pca_comparison.py, with the articale title of:

> **Why do PCA and classical MDS produce the same embedding**

The script reproduces all experiments presented in the article, including:

- Synthetic 2-D toy dataset
- Yale Face Database
- PCA
- Pairwise distance matrix
- Centered Gram matrix
- Classical MDS
- PCA on the recovered embedding

## Requirements

```bash
pip install numpy scipy matplotlib scikit-learn pillow
```

## Run

Toy dataset:

```bash
python mds_pca_comparison.py 1
```

Yale Face Database:

```bash
python mds_pca_comparison.py 2
```

The Yale Face Database should be downloaded separately and placed in the directory specified in the script (the same dir).

## License

MIT License.
