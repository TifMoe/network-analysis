import pickle


def get_data():
    """Utility function to fetch json from pickled file"""
    with open("data/processed/nodes_edges.pkl", "rb") as f:
        data = pickle.load(f)

    return data

