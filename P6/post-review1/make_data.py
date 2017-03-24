import json
import os
import pandas as pd

os.chdir('..')

df = pd.read_csv('orig_data.csv')

target_nodes = [
	'firstTower', 'firstInhibitor', 
	'firstRiftHerald', 'firstDragon', 'firstBaron'
]

data = {'nodes': [], 'links': []}

i = 0
for node_name in ['winner'] + target_nodes:
	if node_name == 'winner':
		data['nodes'].extend([
			{'node': i,
			 'name': node_name + '_' + 'False'},
			{'node': i + 1,
			 'name': node_name + '_' + 'True'}
		])
		i += 2
	else:
		data['nodes'].append({
			'node': i,
			'name': node_name
		})
		i += 1

node_map = {item['name']: item['node'] for item in data['nodes']}
grouped_by_winner = df.groupby(['winner'])
for target in target_nodes:
	for group in grouped_by_winner:
		data['links'].append({
			'source': node_map['winner' + '_' + str(group[0])],
			'target': node_map[target],
			'value': group[1].loc[group[1][target] == True, :].shape[0]
		})

with open('post-review1\\sankey_data.json', 'w+') as fp:
	json.dump(data, fp)
