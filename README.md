# PCA and Classical MDS: Theory and Experiments

This repository contains the companion code for the article:

> **The Relationship Between Principal Component Analysis (PCA) and Classical Multidimensional Scaling (MDS): Theory and Experiments**

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
