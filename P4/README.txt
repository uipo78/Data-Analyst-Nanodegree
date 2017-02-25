# About the data
The data in the directory "json file" was obtained from Riot's developer webpage 
(navigate https://developer.riotgames.com/docs/getting-started to "Seed Data" for the source). 
To see a sample of the raw data structure, please see sample-match_doc.json in P4.

# Handling the data
The data was entered into a local Mongo database in order to make extracting relevant information easier. 
Data resulting from all Mongo queries were dumped into separate csv files, which are located in datasets-csv. 
Please see "to_mongo.py" in "json-to-mongo" and the contents of "formatters" in order to examine the python scripts 
that perform the aforementioned processes.

The six files in "formatters" generate the six csv files in "datasets-csv"

# About data_exploration_files
This file only exists so that the analysis can be displayed on github. For any other purpose, you may ignore it.
