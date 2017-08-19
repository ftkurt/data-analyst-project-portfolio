
# Introduction

The largest city in Turkey that I am familiar with is İstanbul. Therefore, I thought I could look at the map and check if I can catch anything of significance. 


```python
import xml.etree.cElementTree as ET
import pandas as pd
import pprint
import bz2
```


```python
DATA_FILE = "istanbul_turkey.osm"
```


```python
bz2_data = bz2.BZ2File(DATA_FILE+".bz2").read()
open(DATA_FILE, 'wb').write(bz2_data)
```

I want to first check my data to see what hierarchy it has. Below functions will extract tags and hierarchy in my dataset. It will also extract attributes and child tags for each tag residing within our XML file. 


```python
def getTags(filename):
    tags = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag not in tags:
            tags[elem.tag] = 0
        tags[elem.tag] += 1
    return tags
```


```python
def print_element_info(elem):
    print elem.tag+" sample (first encounter):"
    info = {}
    for attr in elem.attrib:
        info[attr] = elem.attrib[attr]
    print info
```


```python
# This function will traverse attributes and childs for each tag type. It will also print each tag first time it is encountered.
def define_file(filename):
    tags = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag not in tags:
            print_element_info(elem)
            tags[elem.tag] = {"count":0,"attribs":set(),"childs":set()}
        tags[elem.tag]["count"] += 1
        for attr in elem.attrib:
            tags[elem.tag]["attribs"].add(attr)
        for elem_ in elem.getiterator():
            if elem_ != elem:
                tags[elem.tag]["childs"].add(elem_.tag)
    return tags
```


```python
file_tag_stats = define_file(DATA_FILE)
```

    bounds sample (first encounter):
    {'minlat': '40.738', 'maxlon': '29.678', 'minlon': '28.313', 'maxlat': '41.421'}
    tag sample (first encounter):
    {'k': 'highway', 'v': 'motorway_junction'}
    node sample (first encounter):
    {'changeset': '11617084', 'uid': '683385', 'timestamp': '2012-05-16T19:43:19Z', 'lon': '29.047924', 'version': '5', 'user': 'nucularbum', 'lat': '41.0222538', 'id': '21107200'}
    nd sample (first encounter):
    {'ref': '482245611'}
    way sample (first encounter):
    {'changeset': '12637783', 'uid': '136321', 'timestamp': '2012-08-06T19:32:43Z', 'version': '14', 'user': 'Teddy73', 'id': '4341858'}
    member sample (first encounter):
    {'role': 'city', 'ref': '1882099475', 'type': 'node'}
    relation sample (first encounter):
    {'changeset': '39135345', 'uid': '2263457', 'timestamp': '2016-05-06T05:55:12Z', 'version': '33', 'user': 'tbolat', 'id': '10692'}
    osm sample (first encounter):
    {'timestamp': '2017-07-19T15:02:02Z', 'version': '0.6', 'generator': 'osmconvert 0.8.5'}
    


```python
df = pd.DataFrame(file_tag_stats)
df
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>bounds</th>
      <th>member</th>
      <th>nd</th>
      <th>node</th>
      <th>osm</th>
      <th>relation</th>
      <th>tag</th>
      <th>way</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>attribs</th>
      <td>{minlat, maxlon, minlon, maxlat}</td>
      <td>{role, ref, type}</td>
      <td>{ref}</td>
      <td>{changeset, uid, timestamp, lon, version, user...</td>
      <td>{timestamp, version, generator}</td>
      <td>{changeset, uid, timestamp, version, user, id}</td>
      <td>{k, v}</td>
      <td>{changeset, uid, timestamp, version, user, id}</td>
    </tr>
    <tr>
      <th>childs</th>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{tag}</td>
      <td>{node, nd, bounds, member, tag, relation, way}</td>
      <td>{member, tag}</td>
      <td>{}</td>
      <td>{tag, nd}</td>
    </tr>
    <tr>
      <th>count</th>
      <td>1</td>
      <td>8034</td>
      <td>1498568</td>
      <td>1164528</td>
      <td>1</td>
      <td>694</td>
      <td>370703</td>
      <td>192562</td>
    </tr>
  </tbody>
</table>
</div>



From above table we can see that the main tag types are **tags**, **ways**, **nodes**, and **nds**. I am going to ignore nd types since they only provide some references. 


```python
df["node"].attribs
```




    {'changeset', 'id', 'lat', 'lon', 'timestamp', 'uid', 'user', 'version'}



Historically, Istanbul had been a very diverse city. Until recent decades, there were a large number of followers of different religions, particularly Ortodox Christians. Therefore, I would like to explore into religious places in Istanbul, and see what is current distribution of religious places in Istanbul. This data might provide insight into proportion of Istanbulites into different religious groups. 

I do not know what types of places are there which are tagged as religious, so I think I should first look into nodes/ways tagged with religion key.

Functions below will explore XML to find stats and sample entries for **element tag** - **tag key** relationships. 


```python
def isTypeOf(tag_,key):
    return (key == tag_.attrib['k'])
```


```python
def add_type(result,value):
    if value in result:
        result[value]+=1
    else:
        result[value] = 1
```


```python
def get_elem_tags(elem):
    result = {}
    for tag_ in elem.iter("tag"):
        result[tag_.attrib["k"]] = tag_.attrib["v"]
    return result
```


```python
def get_stats_with_tag_key(filename,tag,key):
    result = {}
    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == tag:
            for tag_ in elem.iter("tag"):
                if(isTypeOf(tag_,key)):
                    add_type(result,tag_.attrib['v'])
                    if(result[tag_.attrib['v']]==1):
                        pprint.pprint(get_elem_tags(elem))
    return result
```

I am expecting religious places being in *node* tag type. Therefore, let's first look into nodes tagged with *religion*:


```python
get_stats_with_tag_key(DATA_FILE,"node","religion")
```

    {'historic': 'memorial',
     'name': u'Barbaros Hayrettin T\xfcrbesi',
     'religion': 'muslim'}
    {'amenity': 'place_of_worship',
     'name': u'Be\u015fikta\u015f Panayia Rum Ortodoks Kilisesi Vakf\u0131',
     'religion': 'christian'}
    {'amenity': 'place_of_worship',
     'name': u'Ortak\xf6y Etzahayim Musevi Sinagonu',
     'religion': 'jewish'}
    {'amenity': 'place_of_worship',
     'name': u'U\xe7an Spagetti Canavar\u0131 Tap\u0131na\u011f\u0131',
     'religion': 'pastafarian'}
    




    {'christian': 15, 'jewish': 4, 'muslim': 148, 'pastafarian': 1}



I am seeing that there are Christian, Jewish, Muslim and Pastafarian places listed. Where most of nodes belong to Muslims in an unsurprising way.

Let's also look into ways so that we don't miss anything of value. 


```python
get_stats_with_tag_key(DATA_FILE,"way","religion")
```

    {'amenity': 'place_of_worship',
     'building': 'yes',
     'name': u'\u015eehzadeba\u015f\u0131 Camii',
     'name:cs': u'Princova me\u0161ita',
     'name:de': 'Prinzenmoschee',
     'name:en': "Sehzade Camii Prince's Mosque",
     'name:ru': u'\u041c\u0435\u0447\u0435\u0442\u044c \u0428\u0435\u0445\u0437\u0430\u0434\u0435',
     'religion': 'muslim',
     'tourism': 'attraction',
     'wheelchair': 'yes',
     'wikipedia': u'tr:\u015eehzadeba\u015f\u0131 Camii'}
    {'landuse': 'cemetery',
     'name': u'H\u0131ristiyan Mezarl\u0131\u011f\u0131',
     'religion': 'christian'}
    {'landuse': 'cemetery',
     'name': u'A\u015fkenaz Musevi Cemaati Mezarl\u0131\u011f\u0131',
     'religion': 'jewish'}
    




    {'christian': 95, 'jewish': 9, 'muslim': 1923}



Quite surprisingly to me, there are actually not only entries in **way-tag**, but also a lot more entries than **node-tag**. 

I think it will be plausible to merge results from both tag classes. 

# Problems Encountered

* Not all nodes have amanity tag. Therefore we will stick to last word in their names which tells about their types. 

* Most places have a varying naming issues at the end of their names. For example, Mosques have **Camii, Camisi etc**, Sinagogs have **Sinagogu, Sinangog etc.** Therefore, I will be checking last work in place names for each religion, and try to audit their types into known few types.
* There are Turkish characters in almost all names. I will be replacing this characters with their English counterpart to eliminate visual problems with character codes.


```python
turkishCharMap = {
    "ç":"c",
    "Ç":"C",
    "ğ":"g",
    "Ğ":"G",
    "ı":"i",
    "İ":"I",
    "ö":"o",
    "Ö":"O",
    "ş":"s",
    "Ş":"S",
    "ü":"u",
    "Ü":"U"
}
def serializeTurkishText(text):
    text = text.encode("utf-8")
    for k,v in turkishCharMap.iteritems():
        text = text.replace(k,v)
    return text;
```


```python
def get_last_word(name):
    return serializeTurkishText(name.split(" ")[-1]).lower()
```


```python
def get_religious_place_types(filename,religion):
    types = {}
    place_list = {}
    for event, elem in ET.iterparse(filename, events=("start",)):
        elem_tags = get_elem_tags(elem)
        if("religion" in elem_tags and elem_tags["religion"]==religion):
            name = ""
            if "name" in elem_tags:
                name = elem_tags["name"]
            type_ = get_last_word(name)
            if type_ not in types:
                types[type_] = 1
                place_list[type_] = [elem_tags]
            else:
                types[type_] += 1
                place_list[type_].append(elem_tags)
    return (types, place_list)
```


```python
muslim_types, muslim_place_list = get_religious_place_types(DATA_FILE,"muslim")
muslim_types
```




    {'': 3124,
     '(insaat)': 1,
     'ada)': 6,
     'aksemsettin': 1,
     'asamasinda)': 1,
     'cami': 740,
     'camii': 267,
     'camii)': 1,
     'camii3': 1,
     'camil': 1,
     'camisi': 8,
     'cemevi': 8,
     'cmi': 1,
     'germe': 1,
     'hamami': 1,
     'hatun': 1,
     'kulliyesi': 1,
     'kursu': 1,
     'medresesi': 2,
     'mescid': 3,
     'mescidi': 19,
     'mescit': 3,
     'mezarligi': 18,
     'mezarlik': 9,
     'muftulugu': 1,
     'namazgah': 1,
     'pasa': 2,
     'serifi': 3,
     'tekkesi': 1,
     'turbesi': 3}



Many missing places(3124) are in the list. These places seem to be having no names at all. Therefore, I feel an urge to look into this entries: 


```python
muslim_place_list[""]
```




    [{'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'name:en': 'Murat Reis Camii',
      'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'created_by': 'JOSM',
      'name:en': 'Murat Reia Camii',
      'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'created_by': 'Potlatch 0.10f',
      'religion': 'muslim',
      'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'created_by': 'Potlatch 0.10f',
      'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'created_by': 'Potlatch 0.10f',
      'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'created_by': 'Potlatch 0.10f',
      'religion': 'muslim',
      'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'created_by': 'Potlatch 0.10f',
      'religion': 'muslim',
      'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'created_by': 'Potlatch 0.10f',
      'religion': 'muslim',
      'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'created_by': 'Potlatch 0.10f',
      'religion': 'muslim',
      'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'created_by': 'Potlatch 0.10f',
      'religion': 'muslim',
      'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'created_by': 'Potlatch 0.10f',
      'religion': 'muslim',
      'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'created_by': 'Potlatch 0.10f',
      'religion': 'muslim',
      'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim', 'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim', 'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'created_by': 'Potlatch 0.10f',
      'religion': 'muslim',
      'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'created_by': 'Potlatch 0.10f',
      'religion': 'muslim',
      'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim', 'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'created_by': 'Potlatch 0.10f',
      'religion': 'muslim',
      'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'created_by': 'Potlatch 0.10f',
      'religion': 'muslim',
      'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'created_by': 'Potlatch 0.10f',
      'religion': 'muslim',
      'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim', 'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim', 'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim', 'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim', 'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim', 'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim', 'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim', 'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim', 'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim', 'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim', 'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim', 'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim', 'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim', 'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'denomination': 'sunni',
      'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'denomination': 'sunni',
      'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'denomination': 'sunni',
      'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'denomination': 'sunni',
      'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'denomination': 'sunni',
      'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'denomination': 'sunni',
      'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'denomination': 'sunni',
      'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'denomination': 'sunni',
      'religion': 'muslim'},
     {'religion': 'muslim'},
     {'addr:city': 'Istanbul',
      'amenity': 'place_of_worship',
      'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'denomination': 'sunni',
      'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'denomination': 'sunni',
      'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'denomination': 'sunni',
      'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'landuse': 'cemetery', 'religion': 'muslim', 'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'building': 'yes',
      'religion': 'muslim',
      'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'leisure': 'park', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'building': 'yes',
      'religion': 'muslim',
      'source': 'local_knowledge; Bing'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'landuse': 'cemetery', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'building': 'yes',
      'religion': 'muslim',
      'source': 'Bing'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'grave_yard', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'building': 'yes',
      'religion': 'muslim',
      'source': 'bing'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'building': 'yes',
      'religion': 'muslim',
      'source': 'Bing'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'building': 'yes',
      'denomination': 'sunni',
      'religion': 'muslim',
      'source': 'bing'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'denomination': 'sunni',
      'landuse': 'commercial',
      'religion': 'muslim',
      'source': 'bing'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'landuse': 'cemetery', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'landuse': 'cemetery', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'landuse': 'cemetery', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'landuse': 'cemetery', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'landuse': 'cemetery', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'landuse': 'cemetery', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'landuse': 'cemetery', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'landuse': 'cemetery', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'building': 'yes',
      'religion': 'muslim',
      'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'building': 'yes',
      'religion': 'muslim',
      'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'religion': 'muslim', 'source': 'Yahoo'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'building': 'mosque',
      'denomination': 'sunni',
      'religion': 'muslim',
      'source': 'bing'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'addr:city': 'Pendik/istanbul',
      'amenity': 'place_of_worship',
      'building': 'yes',
      'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship',
      'building': 'mosque',
      'denomination': 'sunni',
      'religion': 'muslim',
      'source': 'bing'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     {'amenity': 'place_of_worship', 'building': 'yes', 'religion': 'muslim'},
     {'religion': 'muslim'},
     ...]



## New Problems
* It seems some have names only in English. I will add these entries with their English names. 
* Apart from this, most of places seem to be holding no information but the religion tag itself. Since, we have no chance of making guesses about this I will simply ignore these entries. 
* Lastly, there are some entries with some variables that could help to extract their types.


```python
attributes_to_check = ["amenity","name:en","building","source"]
def getProminentAttributes(list_):
    result = {}
    for elem in list_:
        for k,v in elem.iteritems():
            if k in attributes_to_check:
                if k not in result:
                    result[k] = set(v)
                else:
                    result[k].add(v)
    return result
```


```python
pprint.pprint(getProminentAttributes(muslim_place_list[""]))
```

    {'amenity': set(['_',
                     'a',
                     'c',
                     'e',
                     'f',
                     'grave_yard',
                     'h',
                     'i',
                     'l',
                     'o',
                     'p',
                     'place_of_worship',
                     'r',
                     's',
                     'w']),
     'building': set(['e', 'mosque', 's', 'y', 'yes']),
     'name:en': set([' ',
                     'C',
                     'M',
                     'Murat Reia Camii',
                     'R',
                     'a',
                     'e',
                     'i',
                     'm',
                     'r',
                     's',
                     't',
                     'u']),
     'source': set(['Bing',
                    'Y',
                    'Yahoo',
                    'a',
                    'bing',
                    'h',
                    'local_knowledge; Bing',
                    'o'])}
    

It seems apart from "name:en" attribute none of above elements in sets provide enough info to extract type of the place. Therefore we will ignore the rest.

Now let's also look into other types that dont make much sense:


```python
muslim_types
```




    {'': 3124,
     '(insaat)': 1,
     'ada)': 6,
     'aksemsettin': 1,
     'asamasinda)': 1,
     'cami': 740,
     'camii': 267,
     'camii)': 1,
     'camii3': 1,
     'camil': 1,
     'camisi': 8,
     'cemevi': 8,
     'cmi': 1,
     'germe': 1,
     'hamami': 1,
     'hatun': 1,
     'kulliyesi': 1,
     'kursu': 1,
     'medresesi': 2,
     'mescid': 3,
     'mescidi': 19,
     'mescit': 3,
     'mezarligi': 18,
     'mezarlik': 9,
     'muftulugu': 1,
     'namazgah': 1,
     'pasa': 2,
     'serifi': 3,
     'tekkesi': 1,
     'turbesi': 3}




```python
muslim_place_list["(insaat)"]
```




    [{'amenity': 'place_of_worship',
      'building': 'yes',
      'name': u'Yeni Zeynebiye Camii (\u0130n\u015faat)',
      'religion': 'muslim'}]



This is a mosque with a note stating it's in reconstruction. Therefore, let's remove descriptions in paranthesis, and try again to see if things improve.


```python
import re
def remove_paranthesis(text):
    return re.sub(r'\(.*\)', '', text).strip()
```


```python
#Override the function to handle paranthesis:
def get_last_word(name):
    return serializeTurkishText(remove_paranthesis(name).split(" ")[-1]).lower()
```


```python
muslim_types, muslim_place_list = get_religious_place_types(DATA_FILE,"muslim")
muslim_types
```




    {'': 3124,
     'aksemsettin': 1,
     'cami': 741,
     'camii': 269,
     'camii3': 1,
     'camil': 1,
     'camisi': 8,
     'cemevi': 8,
     'cmi': 1,
     'germe': 1,
     'hamami': 1,
     'hatun': 1,
     'kulliyesi': 1,
     'kursu': 1,
     'medresesi': 2,
     'mescid': 3,
     'mescidi': 19,
     'mescit': 3,
     'mezarligi': 24,
     'mezarlik': 9,
     'muftulugu': 1,
     'namazgah': 1,
     'pasa': 2,
     'serifi': 3,
     'tekkesi': 1,
     'turbesi': 3}



Types listed above provide enough insight into types of places therefore we will now define mappings for types and typo fixes.

I decided to set below types:

* Mosque
* Islamic School
* Graveyard
* Other


```python
mapping = {
    "muslim":{
        'aksemsettin': "Other",
        'cami': "Mosque",
        'camii': "Mosque",
        'camii3': "Mosque",
        'camil': "Mosque",
        'camisi': "Mosque",
        'cemevi': "Mosque",
        'cmi': "Mosque",
        'germe': "Other",
        'hamami': "Other",
        'hatun': "Other",
        'kulliyesi': "Islamic School",
        'kursu': "Islamic School",
        'medresesi': "Islamic School",
        'mescid': "Mosque",
        'mescidi': "Mosque",
        'mescit': "Mosque",
        'mezarligi': "Graveyard",
        'mezarlik': "Graveyard",
        'muftulugu': "Other",
        'namazgah': "Mosque",
        'pasa': "Other",
        'serifi': "Mosque",
        'tekkesi': "Islamic School",
        'turbesi': "Other"
    }
}
typo_fixes = {
    "muslim":{
        'camii': "cami",
        'camii3': "cami",
        'camil': "cami",
        'camisi': "cami",
        'cmi': "cami"
    }
}
```


```python
christian_types, christian_place_list = get_religious_place_types(DATA_FILE,"christian")
christian_types
```




    {'': 127,
     'ayazmasi': 3,
     'church': 4,
     'kabristani': 1,
     'katedrali': 1,
     'kilesi': 1,
     'kiliesi': 1,
     'kilise': 2,
     'kilisesi': 62,
     'manastiri': 6,
     'metropolitligi': 1,
     'mezarligi': 8,
     'mongols': 1,
     'nikola': 1,
     'patrikhanesi': 1,
     'phokas': 1,
     'vakfi': 1,
     '\xd0\xa1\xd1\x82\xd0\xb5\xd1\x84\xd0\xb0\xd0\xbd\xe2\x80\x9c': 1}




```python
print '\xd0\xa1\xd1\x82\xd0\xb5\xd1\x84\xd0\xb0\xd0\xbd\xe2\x80\x9c'
```

    Стефан“
    

Place types seem to be alright. But lets dive into places with no names: 


```python
pprint.pprint(getProminentAttributes(christian_place_list[""]))
```

    {'amenity': set(['_',
                     'a',
                     'c',
                     'e',
                     'f',
                     'h',
                     'i',
                     'l',
                     'o',
                     'p',
                     'place_of_worship',
                     'r',
                     's',
                     'w']),
     'building': set(['e', 's', 'y', 'yes'])}
    

It's seems places with no names are no more that entries with almost no info. Therefore, I will be ignoring these ones also. 

Let's also add type mapping and typo fixes mapping. Our types will be as following:

* Church
* Graveyard
* Monastery
* Other


```python
mapping["christian"] = {
    'ayazmasi': "Other",
    'church': "Church",
    'kabristani': "Graveyard",
    'katedrali': "Church",
    'kilesi': "Church",
    'kiliesi': "Church",
    'kilise': "Church",
    'kilisesi': "Church",
    'manastiri': "Monastery",
    'metropolitligi': "Other",
    'mezarligi': "Graveyard",
    'mongols': "Other",
    'nikola': "Other",
    'patrikhanesi': "Other",
    'phokas': "Other",
    'vakfi': "Other",
    'Стефан“':"Other"
}
typo_fixes["christian"] = {
    'kilesi': "Kilisesi",
    'kiliesi': "Kilisesi"
}
```


```python
jewish_types, jewish_place_list = get_religious_place_types(DATA_FILE,"jewish")
jewish_types
```




    {'': 15,
     'mezarligi': 3,
     'neve-shalom': 1,
     'sinagog': 1,
     'sinagogu': 6,
     'sinagonu': 1}




```python
pprint.pprint(getProminentAttributes(jewish_place_list[""]))
```

    {'amenity': set(['_',
                     'a',
                     'c',
                     'e',
                     'f',
                     'h',
                     'i',
                     'l',
                     'o',
                     'p',
                     'r',
                     's',
                     'w']),
     'building': set(['e', 's', 'y'])}
    

There seems to be nothing to extract from places with no name, so we will ignore them.


```python
jewish_place_list['neve-shalom']
```




    [{'amenity': 'place_of_worship',
      'building': 'yes',
      'name': 'Neve-Shalom',
      'religion': 'jewish'}]



Let's add our type and typo fixes mappings. List of types is provided below:

* Synagogue
* Graveyard



```python
mapping["jewish"] = {
    'mezarligi': "Graveyard",
    'neve-shalom': "Synagogue",
    'sinagog': "Synagogue",
    'sinagogu': "Synagogue",
    'sinagonu': "Synagogue"
}
typo_fixes["jewish"] = {
    'sinagonu': "Sinagogu"
}
```


```python
pastafarian_types, pastafarian_place_list = get_religious_place_types(DATA_FILE,"pastafarian")
pastafarian_types
```




    {'': 1, 'tapinagi': 1}




```python
pastafarian_place_list[""]
```




    [{'religion': 'pastafarian'}]



An empty place. We will ignore this.
* I will tag the only **Tapınak** as temple. 


```python
mapping["pastafarian"] = {
    'tapinagi': "Temple"
}
typo_fixes["pastafarian"] = {}
```

# Data Extraction

Since we don't have any attribute in religious places list we will have a single SQL table.


```python
import sqlite3
sqlite_file = 'istanbul_osm.sqlite'
table = "religious_places"
columns = ["id","name","lat","lon","religion","type"]

conn = sqlite3.connect(sqlite_file)
c = conn.cursor()
```

**Create table, and drop if table already exists:**


```python
c.execute('DROP TABLE {tn}'\
        .format(tn=table))
c.execute('CREATE TABLE {tn} ({columns})'\
        .format(tn=table, columns=",".join(columns)))
```




    <sqlite3.Cursor at 0xafeb3340>




```python
religions = ['christian', 'jewish', 'muslim', 'pastafarian']
```


```python
def get_name(elem_tags):
    if "name" in elem_tags:
        return elem_tags["name"]
    elif "name:en" in elem_tags:
        return elem_tags["name:en"]
    else:
        return ""
```


```python
def get_fixed_name(elem_tags):
    name = get_name(elem_tags)
    name_words = name.split(" ")[0:-1]
    type_identifier = get_last_word(name)
    if type_identifier in typo_fixes[elem_tags["religion"]]:
        name_words.append(typo_fixes[elem_tags["religion"]][type_identifier])
        return " ".join(name_words)
    return name
```


```python
def get_type(elem_tags,name):
    type_identifier = get_last_word(name)
    religion = elem_tags["religion"]
    if type_identifier in mapping[religion]:
        return mapping[religion][type_identifier]
    else:
        pprint.pprint(["unknown type",elem_tags,type_identifier])
        return "Unknown" 
```


```python
def get_religious_places(filename):
    places = []
    for event, elem in ET.iterparse(filename, events=("start",)):
        elem_tags = get_elem_tags(elem)
        if "religion" in elem_tags and elem_tags["religion"] in religions:
            name = get_fixed_name(elem_tags)
            if(len(name)>0):
                type_ = get_type(elem_tags,name)
                elem_tags["name"] = name
                elem_tags["type"] = type_
                for column in columns:
                    if column in elem.attrib:
                        elem_tags[column] = elem.attrib[column]
                places.append(elem_tags)
    return places
```

**Below code will extract all places for all religions:**


```python
religious_places = get_religious_places(DATA_FILE)
```


```python
df = pd.DataFrame(religious_places,columns=columns)
df
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>name</th>
      <th>lat</th>
      <th>lon</th>
      <th>religion</th>
      <th>type</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>269497288</td>
      <td>Barbaros Hayrettin Türbesi</td>
      <td>41.0419227</td>
      <td>29.0068359</td>
      <td>muslim</td>
      <td>Other</td>
    </tr>
    <tr>
      <th>1</th>
      <td>269706604</td>
      <td>Ertuğrul Tekke cami</td>
      <td>41.0456489</td>
      <td>29.0085216</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>2</th>
      <td>269707397</td>
      <td>Beşiktaş Panayia Rum Ortodoks Kilisesi Vakfı</td>
      <td>41.0436679</td>
      <td>29.0050595</td>
      <td>christian</td>
      <td>Other</td>
    </tr>
    <tr>
      <th>3</th>
      <td>278092559</td>
      <td>Murat Reis cami</td>
      <td>41.0184464</td>
      <td>29.0275916</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>4</th>
      <td>278102132</td>
      <td>Murat Reia cami</td>
      <td>41.0231166</td>
      <td>29.0237092</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>5</th>
      <td>278471143</td>
      <td>Karacaahmet Cemevi</td>
      <td>41.0132479</td>
      <td>29.0201048</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>6</th>
      <td>290538729</td>
      <td>Isman Reis cami</td>
      <td>41.1145299</td>
      <td>29.0621858</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>7</th>
      <td>351639244</td>
      <td>Burgazada cami</td>
      <td>40.8829893</td>
      <td>29.0684726</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>8</th>
      <td>354969292</td>
      <td>Hacı Nimet Özden cami</td>
      <td>41.0681321</td>
      <td>29.0101802</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>9</th>
      <td>355123822</td>
      <td>Germe</td>
      <td>41.2738386</td>
      <td>28.6616036</td>
      <td>muslim</td>
      <td>Other</td>
    </tr>
    <tr>
      <th>10</th>
      <td>530505864</td>
      <td>Korkmaz cami</td>
      <td>41.0044274</td>
      <td>29.13552</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>11</th>
      <td>561432550</td>
      <td>Teşvikiye cami</td>
      <td>41.0493076</td>
      <td>28.9943361</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>12</th>
      <td>568011396</td>
      <td>Tuzbaba cami</td>
      <td>41.0456827</td>
      <td>29.0045499</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>13</th>
      <td>583311905</td>
      <td>Ulus Ambarlıdere cami</td>
      <td>41.0642259</td>
      <td>29.0277564</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>14</th>
      <td>618202087</td>
      <td>Tavşanlı Yeni Cami</td>
      <td>40.811901</td>
      <td>29.5138424</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>15</th>
      <td>628974845</td>
      <td>Ortaköy Etzahayim Musevi Sinagogu</td>
      <td>41.0482518</td>
      <td>29.025439</td>
      <td>jewish</td>
      <td>Synagogue</td>
    </tr>
    <tr>
      <th>16</th>
      <td>677531498</td>
      <td>Aya Yorgi Manastırı</td>
      <td>40.8487443</td>
      <td>29.118839</td>
      <td>christian</td>
      <td>Monastery</td>
    </tr>
    <tr>
      <th>17</th>
      <td>768706518</td>
      <td>Neve Şalom Sinagogu</td>
      <td>41.0268319</td>
      <td>28.9725508</td>
      <td>jewish</td>
      <td>Synagogue</td>
    </tr>
    <tr>
      <th>18</th>
      <td>976474174</td>
      <td>Fatih Mescidi</td>
      <td>41.0044905</td>
      <td>28.8526953</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>19</th>
      <td>1137608853</td>
      <td>Kartal Merkez Cami</td>
      <td>40.8888851</td>
      <td>29.1861316</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>20</th>
      <td>1226807915</td>
      <td>Haci şaban cami</td>
      <td>41.0440058</td>
      <td>28.95288</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>21</th>
      <td>1226807920</td>
      <td>çiksalin yeni cami</td>
      <td>41.0484944</td>
      <td>28.9494478</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>22</th>
      <td>1226807989</td>
      <td>Turşucu Hüseyin Cami</td>
      <td>41.0453995</td>
      <td>28.9476708</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>23</th>
      <td>1226826637</td>
      <td>Haşimi Emir Osman Cami</td>
      <td>41.0367007</td>
      <td>28.9633671</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>24</th>
      <td>1296078446</td>
      <td>Saraç Doğan cami</td>
      <td>41.0144096</td>
      <td>28.9344531</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>25</th>
      <td>1346157988</td>
      <td>Kalvinist Kilise</td>
      <td>41.03055</td>
      <td>28.9762479</td>
      <td>christian</td>
      <td>Church</td>
    </tr>
    <tr>
      <th>26</th>
      <td>1459164757</td>
      <td>Hacı Havva Özen cami</td>
      <td>40.8744938</td>
      <td>29.1299312</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>27</th>
      <td>1484043547</td>
      <td>cami</td>
      <td>41.0722109</td>
      <td>29.0427336</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>28</th>
      <td>1572067957</td>
      <td>Şafak Cami</td>
      <td>40.9739685</td>
      <td>29.1239604</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>29</th>
      <td>1572094993</td>
      <td>Küçük Bakkalköy Mrk. Cami</td>
      <td>40.980169</td>
      <td>29.1270825</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>1187</th>
      <td>499944896</td>
      <td>Şeyh Ebül Vefa Cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1188</th>
      <td>499944929</td>
      <td>Cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1189</th>
      <td>499961480</td>
      <td>Cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1190</th>
      <td>500791770</td>
      <td>Hz. Osman cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1191</th>
      <td>503156261</td>
      <td>Kartal Tepe cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1192</th>
      <td>504068206</td>
      <td>Hasan Kalyoncu Cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1193</th>
      <td>505785924</td>
      <td>Aya Nikola</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>christian</td>
      <td>Other</td>
    </tr>
    <tr>
      <th>1194</th>
      <td>505812174</td>
      <td>Yıldız Zöhre Cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1195</th>
      <td>507011662</td>
      <td>Kocatepe cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1196</th>
      <td>507318713</td>
      <td>Yeşilköy Bezmi Alem Cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1197</th>
      <td>1661399</td>
      <td>Fatih cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1198</th>
      <td>4121052</td>
      <td>Uhud cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1199</th>
      <td>4429647</td>
      <td>Beyazıt cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1200</th>
      <td>4465530</td>
      <td>Nişancı Mehmetpaşa Cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1201</th>
      <td>4567928</td>
      <td>Sokullu Şehit Mehmed Paşa cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1202</th>
      <td>4726719</td>
      <td>Mehmet Akif Cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1203</th>
      <td>4726752</td>
      <td>Üçevler cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1204</th>
      <td>4726753</td>
      <td>Mescid-i Selam cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1205</th>
      <td>4726769</td>
      <td>Konutbirlik cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1206</th>
      <td>4726770</td>
      <td>Kocatepe Ulu Cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1207</th>
      <td>5873274</td>
      <td>Zihni Bağdatlıoğlu cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1208</th>
      <td>7312915</td>
      <td>Yeşil Cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1209</th>
      <td>7317847</td>
      <td>Sinan Paşa cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1210</th>
      <td>7318379</td>
      <td>Mihrimah Sultan cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1211</th>
      <td>7318630</td>
      <td>Hz. Hüseyin cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1212</th>
      <td>7318631</td>
      <td>Kara Ahmet Paşa Cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1213</th>
      <td>7321116</td>
      <td>Yeni Valide Cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1214</th>
      <td>7328115</td>
      <td>Yavuz Sultan Selim Cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1215</th>
      <td>7328116</td>
      <td>Laleli cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
    <tr>
      <th>1216</th>
      <td>7328248</td>
      <td>Ataköy 5. Kısım Ömer Duruk Cami</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>muslim</td>
      <td>Mosque</td>
    </tr>
  </tbody>
</table>
<p>1217 rows × 6 columns</p>
</div>



**Let's check if any of places comes with missing fields:**


```python
def check_data_integrity(places):
    missing = []
    for place in places:
        for column in columns:
            if column not in place:
                missing.append(place)
                break
    return missing
```


```python
missing = check_data_integrity(religious_places)
```


```python
print str(len(missing))+" out of "+str(len(religious_places))+" places will have NA values in database."
```

    1122 out of 1217 places will have NA values in database.
    

**Function below will process all results and insert them into SQL table.**


```python
def insert_values(cursor,table,columns,values):
    sql_values = ""
    for value in values:
        values_str = ""
        for column in columns:
            if len(values_str)>0:
                values_str += ","
            if column in value:
                #replace quotes with double quotes in texts: special chars in SQL
                values_str += "'"+value[column].replace("'","''")+"'"
            else:
                values_str += "NULL"
        if len(sql_values)>0:
            sql_values += ","
        sql_values += "("+values_str+")"
    c.execute('INSERT INTO {tn} ({columns}) values {values}'
              .format(tn=table, columns=",".join(columns), values=sql_values.encode("utf-8")))
```


```python
insert_values(c,table,columns,religious_places)
conn.commit()
```

# Sample SQL Queries

### Top Religios Place Types


```python
c.execute("select type, count(type) as count from religious_places group by type order by count desc")
pd.DataFrame(c.fetchall(),columns=["Type","Count"])
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Type</th>
      <th>Count</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Mosque</td>
      <td>1060</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Church</td>
      <td>71</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Graveyard</td>
      <td>45</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Other</td>
      <td>20</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Synagogue</td>
      <td>9</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Monastery</td>
      <td>6</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Islamic School</td>
      <td>5</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Temple</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



### Top Religious Place Names


```python
c.execute("select name, count(type) as count from religious_places group by name order by count desc limit 10 offset 0")
pd.DataFrame(c.fetchall(),columns=["Type","Count"])
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Type</th>
      <th>Count</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Cami</td>
      <td>219</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Mezarlık</td>
      <td>8</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Mevlana Cami</td>
      <td>6</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Fatih cami</td>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Yunus Emre Cami</td>
      <td>4</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Akşemsettin Cami</td>
      <td>3</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Berat Cami</td>
      <td>3</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Huzur Cami</td>
      <td>3</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Hz. Ali Cami</td>
      <td>3</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Hz. Ebubekir cami</td>
      <td>3</td>
    </tr>
  </tbody>
</table>
</div>



### Religion Rank by # of Places


```python
c.execute("select religion, count(type) as count from religious_places group by religion order by count desc")
pd.DataFrame(c.fetchall(),columns=["Type","Count"])
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Type</th>
      <th>Count</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>muslim</td>
      <td>1108</td>
    </tr>
    <tr>
      <th>1</th>
      <td>christian</td>
      <td>96</td>
    </tr>
    <tr>
      <th>2</th>
      <td>jewish</td>
      <td>12</td>
    </tr>
    <tr>
      <th>3</th>
      <td>pastafarian</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>


