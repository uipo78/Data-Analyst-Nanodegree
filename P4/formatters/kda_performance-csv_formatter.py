import csv
import pymongo

from collections import OrderedDict

CSV_PATH = 'Q:\\Program Files\\Programming Applications\\' \
           'Projects\\Udacity\\Data Analysis Nanodegree\\P4\\datasets-csv\\'
CSV_NAME = 'kda_performance.csv'
QUERY = [
    {'$unwind': '$participantIdentities'},
    {'$unwind': '$participants'},
    {'$redact': {
        '$cond': [
            {'$eq': ['$participantIdentities.participantId',
                     '$participants.participantId']},
            '$$KEEP',
            '$$PRUNE'
        ]
    }},
    {'$group': {
        '_id': '$participantIdentities.player.summonerId',
        'avg kills': {'$avg': '$participants.stats.kills'},
        'avg deaths': {'$avg': '$participants.stats.deaths'},
        'avg assists': {'$avg': '$participants.stats.assists'},
        'avg performance': {
            '$avg': {
                '$cond': [
                    {'$and': [{'$eq': ['$participants.stats.kills', 0]},
                              {'$eq': ['$participants.stats.assists', 0]},
                              {'$eq': ['$participants.stats.deaths', 0]}]},
                    0,
                    {'$divide': [
                        {'$subtract': [
                            {'$add': ['$participants.stats.kills',
                                      '$participants.stats.assists']},
                            '$participants.stats.deaths'
                        ]},
                        {'$add': [
                            '$participants.stats.kills',
                            '$participants.stats.assists',
                            '$participants.stats.deaths'
                        ]}
                    ]}
                ]
            }
        },
        'highestAchievedSeasonTier': {
            '$first': '$participants.highestAchievedSeasonTier'
        }
    }},
    {'$project': {
        '_id': False,
        'summonerId': '$_id',
        'participants.highestAchievedSeasonTier': True,
        'avg kills': True,
        'avg deaths': True,
        'avg assists': True,
        'avg performance': True,
        'highestAchievedSeasonTier': True
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
            ('summonerId', dict_['summonerId']),
            ('highestAchievedSeasonTier', dict_['highestAchievedSeasonTier']),
            ('avg kills', dict_['avg kills']),
            ('avg deaths', dict_['avg deaths']),
            ('avg assists', dict_['avg assists']),
            ('avg performance', dict_['avg performance'])
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
