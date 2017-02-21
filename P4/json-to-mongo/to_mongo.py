import json
import pymongo

DATA_DIR = 'Q:\\Program Files\\Programming Applications\\Projects\\Udacity\\' \
           'Data Analysis Nanodegree\\P4\\json-to-mongo\\json files'


def _get_client():
    try:
        ret_client = pymongo.MongoClient('localhost', 27017)
    except pymongo.errors.ConnectionFailure as e:
        print(e)
    else:
        return ret_client


def matches_to_mongo(data_dir=DATA_DIR):
    for n in range(1, 11):
        with open(data_dir + 'matches{0}.json'.format(n)) as f:
            data = json.load(f)
            db.matches.insert_many(data['matches'])


def champs_to_mongo(data_dir=DATA_DIR):
    with open(data_dir + 'champion.json') as f:
        data = json.load(f)
        db.champions.insert(data)


if __name__ == '__main__':
    client = _get_client()
    db = client.seed_lol
    matches_to_mongo()
    champs_to_mongo()
    client.close()
