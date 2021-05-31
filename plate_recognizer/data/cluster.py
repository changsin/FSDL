import numpy as np

from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from scipy.spatial.distance import cdist


class Cluster():
    def __init__(self, dimensions=2):
        self.dimensions = dimensions

    def get_pca(self, X_train, y_train):
        X_train_flatten = X_train.reshape(X_train.shape[0], -1)
        pca = PCA(self.dimensions)

        X_train_pca = pca.fit_transform(X_train_flatten)

        return X_train_pca, pca
    
    def get_clusters(self, X_train_pca, K):
        kmeans = KMeans(n_clusters=K, random_state=0)
        X_train_pca_clusters = kmeans.fit(X_train_pca)

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

    def to_cluster_idx(self, bins, labels):
        """
        param bins: range of K
        param labels: cluster labels
        returns: dictionary of cluster IDs
        """
        cluster_dict = dict()
        for cluster_id in bins:
            cluster_dict[cluster_id] = np.where(labels == cluster_id)[0]
        return cluster_dict

    def to_clusters_dict(self, X, y, X_clusters, K):
        """
        given X_clusters, put X & y into the correct clusters
        and return the dictionary
        """
        X_cluster_idx = self.to_cluster_idx(range(K), X_clusters.labels_)

        X_dict = {}
        y_dict = {}
        for id in range(K):
            ids = X_cluster_idx[id]
            X_dict[id] = X[ids]
            y_dict[id] = y[ids]

        return X_dict, y_dict

    def find_duplicates(self, X_train_pca):
        # Calculate distances of all points
        distances = cdist(X_train_pca, X_train_pca)

        # Find duplicates (very similar images)
        # dupes = np.array([np.where(distances[id] < 1) for id in range(distances.shape[0])]).reshape(-1)
        dupes = [np.array(np.where(distances[id] < 1)).reshape(-1).tolist() \
                for id in range(distances.shape[0])]

        to_remove = set()
        for d in dupes:
            if len(d) > 1:
                for id in range(1, len(d)):
                    to_remove.add(d[id])
        print("Found {} duplicates".format(len(to_remove)))
        return to_remove

    def partition_on_clusters(self, X_d, y_d, bins, val_size=0.1, test_size=0.2):
        X_train_d = dict()
        y_train_d = dict()
        X_val_d = dict()
        y_val_d = dict()
        X_test_d = dict()
        y_test_d = dict()

        # for each cluster reserve test_size portion for test data
        for id in bins:
            Xt_train, Xt_test, yt_train, yt_test = \
            train_test_split(X_d[id], y_d[id], test_size=0.2, shuffle=False)
            Xt_train, Xt_val, yt_train, yt_val = \
            train_test_split(Xt_train, yt_train, test_size=0.1, shuffle=False)

            X_train_d[id] = Xt_train
            y_train_d[id] = yt_train

            X_val_d[id] = Xt_val
            y_val_d[id] = yt_val

            X_test_d[id] = Xt_test
            y_test_d[id] = yt_test

        return X_train_d, y_train_d, \
                X_val_d, y_val_d, \
                X_test_d, y_test_d