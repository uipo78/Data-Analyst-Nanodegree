import csv
import pymongo

CSV_PATH = 'Q:\\Program Files\\Programming Applications\\' \
           'Projects\\Udacity\\Data Analysis Nanodegree\\P4\\datasets-csv\\'
CSV_NAME = 'firstBlood_times.csv'
# Note that we divide firstBlood_timestamp by 1000 so that
# the timestamp values are in terms of seconds instead of milliseconds.
QUERY = [
    {'$unwind': '$timeline.frames'},
    {'$unwind': '$timeline.frames.events'},
    {'$match': {'timeline.frames.events.eventType': 'CHAMPION_KILL'}},
    {'$group': {
        '_id': '$matchId',
        'firstBlood_timestamp': {'$min': '$timeline.frames.events.timestamp'}
    }},
    {'$project': {
        '_id': False,
        'matchId': '$_id',
        'firstBlood_timestamp': {'$divide': ['$firstBlood_timestamp', 1000]}
    }}
]


def _get_client():
    try:
        ret_client = pymongo.MongoClient('localhost', 27017)
    except pymongo.errors.ConnectionFailure as e:
        print(e)
    else:
        return ret_client


def format_to_csv(query_results, csv_out=CSV_PATH+CSV_NAME):
    to_csv = list(query_results)
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
