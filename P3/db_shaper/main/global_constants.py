NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

CORRECTOR_MAPPING = {'Ave': 'Avenue',
                     'Ave.': 'Avenue',
                     'Broadwat': 'Broadway',
                     'Broadway.': 'Broadway',
                     'Bvld': 'Boulevard',
                     'Bvld.': 'Boulevard',
                     'Bvl.': 'Boulevard',
                     'St.': 'Street',
                     'St': 'Street',
                     'N': 'North',
                     'N.': 'North',
                     'E': 'East',
                     'E.': 'East',
                     'S': 'South',
                     'S.': 'South',
                     'W': 'West',
                     'W.': 'West'}