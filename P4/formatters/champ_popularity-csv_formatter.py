import csv
import pymongo

from collections import OrderedDict

CSV_PATH = 'Q:\\Program Files\\Programming Applications\\' \
           'Projects\\Udacity\\Data Analysis Nanodegree\\P4\\datasets-csv\\'
CSV_NAME = 'champ_popularity.csv'
QUERY = [
    {'$unwind': '$participants'},
    {'$group': {
        '_id': '$participants.championId',
        'total': {'$sum': 1},
        'tierArray': {'$push': '$participants.highestAchievedSeasonTier'}
    }},

    {'$project': {
        '_id': False,
        'championId': '$_id',
        'unranked count': {
            '$size': {
                '$filter': {
                    'input': '$tierArray',
                    'as': 'tier',
                    'cond': {'$eq': ['$$tier', 'UNRANKED']}
                }
            }
        },
        'bronze count': {
            '$size': {
                '$filter': {
                    'input': '$tierArray',
                    'as': 'tier',
                    'cond': {'$eq': ['$$tier', 'BRONZE']}
                }
            }
        },
        'silver count': {
            '$size': {
                '$filter': {
                    'input': '$tierArray',
                    'as': 'tier',
                    'cond': {'$eq': ['$$tier', 'SILVER']}
                }
            }
        },
        'gold count': {
            '$size': {
                '$filter': {
                    'input': '$tierArray',
                    'as': 'tier',
                    'cond': {'$eq': ['$$tier', 'GOLD']}
                }
            }
        },
        'platinum count': {
            '$size': {
                '$filter': {
                    'input': '$tierArray',
                    'as': 'tier',
                    'cond': {'$eq': ['$$tier', 'PLATINUM']}
                }
            }
        },
        'diamond count': {
            '$size': {
                '$filter': {
                    'input': '$tierArray',
                    'as': 'tier',
                    'cond': {'$eq': ['$$tier', 'DIAMOND']}
                }
            }
        },
        'master count': {
            '$size': {
                '$filter': {
                    'input': '$tierArray',
                    'as': 'tier',
                    'cond': {'$eq': ['$$tier', 'MASTER']}
                }
            }
        },
        'challenger count': {
            '$size': {
                '$filter': {
                    'input': '$tierArray',
                    'as': 'tier',
                    'cond': {'$eq': ['$$tier', 'CHALLENGER']}
                }
            }
        },
        'total': True
    }}
]
PROJECTION = {
    '_id': False,
    'data': True
}


def _get_client():
    try:
        ret_client = pymongo.MongoClient('localhost', 27017)
    except pymongo.errors.ConnectionFailure as e:
        print(e)
    else:
        return ret_client


# Makes a dictionary whose keys are championId and whose columns are
# the respective champion's name.
def _champ_mapping_maker(query_results):
    ret_dict = {}
    champ_doc = query_results[0]['data']
    for key in champ_doc.keys():
        ret_dict[int(champ_doc[key]['key'])] = champ_doc[key]['name']
    return ret_dict


def _tidier(agg_query, map_query):
    ret_list = []
    mongo_list = list(agg_query)
    mapping = _champ_mapping_maker(map_query)
    for dict_ in mongo_list:
        tmp = [
            ('champion name', mapping[dict_['championId']]),
            ('unranked', dict_['unranked count']),
            ('bronze', dict_['bronze count']),
            ('silver', dict_['silver count']),
            ('gold', dict_['gold count']),
            ('platinum', dict_['platinum count']),
            ('diamond', dict_['diamond count']),
            ('master', dict_['master count']),
            ('challenger', dict_['challenger count']),
            ('total', dict_['total'])
        ]
        ret_list.append(OrderedDict(tmp))
    return ret_list


def format_to_csv(agg_query, map_query, csv_out=CSV_PATH+CSV_NAME):
    to_csv = _tidier(agg_query, map_query)
    keys = to_csv[0].keys()
    with open(csv_out, 'w+', newline='', encoding='utf-8') as output_csv:
        dict_writer = csv.DictWriter(output_csv, keys)
        dict_writer.writeheader()
        dict_writer.writerows(to_csv)


if __name__ == '__main__':
    client = _get_client()
    db = client.seed_lol
    query0 = db.matches.aggregate(QUERY)
    query1 = db.champions.find(projection=PROJECTION)
    format_to_csv(agg_query=query0, map_query=query1)
    client.close()
