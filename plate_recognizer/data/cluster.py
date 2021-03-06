import numpy as np

from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from scipy.spatial.distance import cdist

from FSDL.plate_recognizer.utils.logger import get_logger

logger = get_logger(__name__)


class Cluster():
    def __init__(self, dimensions=2):
        self.dimensions = dimensions

    def get_pca_reduced(self, X_train):
        X_train_flatten = X_train.reshape(X_train.shape[0], -1)
        pca = PCA(self.dimensions)

        X_train_pca_reduced = pca.fit_transform(X_train_flatten)

        return X_train_pca_reduced, pca
    
    def get_clusters(self, X_train_pca_reduced, K):
        kmeans = KMeans(n_clusters=K, random_state=0)
        X_train_pca_clusters = kmeans.fit(X_train_pca_reduced)

        return X_train_pca_clusters, kmeans

    def get_feature_map_clusters(self, X, K):
        """
        param X: input data
        param K: number of clusters
        returns: X_clusters - clustered input data

        (side effect): plots the frequency histogram of clusters
        """
        X_fm, _ = self.get_feature_maps(X)
        # use cosine distance to find similarities
        X_fm_normalized = preprocessing.normalize(X_fm.reshape(len(X_fm), -1))

        return self.get_clusters(X_fm_normalized)

    @staticmethod
    def to_cluster_idx(cluster_labels, bins):
        """
        param bins: range of K
        param labels: cluster labels
        returns: dictionary of cluster IDs
        """
        cluster_dict = dict()
        for cluster_id in bins:
            cluster_dict[cluster_id] = np.where(cluster_labels == cluster_id)[0]
        return cluster_dict

    @staticmethod
    def to_clusters_dict(X, y, X_clusters, K):
        """
        given X_clusters, put X & y into the correct clusters
        and return the dictionary
        """
        cluster_idx = to_cluster_idx(X_clusters.labels_, range(K))

        X_dict = {}
        y_dict = {}
        for id in range(K):
            ids = cluster_idx[id]
            X_dict[id] = X[ids]
            y_dict[id] = y[ids]

        return X_dict, y_dict

    @staticmethod
    def get_merged_data(clusters_d, id=-1):
        if id != -1:
            return clusters_d[id]
        else:
            merged = []
            for cluster_id, cluster in clusters_d.items():
                if cluster_id == 0:
                    merged = cluster
                else:
                    merged = np.hstack((merged, cluster))

            return merged

    @staticmethod
    def find_duplicates(X_train_pca, threshold=0.1):
        # Calculate distances of all points
        distances = cdist(X_train_pca, X_train_pca)

        # Find duplicates (very similar images)
        # dupes = np.array([np.where(distances[id] < 1) for id in range(distances.shape[0])]).reshape(-1)
        dupes = [np.array(np.where(distances[id] < threshold)).reshape(-1).tolist() \
                for id in range(distances.shape[0])]

        to_remove = set()
        for d in dupes:
            if len(d) > 1:
                for id in range(1, len(d)):
                    to_remove.add(d[id])
        logger.info("Found {} duplicates".format(len(to_remove)))
        return to_remove

    @staticmethod
    def find_k(X, bins, distance_fn='euclidean'):
        """
        Adapted from https://www.geeksforgeeks.org/elbow-method-for-optimal-value-of-k-in-kmeans/
        """
        distortions = []
        inertias = []
        mapping1 = {}
        mapping2 = {}

        # Building and fitting the model
        for k in bins:
            kmeanModel = KMeans(n_clusters=k).fit(X)
            kmeanModel.fit(X)

        distortions.append(sum(np.min(cdist(X, kmeanModel.cluster_centers_,
                                            distance_fn), axis=1)) / X.shape[0])
        inertias.append(kmeanModel.inertia_)

        mapping1[k] = sum(np.min(cdist(X, kmeanModel.cluster_centers_,
                                        distance_fn), axis=1)) / X.shape[0]
        mapping2[k] = kmeanModel.inertia_

        return mapping1, mapping2, K, inertias, distortions
    """
    mapping1, mapping2, K, inertias, distortions = find_k(X.reshape(len(X),-1))
    print("Elbow", mapping1)
    print("mapping2", mapping2)
    Elbow {10: 104.03249749637331, 11: 103.10312352976362, 12: 101.6067859189693, 13: 102.26749001212667, 14: 100.82706764423298}
    mapping2 {10: 4814616.603107566, 11: 4737997.623679198, 12: 4730363.9842358045, 13: 4692806.712752489, 14: 4614212.104605412}

    plt.plot(K, distortions, 'bx-')
    plt.xlabel('Values of K')
    plt.ylabel('Distortion')
    plt.title('The Elbow Method using Distortion')
    plt.show()

    Using cosine similarity: https://stackoverflow.com/questions/63018098/deep-learning-with-python-cosine-similarity
    """


from keras.applications.vgg16 import VGG16
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input, decode_predictions
import numpy as np
import os
import sys

#Calculate similar matrics
def cosine_similarity(ratings):
    sim = ratings.dot(ratings.T)
    if not isinstance(sim,np.ndarray):
        sim = sim.toarray()
    norms = np.array([np.sqrt(np.diagonal(sim))])
    return (sim/norms/norms.T)

def get_feature_maps(X):
    #Convert to VGG input format 
    x_test = preprocess_input(X)

    #include_top=False == not getting VGG16 last 3 layers
    model = VGG16(weights = "imagenet", include_top=False)

    #Get features
    features = model.predict(x_test)

    return model, features

    # #Calculate similar metrics
    # features_compress = features.reshape(len(y_test), 7*7*512)
    # sim = cosine_similarity(features_compress)

def display_feature_maps(features):
    feature_maps = [features]

    # Retrieve are the names of the layers, so can have them as part of our plot
    layer_names = [layer.name for layer in model_vgg16.layers]
    for layer_name, feature_map in zip(layer_names, feature_maps):
        print(layer_name, feature_map.shape)
        if len(feature_map.shape) == 4:

            n_features = feature_map.shape[-1]  # number of features in the feature map
            size       = feature_map.shape[ 1]  # feature map shape (1, size, size, n_features)

            # We will tile our images in this matrix
            display_grid = np.zeros((size, size * n_features))

            # Postprocess the feature to be visually palatable
            for i in range(n_features):
                x  = feature_map[0, :, :, i]
                x -= x.mean()
                x /= x.std ()
                x *=  64
                x += 128
                x  = np.clip(x, 0, 255).astype('uint8')
                # Tile each filter into a horizontal grid
                display_grid[:, i * size : (i + 1) * size] = x

            # Display the grid
            scale = 20. / n_features
            plt.figure( figsize=(scale * n_features, scale) )
            plt.title ( 'feature' )
            plt.grid  ( False )
            plt.imshow( display_grid, aspect='auto', cmap='viridis' )

from sklearn import preprocessing  # to normalise existing X
def get_top_n_similar_images(features, n=10):
    features_norm = preprocessing.normalize(features.reshape(len(features), -1))
    kmeans_features = KMeans(n_clusters=11, random_state=0).fit(features_norm)

    features_compress = features.reshape(features.shape[0],
                                     features.shape[1]*features.shape[2]*features.shape[3])
    similarities = cosine_similarity(features_compress)

    topn_sim = np.argsort(-similarities[n], axis=0)[0:12]
    topn_sim


#####
# Better PCA
# https://gtraskas.github.io/post/ex7/

import scipy.linalg as linalg

# Create a function to normalize features.
def featureNormalize(X):
    """
    Returns a normalized version of X where the mean
    value of each feature is 0 and the standard deviation
    is 1. This is often a good preprocessing step to do
    when working with learning algorithms.
    Args:
        X     : array(# of training examples, n)
    Returns:
        X_norm: array(# of training examples, n)
        mu    : array(n,)
        sigma : array(n,)
    """
    mu = np.mean(X, axis=0)
    X_norm = X - mu
    # Set Delta Degrees of Freedom (ddof) to 1, to compute
    # the std based on a sample and not the population.
    sigma = np.std(X_norm, axis=0, ddof=1)
    X_norm = X_norm / sigma
    
    return X_norm, mu, sigma

# Create a function to compute the eigenvectors and eigenvalues.
def pca(X):
    """
    Returns the eigenvectors U, the eigenvalues (on diagonal) in S.
    Args:
        X: array(# of training examples, n)
    Returns:
        U: array(n, n)
        S: array(n, n)
    """
    # Get some useful values
    m, n, _, _ = X.shape
    
    # Init U and S.
    U = np.zeros(n)
    S = np.zeros(n)
    
    # When computing the covariance matrix, we have
    # to divide by m (the number of examples).
    sigma = (1. / m) * np.dot(X.T, X)
    
    # Compute the eigenvectors and eigenvalues
    # of the covariance matrix.
    U, S, V = linalg.svd(sigma)
    S = linalg.diagsvd(S, len(S), len(S))

    return U, S


def execute_better_pca():
    print('Running PCA on face dataset...')

    # Before running PCA, it is important to first normalize X
    # by subtracting the mean value from each feature.
    X_norm, mu, _ = featureNormalize(X_train)

    # Run PCA.
    U, S = pca(X_norm)

    # Visualize the top 36 eigenvectors found.
    displayData(U.T, 6)

    # Normalize X.
    X_norm, mu, _ = featureNormalize(X)

    # Run PCA.
    U, S = pca(X_norm)

    # Draw the eigenvectors centered at mean of data. These lines show the
    # directions of maximum variations in the dataset.
    plt.figure(figsize=(6, 6))
    plt.scatter(X[:,0], X[:,1], edgecolors='b', facecolors='none')
    plt.title("Figure 2: Computed eigenvectors of the dataset.")
    # Compute the pairs of points to draw the lines.
    p1 = mu
    p2 = mu + 1.5 * S[0,0] * U[:,0].T
    p3 = mu + 1.5 * S[1,1] * U[:,1].T
    plt.plot([p1[0], p2[0]], [p1[1], p2[1]], c='k', linewidth=2)
    plt.plot([p1[0], p3[0]], [p1[1], p3[1]], c='k', linewidth=2)
    plt.show()

    print('Top eigenvector:')
    print('U[:,0]= {:f} {:f}'.format(U[0,0], U[1,0]))
    print('(expected to see -0.707107 -0.707107)')

## 3d plotting
## X_train_pca_3d = to_pca_3d(X_train, y_train)