
# Data Wrangling

__Map Area__: New York City area ([See here](https://mapzen.com/data/metro-extracts/metro/new-york_new-york/)) I chose this area because it is where I went to school.

__Note__: 
* The OSM-to-CSV code is NOT included in this document. See the folder 'db_shaper' provided in 'P3'.
* Only a sample of the file 'new-york_new-york.osm' is included in 'P3'. In order to obtain the file in full (whose size is over 2.7GB), you should directly download the file from mapzen.com. Clicking on the link above 'see here' will direct you to the file's source. 


```python
import pprint
import re
import xml.etree.ElementTree as et

from collections import defaultdict

WD = '...'
OSM_FILE = 'new-york_new-york.osm'
```

## Problems Encountered in the Map

After running a few functions that identify irregular entries, I notice two *recurring* issues:
* Inconsistent street types and cardinal directions
* Inconsistent zip codes

Provided below are the functions used to identify the irregularities. Note that all fixes are made via 'db_shaper'.


```python
NOT_NUMBER_RE = re.compile('\D+')
ZIPCODE_RE = re.compile('06|07|08|10|11')
STREET_TYPE_RE = re.compile(r'b\S+\.?$', re.IGNORECASE)
CARDINAL_RE = re.compile('[NESW](\s|\.\s)', re.IGNORECASE)

EXPECTED_CARDINAL = set(['North ', 'East ', 'South ', 'West '])
EXPECTED_STREET = set(['Avenue', 'Bridge', 'Boulevard', 'Commons', 'Court','Drive', 'Lane',
                       'Parkway', 'Place', 'Road', 'Square', 'Street', 'Trail'])


def audit_zipcode(dict_, tag):
    f_all = NOT_NUMBER_RE.findall(tag.attrib['v'])
    if len(f_all) != 0 and set(f_all) != set('-'):
        unexpected_set = set(f_all).difference(set('-'))
        for unexpected in unexpected_set:
            dict_[unexpected].add(tag.attrib['v'])
    else:
        match = ZIPCODE_RE.match(tag.attrib['v'])
        if not match:
            wrong_region = tag.attrib['v'][:2]
            dict_[wrong_region].add(tag.attrib['v'])
                

def audit_street(dict_, tag):
    match = STREET_TYPE_RE.search(tag.attrib['v'])
    if match:
        street_type = match.group()
        if street_type not in EXPECTED_STREET:                
            dict_[street_type].add(tag.attrib['v'])
    match = CARDINAL_RE.match(tag.attrib['v'])
    if match:
        cardinal = match.group()
        if cardinal not in EXPECTED_CARDINAL:
            dict_[cardinal].add(tag.attrib['v'])
            

function_mapping = {'zipcode': audit_zipcode,
                 'street': audit_street}
key_mapping = {'zipcode': 'addr:postcode',
               'street': 'addr:street'}


def is_type(type_to_audit, tag):
    return key_mapping[type_to_audit] == tag.attrib['k']
            

def audit(osm_file, type_to_audit, tags=('node', 'way', 'relation')):
    weirdos = defaultdict(set)
    context = iter(et.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if elem.tag in tags:
            for tag in elem.iter('tag'):
                if is_type(type_to_audit, tag):
                    audit_function = function_mapping[type_to_audit]
                    audit_function(weirdos, tag)
            if event == 'end':
                root.clear()
    pprint.pprint(dict(weirdos))
```

Let's look at the street irregularities first.


```python
audit(osm_file=WD+OSM_FILE, type_to_audit='street')
```

    {'Ballfields': {'John Golden Ballfields'},
     'Bayside': {'Bayside'},
     'Beach': {'Crescent Beach'},
     'Bellerose': {'Hillside Avenue Bellerose'},
     'Blv.': {'John F. Kennedy Blv.'},
     'Blvd': {'Bell Blvd',
              'Bristol Blvd',
              'College Point Blvd',
              'Empire Blvd',
              'Francis Lewis Blvd',
              'Jefryn Blvd',
              'Lukas Blvd',
              'Manorhaven Blvd',
              'Marin Blvd',
              'McLean Blvd',
              'Merrick Blvd',
              'Northern Blvd',
              'Orchard Beach Blvd',
              'Port Washington Blvd',
              'Queens Blvd',
              'Rockaway Blvd',
              'Sunnyside Blvd',
              'Washington Blvd',
              'Woodhaven Blvd',
              'Yellowstone Blvd'},
     'Blvd.': {'JFK Blvd.', 'Rockaway Beach Blvd.'},
     'Bowery': {'The Bowery', 'Bowery'},
     'Box': {'Po Box'},
     'Brandon': {'Brandon'},
     'Broadwat': {'South Broadwat'},
     'Broadway': {'Broadway',
                  'Dutch Broadway',
                  'East Broadway',
                  'North Broadway',
                  'Old Broadway',
                  'South Broadway',
                  'W. Broadway',
                  'West Broadway'},
     'Broadway.': {'Broadway.'},
     'Brooklyn': {'334 Furman St, Brooklyn'},
     'Bush': {'Ploughmans Bush'},
     'Bushwick': {'Bushwick'},
     'E ': {'E 137th St',
            'E 170th St',
            'E 24th Street',
            'E 43rd St',
            'E 45th street',
            'E 50th Street',
            'E 55th St Ste. 301',
            'E 72nd St #LC',
            'E 73rd Street',
            'E 78th Street',
            'E 92nd St',
            'E 95th St',
            'E Garfield',
            'E Gun Hill Rd',
            'E Halsey Rd',
            'E Jericho Turnpike',
            'E Kingsbridge Rd',
            'E Main St',
            'E Park Ave',
            'E Putnam Ave #I',
            'E Ridgewood Ave',
            'E Ridgewood Avenue',
            'E River Rd',
            'E Road',
            'E Route 59'},
     'E. ': {'E. 4th Street',
             'E. 54th St.',
             'E. Broad Street',
             'E. Palisade Avenue'},
     'N ': {'N 7th St',
            'N 9th ST',
            'N Beverwyck Rd',
            'N Broadway #307',
            'N Maple Ave',
            'N Park Ave',
            'N Service Road',
            'N Wood Ave #A'},
     'S ': {'S Park St', 'S Central Avenue', 'S Broadway #2', 'S Oyster Bay Rd #D'},
     'S. ': {'S. Fifth Street'},
     'W ': {'W 26th St',
            'W 27th',
            'W 35th st',
            'W 36th St #800a',
            'W 36th Street',
            'W 47th St #B',
            'W 56th St #1H',
            'W 56th St 2nd Floor',
            'W 57th St',
            'W 69th St., Central Park West',
            'W 71st Street',
            'W 77th Street',
            'W 79th St #2',
            'W Allendale Ave',
            'W Crescent Ave',
            'W Front Street',
            'W Main',
            'W Main St',
            'W Mt Pleasant Ave',
            'W Shore Rd',
            'W front Street'},
     'W. ': {'W. 44th street',
             'W. Broadway',
             'W. Main Street',
             'W. Saint Georges Avenue'},
     'ba': {'Center Drive Malba'},
     'bed': {'4th Avenue Southbound Roadbed',
             'Delancey Street Eb Roadbed',
             'Gateway Drive Westbound Roadbed',
             'Gd Concourse Northbound Roadbed',
             'Hillside Avenue Eb Roadbed',
             'Jamaica Avenue Eastbound Roadbed',
             'Jamaica Avenue Westbound Roadbed',
             'Kings Highway Westbound Roadbed',
             'Linden Boulevard Eb Roadbed',
             'Ocean Parkway Southbound Roadbed',
             'Park Avenue Northbound Roadbed',
             'Pennsylvania Avenue Nb Roadbed',
             'Queens Boulevard Wb Roadbed',
             'Teleport Drive Nb Roadbed',
             'Union Turnpike Eastbound Roadbed'},
     'bhadevi': {'12th Floor, Krypton Tower, Prabhadevi'},
     'bilt': {'Vanderbilt'},
     'boulevard': {'sutphin boulevard'},
     'bus_stop': {'bus_stop'},
     'by': {'Willoughby'}}
    

As you can see, there are several inconsistencies in street types and cardinal directions. These will need to be fixed before formatting the osm file into a csv. In addition, we see mispellings (Broadwat), town names (334 Furmat St, Brooklyn), and some unrecognizable entries (e.g., 'bhadevi'. Is that entry supposed to be in Mumbai?). These too will be fixed before formatting, by: 1) correcting the misspellings; 2) removing the town names; 3) removing the unrecognizable entries.

Now let's examine the zipcodes.


```python
audit(osm_file=WD+OSM_FILE, type_to_audit='zipcode')
```

    {' ': {'07052 '},
     '(': {'(718) 778-0140'},
     ') ': {'(718) 778-0140'},
     '12': {'12'},
     '19': {'19122'},
     '2': {'2'},
     '22': {'22645'},
     '29': {'29201'},
     '3': {'3'},
     '32': {'320'},
     '40': {'40299'},
     '56': {'56'},
     '61': {'61'},
     '74': {'74'},
     '83': {'83'},
     '90': {'90745'},
     '97': {'97657'},
     ';': {'11214;11223', '11201;11231', '11231;11230', '08901-8556;08901'},
     'CT ': {'CT 06870'},
     'NJ': {'NJ'},
     'NJ ': {'NJ 07001',
             'NJ 07036',
             'NJ 07065',
             'NJ 07086',
             'NJ 07102',
             'NJ 07105',
             'NJ 07652',
             'NJ 07747'},
     'NY ': {'NY 10001',
             'NY 10002',
             'NY 10003',
             'NY 10010',
             'NY 10012',
             'NY 10016',
             'NY 10018',
             'NY 10024',
             'NY 10026',
             'NY 10075',
             'NY 10111',
             'NY 10455-1201',
             'NY 10469',
             'NY 10533',
             'NY 10703',
             'NY 11106',
             'NY 11201',
             'NY 11221',
             'NY 11572',
             'NY 11580',
             'NY 11735',
             'NY 11758'},
     'New York, NY ': {'New York, NY 10065'},
     'nj ': {'nj 07652'}}
    

Considering the size of this dataset, there actually aren't many strange zipcode entries. We see a few problematic patterns here: 1) phone numbers instead of zipcodes; 2) strange numbers that aren't nearly long enough to be a zipcode; 3) users who weren't certain about the zipcode to enter (see ';' entries); 4) state abbreviations and cities included with the zipcode.

To fix those problematic patterns, we remove 1-3 entirely, and remove non-numerics parts of any entry belonging to 4.

At this point, we reformat the data (please see the file 'db_shaper' for more information on this process) and upload it to SQLite. Finally we alter the 4 resulting tables so that their characteristics are as follows:

CREATE TABLE nodes(  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;id INTEGER PRIMARY KEY,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lat TEXT,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lon TEXT,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;user TEXT,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;uid TEXT,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;version TEXT,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;changeset TEXT,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;timestamp TEXT  
);  
CREATE TABLE node_tags(  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;id INTEGER,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;key TEXT,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value TEXT,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;type TEXT,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;FOREIGN KEY (id) REFERENCES nodes (id)  
);  
CREATE TABLE ways(  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;id INTEGER PRIMARY KEY,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;user TEXT,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;uid TEXT,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;version TEXT,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;changeset TEXT,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;timestamp TEXT,  
);  
CREATE TABLE ways_nodes(  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;id INTEGER,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;node_id INTEGER,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;position INTEGER,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;FOREIGN KEY (id) REFERNCES ways (id),  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;FOREIGN KEY (node_id) REFERNCES nodes (id),  
);  
CREATE TABLE ways_tags(  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;id INTEGER,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;key TEXT,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;value TEXT,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;type TEXT,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;FOREIGN KEY (id) REFERENCES ways (id)  
);

## Overview of the Data
### Number of nodes

SELECT COUNT(DISTINCT id)  
FROM nodes;

11417150

### Number of ways

SELECT COUNT(DISTINCT id)  
FROM ways;

1787504

### Number of node tags

SELECT COUNT(DISTINCT id)  
FROM nodes_tags;

316893

### Number of way tags

SELECT COUNT(DISTINCT id)  
FROM ways_tags;

1780123

### Number of unique users

CREATE VIEW tmp_view AS  
SELECT uid FROM nodes  
UNION   
SELECT uid FROM ways;  

SELECT COUNT(uid)  
FROM tmp_view;

4438

## Data Exploration
A good many of the node tags are associated with banal places and objects (such as benches). Still there are a few categories that may be of interest. They are considered below.
### Top 5 banks
A common perception in the New York-New Jersey area is that Chase bank appears to be almost everywhere. Indeed, when I lived in New York, there seemed to be a Chase bank at every corner and a Chase atm in every Walgreens and Duane Reade. Let's see if this is true.

CREATE VIEW banks AS  
SELECT DISTINCT(id)  
FROM nodes_tags  
WHERE value='bank';

SELECT nodes_tags.value, COUNT(*) as count  
FROM nodes_tags JOIN banks  
ON nodes_tags.id=banks.id  
WHERE nodes_tags.key='name'  
GROUP BY nodes_tags.value  
ORDER BY count DESC  
LIMIT 5;

Chase|115  
Bank of America|76  
Citibank|61  
TD Bank|49  
Capital One|36  

### Religion with the most places of worship

CREATE VIEW religion AS  
SELECT DISTINCT(id)  
FROM nodes_tags  
WHERE value='place_of_worship';

SELECT nodes_tags.value, COUNT(*) as count  
FROM nodes_tags JOIN religion  
ON nodes_tags.id=religion.id  
WHERE nodes_tags.key='religion'  
GROUP BY nodes_tags.value  
ORDER BY count DESC;

christian|2664  
jewish|194  
muslim|25  
buddhist|9  
hindu|7  
sikh|1

### Most popular type of cuisine for fast food joints
Dollar pizza is a "thing" in New York City. Let's see if pizza makes it to the top.

CREATE VIEW ff AS  
SELECT DISTINCT(id)  
FROM nodes_tags  
WHERE value='fast_food';

SELECT nodes_tags.value, COUNT(*) as count  
FROM nodes_tags JOIN ff  
ON nodes_tags.id=ff.id  
WHERE nodes_tags.key='cuisine'  
GROUP BY nodes_tags.value  
ORDER BY count DESC  
LIMIT 5;

burger|146  
pizza|83  
sandwich|77  
mexican|45  
chicken|28

### Most popular type of cuisine for restaurants

CREATE VIEW restaurants AS  
SELECT DISTINCT(id)  
FROM nodes_tags  
WHERE value='restaurants';

SELECT nodes_tags.value, COUNT(*) as count  
FROM nodes_tags JOIN restaurants  
ON nodes_tags.id=restaurants.id  
WHERE nodes_tags.key='cuisine'  
GROUP BY nodes_tags.value  
ORDER BY count DESC  
LIMIT 5;

italian|206  
american|151  
pizza|148  
mexican|103  
chinese|95

## Conclusion

Following this review, it seems pretty clear that the dataset is not complete and that there likely remain several areas that need to be cleaned. Nevertheless, for the purpose of this analysis, the data was properly scrubbed.

One aspect of the data in its current state which precluded some exploration was that not every node belonging to New York City is given an attribute that identifies the borough in which it is located. So it might be interesting to design an automated process that assigns every node in New York City to its respective borough, based on its geographic coordinates.

The beneifts of implementing such an improvement would be especially valuable for analyzing data belonging to New York City. It would have allowed us to explore, for example, bank popularity by NYC borough: As mentioned above, Chase appears to be ubiquitous—able to be found at nearly every corner in Manhattan. Is this true for the other boroughs? Perhaps Chase has such a presence in Manhattan only.

In designing such a program, you should consider the following items so as to avoid potential issues:
* Really take care to ensure that the geographical coordinates defining each borough are as accurate as possible. It may be surprising that the borough delimiters are not as obvious as one might expect. Examples: To what borough does Rikers Island belong? Are there nodes located in regions in which the borough isn't clearly classified? (Answer: Yes, anything on Ellis Island or Governors Island).
* On the other hand, an extremely precise coordinate definition may not be feasible. Clearly, the boroughs are not simple shapes.

In short, beware of the trade-off between accuracy and feasibility and the issues that may arise from emphasizing one part of the trade-off.
