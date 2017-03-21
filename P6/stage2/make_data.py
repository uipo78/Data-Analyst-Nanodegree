import json
import os
import pandas as pd

os.chdir('..')

df = pd.read_csv('orig_data.csv')

target_nodes = [
	'firstBlood', 'firstTower', 'firstInhibitor', 
	'firstRiftHerald', 'firstDragon', 'firstBaron'
]

data = {'nodes': [], 'links': []}

i = 0
for node_name in ['winner'] + target_nodes:
	data['nodes'].extend([
		{'node': i,
		 'name': node_name + '_' + 'False'},
		{'node': i + 1,
		 'name': node_name + '_' + 'True'}
	])
	i += 2

node_map = {item['name']: item['node'] for item in data['nodes']}
grouped_by_winner = df.groupby(['winner'])
for target in target_nodes:
	for group in grouped_by_winner:
		subgrouped = group[1].groupby(target)
		for subgroup in subgrouped:
			data['links'].append({
				'source': node_map['winner' + '_' + str(group[0])],
				'target': node_map[target + '_' + str(subgroup[0])],
				'value': subgroup[1].shape[0]
			})

with open('stage2\\sankey_data.json', 'w+') as fp:
	json.dump(data, fp)
