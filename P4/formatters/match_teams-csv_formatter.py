import csv
import pymongo

from collections import OrderedDict

CSV_PATH = 'Q:\\Program Files\\Programming Applications\\Projects' \
           '\\Udacity\\Data Analysis Nanodegree\\P4\\datasets-csv\\'
CSV_NAME = 'match_teams.csv'
QUERY = [
    {'$unwind': '$teams'},
    {'$project': {
        '_id': False,
        'matchId': True,
        'teams.winner': True,
        'teams.inhibitorKills': True,
        'teams.baronKills': True,
        'teams.firstBaron': True,
        'teams.towerKills': True,
        'teams.firstTower': True,
        'teams.firstBlood': True,
        'teams.riftHeraldKills': True,
        'teams.dragonKills': True,
        'teams.firstInhibitor': True,
        'teams.firstDragon': True,
        'teams.firstRiftHerald': True
    }}
]


def _get_client():
    try:
        ret_client = pymongo.MongoClient('localhost', 27017)
    except pymongo.errors.ConnectionFailure as e:
        print(e)
    else:
        return ret_client


def _tidier(mongo_query):
    ret_list = []
    mongo_list = list(mongo_query)
    for dict_ in mongo_list:
        tmp = [('matchId', dict_['matchId'])]
        tmp.extend(dict_['teams'].items())
        ret_list.append(OrderedDict(tmp))
    return ret_list


def format_to_csv(query_results, csv_out=CSV_PATH + CSV_NAME):
    to_csv = _tidier(query_results)
    keys = to_csv[0].keys()
    with open(csv_out, 'w+', newline='', encoding='utf-8') as output_csv:
        dict_writer = csv.DictWriter(output_csv, keys)
        dict_writer.writeheader()
        dict_writer.writerows(to_csv)


if __name__ == '__main__':
    client = _get_client()
    db = client.seed_lol
    query = db.matches.aggregate(QUERY)
    format_to_csv(query_results=query)
    client.close()
