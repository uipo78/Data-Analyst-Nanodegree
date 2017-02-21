import csv
import pymongo

from collections import OrderedDict

CSV_PATH = 'Q:\\Program Files\\Programming Applications\\' \
           'Projects\\Udacity\\Data Analysis Nanodegree\\P4\\datasets-csv\\'
CSV_NAME = 'death_location.csv'
# Note that we divide firstBlood_timestamp by 1000 so that
# the timestamp values are in terms of seconds instead of milliseconds.
# Also note that mapId 11 corresponds to Summoner's Rift.
QUERY = [
    {'$match': {'mapId': 11}},
    {'$unwind': '$timeline.frames'},
    {'$unwind': '$timeline.frames.events'},
    {'$match': {'timeline.frames.events.eventType': 'CHAMPION_KILL'}},
    {'$project': {
        '_id': False,
        'x': '$timeline.frames.events.position.x',
        'y': '$timeline.frames.events.position.y',
        'timestamp': {'$divide': ['$timeline.frames.events.timestamp', 1000]}
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
        tmp = [
            ('x', dict_['x']),
            ('y', dict_['y']),
            ('timestamp', dict_['timestamp'])
        ]
        ret_list.append(OrderedDict(tmp))
    return ret_list


def format_to_csv(query_results, csv_out=CSV_PATH+CSV_NAME):
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
