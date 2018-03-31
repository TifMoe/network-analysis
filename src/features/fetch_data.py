from src.data.database.database_functions import connect_mongo, fetch_collections
from configparser import ConfigParser


def fetch_data(min_priority_score):
    """ Function to fetch relevant records from mongo where the node
        priority score falls above the min threshold"""

    config = ConfigParser()
    config.read('config.ini')

    db = connect_mongo(config)
    edges, nodes = fetch_collections(db)

    priority_nodes = list(nodes.find({'priority_score': {'$gte': min_priority_score}}, {'_id': 0}))
    priority_edges = list(edges.find({'priority_score': {'$gte': min_priority_score}}, {'_id': 0}))

    data = {'edges': priority_edges, 'nodes': priority_nodes}

    return data


def rename_target_source(json_list):

    for i in json_list:
        src = i.pop('src')
        dst = i.pop('dst')

        i.update({'source': src})
        i.update({'target': dst})

    return json_list

