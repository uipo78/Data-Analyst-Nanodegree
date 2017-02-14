import re

from main import global_constants as gc

COLON_RE = re.compile(r'([a-z]|_)+:([a-z]|_)+')
PROBLEMATIC_RE = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def _corrector(name):
    replaced_incorrect = []
    for elem in name.split(' '):
        if elem in gc.CORRECTOR_MAPPING.keys():
            replaced_incorrect.append(gc.CORRECTOR_MAPPING[elem])
        else:
            replaced_incorrect.append(elem)
    return ' '.join(replaced_incorrect)


def _tags_list_builder(list_, element, default_tag_type):
    for tag in element.iter('tag'):
        tag_has_prob_chars = PROBLEMATIC_RE.search(tag.attrib['k'])
        tag_has_colons = COLON_RE.match(tag.attrib['k'])
        if not tag_has_prob_chars:
            tmp_dict = {'id': element.attrib['id'],
                        'value': _corrector(tag.attrib['v'])}
            if tag_has_colons:
                split = tag.attrib['k'].split(':')
                tmp_dict['key'] = ':'.join(split[1:])
                tmp_dict['type'] = split[0]
            else:
                tmp_dict['key'] = tag.attrib['k']
                tmp_dict['type'] = default_tag_type
            list_.append(tmp_dict)


def shape_element(elem, node_attr_fields=gc.NODE_FIELDS, way_attr_fields=gc.WAY_FIELDS,
                  default_tag_type='regular'):
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []

    if elem.tag == 'node':
        for field in node_attr_fields:
            node_attribs[field] = elem.attrib[field]
        _tags_list_builder(tags, elem, default_tag_type)
        return {'node': node_attribs, 'node_tags': tags}
    elif elem.tag == 'way':
        for field in way_attr_fields:
            way_attribs[field] = elem.attrib[field]
        count = 0
        for nd in elem.iter('nd'):
            tmp_dict = {'id': elem.attrib['id'], 'node_id': nd.attrib['ref'], 'position': count}
            way_nodes.append(tmp_dict)
            count += 1
        _tags_list_builder(tags, elem, default_tag_type)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
