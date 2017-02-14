#!/usr/bin/env python3
import cerberus
import io

from main import global_constants as gc
from main import shaper_functions as sf
from main.helper import functions as hf

OSM_FILE_NAME = 'new-york_new-york.osm'
DB = 'sql'
VALIDATE = False

READ_DIR = 'Q:\\Program Files\\Programming Applications\\Projects\\Udacity\\Data Analysis Nanodegree\\P3\\db\\'
WRITE_DIR = READ_DIR + DB + '\\'
OSM_PATH = READ_DIR + OSM_FILE_NAME
NODES_PATH = WRITE_DIR + 'nodes.csv'
NODE_TAGS_PATH = WRITE_DIR + 'nodes_tags.csv'
WAYS_PATH = WRITE_DIR + 'ways.csv'
WAY_NODES_PATH = WRITE_DIR + 'ways_nodes.csv'
WAY_TAGS_PATH = WRITE_DIR + 'ways_tags.csv'


def process_map(file_in, validate):
    with io.open(NODES_PATH, 'w', encoding='utf8') as nodes_file, \
            io.open(NODE_TAGS_PATH, 'w', encoding='utf8') as nodes_tags_file, \
            io.open(WAYS_PATH, 'w', encoding='utf8') as ways_file, \
            io.open(WAY_NODES_PATH, 'w', encoding='utf8') as way_nodes_file, \
            io.open(WAY_TAGS_PATH, 'w', encoding='utf8') as way_tags_file:

        nodes_writer = hf.UnicodeDictWriter(nodes_file, gc.NODE_FIELDS)
        node_tags_writer = hf.UnicodeDictWriter(nodes_tags_file, gc.NODE_TAGS_FIELDS)
        ways_writer = hf.UnicodeDictWriter(ways_file, gc.WAY_FIELDS)
        way_nodes_writer = hf.UnicodeDictWriter(way_nodes_file, gc.WAY_NODES_FIELDS)
        way_tags_writer = hf.UnicodeDictWriter(way_tags_file, gc.WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in hf.get_element(file_in, tags=('node', 'way')):
            elem = sf.shape_element(element)
            if elem:
                if validate is True:
                    hf.validate_element(elem, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(elem['node'])
                    node_tags_writer.writerows(elem['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(elem['way'])
                    way_nodes_writer.writerows(elem['way_nodes'])
                    way_tags_writer.writerows(elem['way_tags'])

if __name__ == '__main__':
    process_map(OSM_PATH, validate=VALIDATE)
