import pytest

from importlib.util import find_spec
if find_spec("plate_recognizer") is None:
    import sys
    sys.path.append('../..')

from data.kaggle_data import KaggleData
from data.cluster import Cluster

def test_kaggle_data():
    dataset = KaggleData()
    assert dataset is not None
    dataset.prepare_data()

    assert dataset.X is not None
    assert dataset.Y is not None

def test_cluster():
    cluster = Cluster()

    assert cluster is not None

if __name__ == '__main__':
    pytest.main()


