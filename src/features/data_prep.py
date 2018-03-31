import pickle
import gzip
import os
import pandas as pd
from collections import Counter, defaultdict


def import_pickled_files(directory_path):
    """Utility function to read in files from a folder"""
    all_files = []

    for filename in os.listdir(directory_path):
        with gzip.open(directory_path + "/" + filename, 'rb') as file:
            all_files.extend(pickle.load(file))

    return all_files


all = import_pickled_files('data/archive')


def separate_provider_reviews(all_data):
    """Utility function to unpack list of json and separate reviews dict from provider details"""
    reviews = defaultdict()
    providers = []

    for i, dictionary in enumerate(all_data):
        r = dictionary.pop('reviews')

        reviews[dictionary['id']] = r
        providers.append(dictionary)

    return providers, reviews


p, r = separate_provider_reviews(all)


def construct_reviews_df(reviews_json):
    """Utility function to structure reviews data into table format"""
    list_dicts = []

    month_num_map = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                     'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}

    for i in reviews_json.keys():
        for r in reviews_json[i].keys():
            month = month_num_map[reviews_json[i][r]['date'].split()[-2]]
            year = reviews_json[i][r]['date'].split()[-1]

            new_dict = reviews_json[i][r]
            new_dict['review_date'] = year + '_' + month
            new_dict['provider_id'] = i
            new_dict['user_id'] = reviews_json[i][r]['url'].split('-')[-1]
            list_dicts.append(new_dict)

    return pd.io.json.json_normalize(list_dicts)


reviews_df = construct_reviews_df(r)
providers_df = pd.io.json.json_normalize(p)

# Read in pickled data from pyspark run (can we do that from a .py file in PyCharm?)
with gzip.open('data/edges_df.pkl', 'rb') as file:
    edges_df = pickle.load(file)

with gzip.open('data/vertex_df.pkl', 'rb') as file:
    nodes_df = pickle.load(file)

with gzip.open('data/out_degrees_df.pkl', 'rb') as file:
    out_degrees = pickle.load(file)

# Find most recent review for user -> provider pair and join to edges table as attribute
max_review_pair_df = reviews_df.groupby(['user_id', 'provider_id'], as_index=False)['review_date'].max()
max_date_pair_dict = {(row[0], row[1]): row[2] for (index, row) in max_review_pair_df.iterrows()}

max_reviewer_df = reviews_df.groupby(['user_id'], as_index=False)['review_date'].max()
max_date_reviewer_dict = {row[0]: row[1] for (index, row) in max_reviewer_df.iterrows()}

max_review_provider = reviews_df.groupby(['provider_id'], as_index=False)['review_date'].max()
max_date_provider_dict = {row[0]: row[1] for (index, row) in max_review_provider.iterrows()}


def add_max_date_edges(edges, max_date_pair_dict, max_date_provider_dict):

    # Split edges off by relationship
    reviews = edges.loc[edges['relationship'] == 'reviews', :]
    phones = edges.loc[edges['relationship'] == 'contact_info', :]

    reviews['max_date'] = [max_date_pair_dict[(src, dst)] for (src, dst)
                                                        in zip(reviews['src'], reviews['dst'])]

    # Not every provider with a phone number has an existing review
    phone_date = []
    for dst in phones['dst']:
        try:
            phone_date.append(max_date_provider_dict[dst])
        except KeyError:
            phone_date.append(None)

    phones['max_date'] = phone_date

    return pd.concat([reviews, phones])


new_edges = add_max_date_edges(edges_df, max_date_pair_dict, max_date_provider_dict)
out_degrees_merge = pd.merge(new_edges, out_degrees, how='left', left_on='src', right_on='id')

# Find relationships for providers with a review in 2018
recent_edges = out_degrees_merge.loc[out_degrees_merge['max_date'] > '2017_12', :]
interesting_phones = recent_edges[(recent_edges['relationship']=='contact_info') &
                                  (recent_edges['outDegree'] > 1)].sample(10)

# Find all women linked to these phone numbers
linked_women = pd.merge(pd.DataFrame(interesting_phones['src']),
                        edges_df, how='left', on='src')

relevant_edges = pd.merge(pd.DataFrame(linked_women['dst']),
                          edges_df, how='left', on='dst')


def find_relevant_nodes(relevant_edges, all_nodes):

    src_nodes = pd.merge(pd.DataFrame(relevant_edges['src']),
                         all_nodes, how='left', left_on='src', right_on='id')

    dst_nodes = pd.merge(pd.DataFrame(relevant_edges['dst']),
                         all_nodes, how='left', left_on='dst', right_on='id')

    cols = ['id', 'name', 'type']

    return pd.concat([src_nodes[cols], dst_nodes[cols]])


relevant_nodes = find_relevant_nodes(relevant_edges, nodes_df)
print(relevant_nodes.groupby('type').count())


n = relevant_nodes.drop_duplicates().to_dict('records')

renamed_edges = relevant_edges.rename(columns={'src':'source', 'dst':'target', 'relationship':'type'})
e = renamed_edges.drop_duplicates().to_dict('records')

data = {'nodes': n, 'edges': e}

# Pickle data in format ready for graphing
with open('data/processed/nodes_edges.pkl', 'wb') as file:
    pickle.dump(data, file)




def review_count_edges(list_dictionaries):
    """Takes in a list of dictionaries and creates two lists with and element for every review"""

    providers = []  # (id, name, type)
    reviewer = []  # (id, name, type)

    for i, dictionary in enumerate(list_dictionaries):
        for r in list(dictionary['reviews'].keys()):
            providers.append((dictionary['id'],
                              dictionary['name'],
                              'provider'))
            reviewer.append((dictionary['reviews'][r]['url'].split('-')[-1],
                             dictionary['reviews'][r]['user_name'],
                             'reviewer'))

    nodes = list(set(providers + reviewer))
    all_reviews = [(provider[0], reviewer[0]) for (provider, reviewer) in zip(providers, reviewer)]
    edges = [(node[0], node[1], num_reviews) for (node, num_reviews) in list(Counter(all_reviews).most_common())]

    return nodes, edges


def list_nodes_edges_phone(list_dictionaries):
    """Takes in a list of dictionaries and creates two lists with and element for every review"""

    # Lists for reviews relationship
    providers = []  # (id, name, type)
    reviewer = []  # (id, name, type)

    # Lists for phone number relationship
    providers_num = []
    numbers = []

    for i, dictionary in enumerate(list_dictionaries):

        # Search for reviews
        for r in list(dictionary['reviews'].keys()):
            providers.append((dictionary['id'],
                              dictionary['name'],
                              'provider'))
            reviewer.append((dictionary['reviews'][r]['url'].split('-')[-1],
                             dictionary['reviews'][r]['user_name'],
                             'reviewer'))

        # Search for phone number
        try:
            providers_num.append((dictionary['id'],
                                  dictionary['name'],
                                  'provider'))
            numbers.append((dictionary['contact']['Phone Number'],
                            dictionary['contact']['Phone Number'],
                            'phone_number'))
        except KeyError:
            pass

        try:
            numbers.append((dictionary['contact']['Alt.phone Number'],
                            dictionary['contact']['Alt.phone Number'],
                            'phone_number'))
            providers_num.append((dictionary['id'],
                                  dictionary['name'],
                                  'provider'))
        except KeyError:
            pass

    nodes = list(set(providers + reviewer + providers_num + numbers))
    review_edges = [(reviewer[0], provider[0], 'reviews') for (provider, reviewer) in zip(providers, reviewer)]
    distinct_reviews = [(node[0], node[1], node[2]) for (node, num_reviews) in
                        list(Counter(review_edges).most_common())]
    phone_edges = [(number[0], provider[0], 'contact_info') for (provider, number) in zip(providers_num, numbers)]

    return nodes, (distinct_reviews + phone_edges)


nodes, edges = list_nodes_edges_phone(all)


# Create histogram of review counts
def review_counts_month(all_providers):
    dates = []

    month_num_map = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                     'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

    for i, dictionary in enumerate(all_providers):
        for r in list(dictionary['reviews'].keys()):
            year = dictionary['reviews'][r]['date'].split()[-1]
            month = month_num_map[dictionary['reviews'][r]['date'].split()[-2]]
            dates.append(tuple((year, month)))

    return list(Counter(dates).most_common())


review_dates = review_counts_month(all).sort()

