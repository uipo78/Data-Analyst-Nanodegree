import json
import pandas as pd

df = pd.read_csv('data\\orig_data.csv')

source_target_pairs = [
	('firstBlood', 'firstTower'), ('firstTower', 'firstInhibitor'),
	('firstInhibitor', 'firstRiftHerald'), ('firstRiftHerald', 'firstDragon'),
	('firstDragon', 'firstBaron'), ('firstBaron', 'winner')
]

data = {'nodes': [], 'links': []}

i = 0
node_names = [p[0] for p in source_target_pairs] + ['winner']
for node_name in node_names:
	data['nodes'].extend([
		{'node': i,
		 'name': node_name + '_' + 'False'},
		{'node': i + 1,
		 'name': node_name + '_' + 'True'}
	])
	i += 2

node_map = {item['name']: item['node'] for item in data['nodes']}
for source, target in source_target_pairs:
	grouped = df.groupby(source)
	for group in grouped:
		subgrouped = group[1].groupby(target)
		for subgroup in subgrouped:
			data['links'].append({
				'source': node_map[source + '_' + str(group[0])],
				'target': node_map[target + '_' + str(subgroup[0])],
				'value': subgroup[1].shape[0]
			})

with open('data\\sankey_data.json', 'w+') as fp:
	json.dump(data, fp)