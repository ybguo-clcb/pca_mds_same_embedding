# Why do PCA and Classical MDS produce the same embedding?
## Coordinates and pairwise distances look like fundamentally different descriptions of data. The Gram matrix reveals why they lead to the same geometry.
PCA and Classical MDS start from fundamentally different inputs. PCA operates directly on data coordinates, whereas Classical MDS requires only pairwise distances. At first glance, there is no obvious reason why the two methods should be closely related.

Surprisingly, for Euclidean data, the two methods can recover equivalent embeddings despite these fundamentally different starting points. Is this merely an algebraic coincidence, or does it reflect a deeper geometric connection?

The key is to stop thinking of PCA and Classical MDS as two competing algorithms and instead view coordinates and pairwise distances as two mathematical descriptions of the same underlying Euclidean point configuration.
## Theoretical Relationship Between PCA and Classical MDS
### A Step-by-Step Comparison
As a brief review, PCA starts from a centered data matrix:

$$
X = [x_1, x_2, \ldots, x_m].
$$

The basic procedure is:

$$
X \rightarrow XX^T \rightarrow XX^T W = W\Lambda,
$$

where the columns of $W = [w_1, w_2, \ldots]$ are the principal directions. Multiplying $XX^T$ by the constant factor $1/(m-1)$ simply converts it into the covariance matrix and does not change the eigenvectors.

Classical MDS takes a different route, starting from a pairwise distance matrix $D$. Although some applications appear to begin with coordinates, these coordinates are used only to construct the pairwise distance matrix. With $D$, it first reconstructs the centered Gram matrix $B$ using

$$
b_{ij} = -\frac{1}{2}\left(d_{ij}^2 - d_{i\cdot}^2 - d_{\cdot j}^2 + d_{\cdot\cdot}^2\right).
$$

After eigen-decomposition,

$$
B = V\Lambda V^T,
$$

the reconstructed coordinates are obtained as

$$
Z = \Lambda^{1/2} V^T,
$$

where the number of retained dimensions is chosen according to the desired embedding dimension.
Therefore, the overall procedure of Classical MDS is

$$
D \rightarrow B \rightarrow V\Lambda V^T \rightarrow Z.
$$

### The MDS Solution Is Not Unique
An important observation is that the coordinate matrix reconstructed by Classical MDS is not the unique solution satisfying

$$
B = Z^T Z.
$$

Given the same distance matrix $D$, there are infinitely many coordinate systems that represent exactly the same point configuration. These coordinate systems may differ by orthogonal transformations, embedding dimensions, or other equivalent representations, while preserving the same pairwise distances.

Classical MDS constructs one particular representation through the following steps.

First, transforming

$$
D \rightarrow B
$$

implicitly assumes that the reconstructed coordinates are centered. In other words, the origin is fixed at the centroid of the point configuration.

Second, after obtaining the centered Gram matrix, there are still infinitely many coordinate matrices satisfying

$$
B=Z^TZ,
$$

possibly with different embedding dimensions. Classical MDS selects the embedding dimension specified by the user.

Finally, among all equivalent coordinate systems, Classical MDS adopts the one generated directly from the eigen-decomposition,

$$
Z = \Lambda^{1/2} V^T.
$$

Therefore, Classical MDS should not simply be regarded as a method for recovering a coordinate representation of the point configuration from pairwise distances. Instead, it selects a canonical coordinate system determined by the eigen-decomposition from an infinite family of equivalent embeddings.
