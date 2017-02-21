import csv
import pymongo

from collections import defaultdict, OrderedDict

CSV_PATH = 'Q:\\Program Files\\Programming Applications\\' \
           'Projects\\Udacity\\Data Analysis Nanodegree\\P4\\datasets-csv\\'
CSV_NAME = 'levelUp_times.csv'
# Note that we divide firstBlood_timestamp by 1000 so that
# the timestamp values are in terms of seconds instead of milliseconds.
QUERY = [
    {'$unwind': '$timeline.frames'},
    {'$unwind': '$timeline.frames.events'},
    {'$match': {'timeline.frames.events.eventType': 'SKILL_LEVEL_UP'}},
    {'$unwind': '$participants'},
    {'$project': {
        '_id': False,
        'matchId': True,
        'highestAchievedSeasonTier': '$participants.highestAchievedSeasonTier',
        'championId': '$participants.championId',
        'participantId': '$participants.participantId',
        'levelUpType': '$timeline.frames.events.levelUpType',
        'eventParticipantId': '$timeline.frames.events.participantId',
        'skillSlot': '$timeline.frames.events.skillSlot',
        'timestamp': {'$divide': ['$timeline.frames.events.timestamp', 1000]}
    }},
    {'$redact': {
        '$cond': [
            {'$eq': ['$participantId', '$eventParticipantId']},
            '$$KEEP',
            '$$PRUNE'
        ]
    }}
]


def _get_client():
    try:
        ret_client = pymongo.MongoClient('localhost', 27017)
    except pymongo.errors.ConnectionFailure as e:
        print(e)
    else:
        return ret_client

# Tidies and adds 'lvlAchieved' field
def _tidier(mongo_query):
    counter = defaultdict(int)
    match_id = 0
    mongo_list = list(mongo_query)
    ret_list = []
    for dict_ in mongo_list:
        if match_id != dict_['matchId']:
            match_id = dict_['matchId']
            counter.clear()
        counter[dict_['participantId']] += 1
        tmp = [
            ('matchId', dict_['matchId']),
            ('participantId', dict_['participantId']),
            ('highestAchievedSeasonTier', dict_['highestAchievedSeasonTier']),
            ('timestamp', dict_['timestamp']),
            ('lvlAchieved', counter[dict_['participantId']] + 1),
            ('championId', dict_['championId']),
            ('skillSlot', dict_['skillSlot']),
            ('levelUpType', dict_['levelUpType'])
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
