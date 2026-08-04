# -*- coding: utf-8 -*-
"""
Compare PCA and Classical MDS on either:

1. A synthetic two-dimensional point set.
2. The Yale Face Database loaded from a local directory.

The script follows the same sequence as the accompanying article:

    data -> PCA -> pairwise distances -> centered Gram matrix
         -> eigendecomposition -> Classical MDS embedding

Usage
-----
Toy data:
    python mds_pca_comparison_refactored.py 1

Yale faces:
    python mds_pca_comparison_refactored.py 2
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.distance import cdist
from sklearn.decomposition import PCA

YALE_DIRECTORY = Path(r".")

def generate_points(
    n: int = 1000,
    seed: int = 42,
    slope: float = 0.7,
    max_distance: float = 0.2,
) -> np.ndarray:
    """Generate points in [0, 1]^2 near the line y = slope * x."""
    rng = np.random.default_rng(seed)
    accepted_batches: list[np.ndarray] = []
    accepted_count = 0
    denominator = np.sqrt(slope**2 + 1.0)

    while accepted_count < n:
        batch = rng.uniform(0.0, 1.0, size=(max(5 * n, 1000), 2))
        distances = np.abs(slope * batch[:, 0] - batch[:, 1]) / denominator
        valid_points = batch[distances < max_distance]

        accepted_batches.append(valid_points)
        accepted_count += len(valid_points)

    return np.vstack(accepted_batches)[:n]


def load_yale_faces(directory: Path) -> np.ndarray:
    """Load all readable images in a directory as flattened grayscale vectors."""
    from PIL import Image

    images: list[np.ndarray] = []

    for file_name in sorted(os.listdir(directory)):
        file_path = directory / file_name
        if not file_path.is_file():
            continue

        try:
            with Image.open(file_path) as image:
                image_vector = np.asarray(
                    image.convert("L"),
                    dtype=np.float64,
                ).ravel()
            images.append(image_vector)
        except (OSError, ValueError):
            # Ignore non-image or unreadable files in the dataset directory.
            continue

    if not images:
        raise ValueError(f"No readable images were found in: {directory}")

    image_lengths = {image.size for image in images}
    if len(image_lengths) != 1:
        raise ValueError("All Yale face images must have the same dimensions.")

    return np.vstack(images)


def plot_matrix(
    matrix: np.ndarray,
    *,
    title: str,
    colorbar_label: str,
) -> None:
    """Display a square matrix as a grayscale image."""
    figure, axis = plt.subplots(figsize=(8, 7))
    image = axis.imshow(matrix, cmap="gray", origin="upper")
    figure.colorbar(image, ax=axis, label=colorbar_label)

    axis.set(
        xlabel="Sample index",
        ylabel="Sample index",
        title=title,
    )
    figure.tight_layout()


def draw_principal_axes(
    axis: plt.Axes,
    *,
    mean: np.ndarray,
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray,
    scale: float = 1.0,
    count: int = 2,
) -> None:
    """Draw the leading principal directions on an existing scatter plot."""
    for index in range(min(count, len(eigenvalues))):
        direction = eigenvectors[:, index]
        length = scale * np.sqrt(max(eigenvalues[index], 0.0))

        axis.annotate(
            "",
            xy=mean + direction * length,
            xytext=mean,
            arrowprops={
                "arrowstyle": "-|>",
                "linewidth": 2,
            },
        )
        axis.text(
            *(mean + direction * length),
            f"  PC{index + 1}",
            va="center",
        )


def plot_embedding(
    points: np.ndarray,
    *,
    title: str,
    xlabel: str = "Dimension 1",
    ylabel: str = "Dimension 2",
    eigenvalues: np.ndarray | None = None,
    eigenvectors: np.ndarray | None = None,
    arrow_scale: float = 1.0,
) -> None:
    """Plot the first two dimensions of an embedding."""
    if points.ndim != 2 or points.shape[1] < 2:
        raise ValueError("The embedding must contain at least two dimensions.")

    figure, axis = plt.subplots(figsize=(8, 8))
    axis.scatter(points[:, 0], points[:, 1], s=5, alpha=0.6)
    axis.set(
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
    )
    axis.set_aspect("equal", adjustable="box")

    if eigenvalues is not None and eigenvectors is not None:
        draw_principal_axes(
            axis,
            mean=points[:, :2].mean(axis=0),
            eigenvalues=eigenvalues,
            eigenvectors=eigenvectors[:2, :],
            scale=arrow_scale,
        )

    figure.tight_layout()


def classical_mds(
    distance_matrix: np.ndarray,
    n_components: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Recover a Classical MDS embedding from a Euclidean distance matrix.

    Returns
    -------
    coordinates:
        Reconstructed coordinates with shape
        (n_samples, n_components).
    eigenvalues:
        Eigenvalues of the centered Gram matrix, sorted descending.
    gram_matrix:
        The centered Gram matrix.
    """
    squared_distances = distance_matrix**2
    row_means = squared_distances.mean(axis=1, keepdims=True)
    column_means = squared_distances.mean(axis=0, keepdims=True)
    grand_mean = squared_distances.mean()

    gram_matrix = -0.5 * (
        squared_distances - row_means - column_means + grand_mean
    )

    eigenvalues, eigenvectors = np.linalg.eigh(gram_matrix)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]

    # Tiny negative values can appear because of floating-point round-off.
    tolerance = np.finfo(float).eps * max(gram_matrix.shape) * np.max(
        np.abs(eigenvalues)
    )
    eigenvalues[np.abs(eigenvalues) < tolerance] = 0.0

    if np.any(eigenvalues[:n_components] < 0):
        raise ValueError(
            "The requested dimensions include negative eigenvalues; "
            "the supplied distances are not exactly Euclidean."
        )

    coordinates = (
        eigenvectors[:, :n_components]
        * np.sqrt(eigenvalues[:n_components])
    )

    return coordinates, eigenvalues, gram_matrix


def main() -> None:
    # Step 1: Prepare the dataset.
    if len(sys.argv) != 2 or sys.argv[1] not in {"1", "2"}:
        sys.exit(
            f"Usage: python {Path(sys.argv[0]).name} 1|2\n"
            "  1: synthetic two-dimensional points\n"
            "  2: Yale Face Database"
        )

    use_toy_data = sys.argv[1] == "1"

    if use_toy_data:
        points = generate_points()
    else:
        points = load_yale_faces(YALE_DIRECTORY)

    n_samples, n_features = points.shape
    max_components = min(n_samples - 1, n_features)

    # Step 2: Perform PCA on the original coordinates.
    pca = PCA(n_components=max_components, svd_solver="full")
    pca_coordinates = pca.fit_transform(points)

    print(f"Data matrix shape: {points.shape}")
    print("Top PCA eigenvalues:")
    print(pca.explained_variance_[:5])

    if use_toy_data:
        plot_embedding(
            points,
            title="Synthetic data and principal directions",
            xlabel="x",
            ylabel="y",
            eigenvalues=pca.explained_variance_,
            eigenvectors=pca.components_.T,
        )

    # Step 3: Compute the pairwise Euclidean distance matrix.
    distance_matrix = cdist(points, points, metric="euclidean")
    plot_matrix(
        distance_matrix,
        title=f"Pairwise distance matrix ({n_samples} × {n_samples})",
        colorbar_label="Euclidean distance",
    )

    # Steps 4-5: Recover the Gram matrix and the Classical MDS coordinates.
    mds_coordinates, mds_eigenvalues, gram_matrix = classical_mds(
        distance_matrix,
        n_components=max_components,
    )

    plot_matrix(
        gram_matrix,
        title=f"Centered Gram matrix ({n_samples} × {n_samples})",
        colorbar_label="Inner-product value",
    )

    print("Top Classical MDS Gram-matrix eigenvalues:")
    print(mds_eigenvalues[:5])

    plot_embedding(
        mds_coordinates,
        title="Classical MDS embedding",
        xlabel="MDS dimension 1",
        ylabel="MDS dimension 2",
    )

    # Step 6: Perform PCA again on the MDS-recovered coordinates.
    recovered_pca = PCA(
        n_components=min(max_components, mds_coordinates.shape[1]),
        svd_solver="full",
    )
    recovered_pca.fit(mds_coordinates)

    print("Top PCA eigenvalues of the MDS-recovered coordinates:")
    print(recovered_pca.explained_variance_[:5])

    plot_embedding(
        mds_coordinates,
        title="PCA applied to the Classical MDS embedding",
        xlabel="MDS dimension 1",
        ylabel="MDS dimension 2",
        eigenvalues=recovered_pca.explained_variance_,
        eigenvectors=recovered_pca.components_.T,
    )

    # The scaling relation expected from the article:
    # eigenvalues(B) = (n_samples - 1) * PCA explained variances.
    comparison_count = min(5, max_components)
    scaled_pca_eigenvalues = (
        pca.explained_variance_[:comparison_count] * (n_samples - 1)
    )
    print("MDS eigenvalues / [(n_samples - 1) × PCA eigenvalues]:")
    print(
        mds_eigenvalues[:comparison_count]
        / scaled_pca_eigenvalues
    )

    plt.show()


if __name__ == "__main__":
    main()
