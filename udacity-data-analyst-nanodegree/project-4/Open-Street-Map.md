
# Introduction

The largest city in Turkey that I am familiar with is İstanbul. Therefore, I thought I could look at the map and check if I can catch anything of significance. 


```python
import xml.etree.cElementTree as ET
import pandas as pd
import pprint
import bz2file
import operator
import numpy as np
import os
```


```python
DATA_FILE = "istanbul_turkey.osm"
```


```python
bz2_data = bz2file.BZ2File(DATA_FILE+".bz2").read()
open(DATA_FILE, 'wb').write(bz2_data)
```

I want to first check my data to see what hierarchy it has. Below functions will extract tags and hierarchy in my dataset. It will also extract attributes and child tags for each tag residing within our XML file. 


```python
# This function will traverse attributes and childs for each tag type.
def define_file(filename):
    tags = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag not in tags:
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
        result[value] += 1
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
    return result
```

I am expecting religious places being in *node* tag type. Therefore, let's first look into nodes tagged with *religion*:


```python
get_stats_with_tag_key(DATA_FILE,"node","religion")
```




    {'christian': 15, 'jewish': 4, 'muslim': 148, 'pastafarian': 1}



I am seeing that there are Christian, Jewish, Muslim and Pastafarian places listed. Where most of nodes belong to Muslims in an unsurprising way.

Let's also look into ways so that we don't miss anything of value. 


```python
get_stats_with_tag_key(DATA_FILE,"way","religion")
```




    {'christian': 95, 'jewish': 9, 'muslim': 1923}



Quite surprising to me, there are actually not only entries in **way-tag**, but also a lot more entries than **node-tag**. 

I think it will be plausible to merge results from both tag classes. 

# Problems Encountered

* Not all nodes have amenity tag. Therefore we will stick to last word in their names which tells about their types. 

* Most places have a varying naming issues at the end of their names. For example, Mosques have **Camii, Camisi etc**, Sinagogs have **Sinagogu, Sinangog etc.** Therefore, I will be checking last word in place names for each religion, and try to audit their types into known few types.
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
def tabulate_dict(dict_):
    sorted_list = sorted(list(dict_.items()), key=operator.itemgetter(1), reverse=True)
    return pd.DataFrame([i[1] for i in sorted_list],index=[i[0] for i in sorted_list]).transpose()
```


```python
muslim_types, muslim_place_list = get_religious_place_types(DATA_FILE,"muslim")
tabulate_dict(muslim_types)
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
      <th></th>
      <th>cami</th>
      <th>camii</th>
      <th>mescidi</th>
      <th>mezarligi</th>
      <th>mezarlik</th>
      <th>camisi</th>
      <th>cemevi</th>
      <th>ada)</th>
      <th>serifi</th>
      <th>...</th>
      <th>aksemsettin</th>
      <th>muftulugu</th>
      <th>camii)</th>
      <th>(insaat)</th>
      <th>camii3</th>
      <th>kulliyesi</th>
      <th>kursu</th>
      <th>cmi</th>
      <th>asamasinda)</th>
      <th>hatun</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>3124</td>
      <td>740</td>
      <td>267</td>
      <td>19</td>
      <td>18</td>
      <td>9</td>
      <td>8</td>
      <td>8</td>
      <td>6</td>
      <td>3</td>
      <td>...</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
<p>1 rows × 30 columns</p>
</div>



Many missing places(3124) are in the list. These places seem to be having no names at all. Therefore, I feel an urge to look into this entries: 


```python
np.random.choice(muslim_place_list[""],10)
```




    array([{'religion': 'muslim'}, {'religion': 'muslim'},
           {'religion': 'muslim'},
           {'religion': 'muslim', 'amenity': 'place_of_worship'},
           {'building': 'yes', 'religion': 'muslim', 'amenity': 'place_of_worship'},
           {'building': 'yes', 'religion': 'muslim', 'amenity': 'place_of_worship'},
           {'religion': 'muslim'},
           {'building': 'yes', 'religion': 'muslim', 'amenity': 'place_of_worship'},
           {'religion': 'muslim'}, {'religion': 'muslim'}], dtype=object)




```python
tabulate_dict(muslim_types)
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
      <th></th>
      <th>cami</th>
      <th>camii</th>
      <th>mescidi</th>
      <th>mezarligi</th>
      <th>mezarlik</th>
      <th>camisi</th>
      <th>cemevi</th>
      <th>ada)</th>
      <th>serifi</th>
      <th>...</th>
      <th>aksemsettin</th>
      <th>muftulugu</th>
      <th>camii)</th>
      <th>(insaat)</th>
      <th>camii3</th>
      <th>kulliyesi</th>
      <th>kursu</th>
      <th>cmi</th>
      <th>asamasinda)</th>
      <th>hatun</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>3124</td>
      <td>740</td>
      <td>267</td>
      <td>19</td>
      <td>18</td>
      <td>9</td>
      <td>8</td>
      <td>8</td>
      <td>6</td>
      <td>3</td>
      <td>...</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
<p>1 rows × 30 columns</p>
</div>



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
tabulate_dict(getProminentAttributes(muslim_place_list[""]))
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
      <th>building</th>
      <th>source</th>
      <th>amenity</th>
      <th>name:en</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>y</td>
      <td>a</td>
      <td>a</td>
      <td>a</td>
    </tr>
    <tr>
      <th>1</th>
      <td>mosque</td>
      <td>bing</td>
      <td>place_of_worship</td>
      <td></td>
    </tr>
    <tr>
      <th>2</th>
      <td>s</td>
      <td>h</td>
      <td>c</td>
      <td>C</td>
    </tr>
    <tr>
      <th>3</th>
      <td>e</td>
      <td>local_knowledge; Bing</td>
      <td>e</td>
      <td>e</td>
    </tr>
    <tr>
      <th>4</th>
      <td>yes</td>
      <td>Yahoo</td>
      <td>f</td>
      <td>Murat Reia Camii</td>
    </tr>
    <tr>
      <th>5</th>
      <td>None</td>
      <td>o</td>
      <td>i</td>
      <td>i</td>
    </tr>
    <tr>
      <th>6</th>
      <td>None</td>
      <td>Y</td>
      <td>h</td>
      <td>m</td>
    </tr>
    <tr>
      <th>7</th>
      <td>None</td>
      <td>Bing</td>
      <td>l</td>
      <td>M</td>
    </tr>
    <tr>
      <th>8</th>
      <td>None</td>
      <td>None</td>
      <td>o</td>
      <td>s</td>
    </tr>
    <tr>
      <th>9</th>
      <td>None</td>
      <td>None</td>
      <td>p</td>
      <td>r</td>
    </tr>
    <tr>
      <th>10</th>
      <td>None</td>
      <td>None</td>
      <td>s</td>
      <td>u</td>
    </tr>
    <tr>
      <th>11</th>
      <td>None</td>
      <td>None</td>
      <td>r</td>
      <td>t</td>
    </tr>
    <tr>
      <th>12</th>
      <td>None</td>
      <td>None</td>
      <td>w</td>
      <td>R</td>
    </tr>
    <tr>
      <th>13</th>
      <td>None</td>
      <td>None</td>
      <td>grave_yard</td>
      <td>None</td>
    </tr>
    <tr>
      <th>14</th>
      <td>None</td>
      <td>None</td>
      <td>_</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>



It seems apart from "name:en" attribute none of above elements in sets provide enough info to extract type of the place. Therefore we will ignore the rest.

Now let's also look into other types that dont make much sense:


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
tabulate_dict(muslim_types)
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
      <th></th>
      <th>cami</th>
      <th>camii</th>
      <th>mezarligi</th>
      <th>mescidi</th>
      <th>mezarlik</th>
      <th>camisi</th>
      <th>cemevi</th>
      <th>serifi</th>
      <th>mescit</th>
      <th>...</th>
      <th>germe</th>
      <th>tekkesi</th>
      <th>aksemsettin</th>
      <th>muftulugu</th>
      <th>hamami</th>
      <th>camii3</th>
      <th>kulliyesi</th>
      <th>kursu</th>
      <th>cmi</th>
      <th>hatun</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>3124</td>
      <td>741</td>
      <td>269</td>
      <td>24</td>
      <td>19</td>
      <td>9</td>
      <td>8</td>
      <td>8</td>
      <td>3</td>
      <td>3</td>
      <td>...</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
<p>1 rows × 26 columns</p>
</div>



Types listed above provide enough insight into types of places therefore we will now define mappings for types and typo fixes.

I decided to set below types:

* Mosque
* Islamic School
* Graveyard
* Other


```python
mapping = {
    'Graveyard': ['mezarligi', 'mezarlik'],
    'Islamic School': ['kursu', 'tekkesi', 'medresesi', 'kulliyesi'],
    'Mosque': ['camil', 'camii','camisi','namazgah','serifi','mescit','cemevi','camii3','mescid','mescidi','cmi','cami'],
    'Other': ['pasa','germe','aksemsettin','muftulugu','hamami','turbesi','hatun']
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
tabulate_dict(christian_types)
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
      <th></th>
      <th>kilisesi</th>
      <th>mezarligi</th>
      <th>manastiri</th>
      <th>church</th>
      <th>ayazmasi</th>
      <th>kilise</th>
      <th>nikola</th>
      <th>phokas</th>
      <th>katedrali</th>
      <th>vakfi</th>
      <th>patrikhanesi</th>
      <th>mongols</th>
      <th>metropolitligi</th>
      <th>kabristani</th>
      <th>Стефан“</th>
      <th>kilesi</th>
      <th>kiliesi</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>127</td>
      <td>62</td>
      <td>8</td>
      <td>6</td>
      <td>4</td>
      <td>3</td>
      <td>2</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



Place types seem to be alright. But lets dive into places with no names: 


```python
tabulate_dict(getProminentAttributes(christian_place_list[""])).transpose()
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
      <th>0</th>
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>4</th>
      <th>5</th>
      <th>6</th>
      <th>7</th>
      <th>8</th>
      <th>9</th>
      <th>10</th>
      <th>11</th>
      <th>12</th>
      <th>13</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>building</th>
      <td>y</td>
      <td>s</td>
      <td>e</td>
      <td>yes</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>amenity</th>
      <td>a</td>
      <td>place_of_worship</td>
      <td>c</td>
      <td>e</td>
      <td>f</td>
      <td>i</td>
      <td>h</td>
      <td>l</td>
      <td>o</td>
      <td>p</td>
      <td>s</td>
      <td>r</td>
      <td>w</td>
      <td>_</td>
    </tr>
  </tbody>
</table>
</div>



It's seems places with no names are no more that entries with almost no info. Therefore, I will be ignoring these ones also. 

Let's also add type mapping and typo fixes mapping. Our types will be as following:

* Church
* Graveyard
* Monastery
* Other


```python
mapping['Church'] = ['kilesi', 'katedrali', 'kilise', 'kilisesi', 'church', 'kiliesi']
mapping['Monastery'] = ['manastiri']
mapping['Graveyard'] += ['kabristani', 'mezarligi']
mapping['Other'] += ['nikola','phokas','ayazmasi','metropolitligi','patrikhanesi','mongols','Стефан“','vakfi']

typo_fixes["christian"] = {
    'kilesi': "Kilisesi",
    'kiliesi': "Kilisesi"
}
```


```python
jewish_types, jewish_place_list = get_religious_place_types(DATA_FILE,"jewish")
tabulate_dict(jewish_types)
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
      <th></th>
      <th>sinagogu</th>
      <th>mezarligi</th>
      <th>sinagonu</th>
      <th>sinagog</th>
      <th>neve-shalom</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>15</td>
      <td>6</td>
      <td>3</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>




```python
tabulate_dict(getProminentAttributes(jewish_place_list[""])).transpose()
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
      <th>0</th>
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>4</th>
      <th>5</th>
      <th>6</th>
      <th>7</th>
      <th>8</th>
      <th>9</th>
      <th>10</th>
      <th>11</th>
      <th>12</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>building</th>
      <td>y</td>
      <td>s</td>
      <td>e</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>amenity</th>
      <td>a</td>
      <td>c</td>
      <td>e</td>
      <td>f</td>
      <td>i</td>
      <td>h</td>
      <td>l</td>
      <td>o</td>
      <td>p</td>
      <td>s</td>
      <td>r</td>
      <td>w</td>
      <td>_</td>
    </tr>
  </tbody>
</table>
</div>



There seems to be nothing to extract from places with no name, so we will ignore them.

Let's add our type and typo fixes mappings. List of types is provided below:

* Synagogue
* Graveyard



```python
mapping['Synagogue'] = ['neve-shalom', 'sinagogu', 'sinagonu', 'sinagog']
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
mapping["Temple"] = ["tapinagi"]
typo_fixes["pastafarian"] = {}
```

# Data Extraction

Since we don't have any multiple valued attribute in religious places list we will have a single SQL table.


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




    <sqlite3.Cursor at 0x5d314ab0>




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
    for k,v in mapping.iteritems():
        if type_identifier in mapping[k]:
            return k
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
pd.DataFrame(religious_places,columns=columns).head()
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
  </tbody>
</table>
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
print str(len(missing))+" out of "+str(len(religious_places))+" places will have NULL values in database."
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

# Data Overview and Additional Ideas

## Data File Size


```python
print DATA_FILE+"........"+str(os.stat(DATA_FILE).st_size/(1024*1024))+"MB"
print sqlite_file+"........"+str(os.stat(sqlite_file).st_size/(1024))+"kB"
```

    istanbul_turkey.osm........242MB
    istanbul_osm.sqlite........130kB
    

## Sample SQL Queries

### Top Religios Place Types


```python
c.execute("select type, count(type) as count from religious_places group by type order by count desc")
pd.DataFrame(c.fetchall(),columns=["Type","Count"]).transpose()
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
      <th>0</th>
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>4</th>
      <th>5</th>
      <th>6</th>
      <th>7</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Type</th>
      <td>Mosque</td>
      <td>Church</td>
      <td>Graveyard</td>
      <td>Other</td>
      <td>Synagogue</td>
      <td>Monastery</td>
      <td>Islamic School</td>
      <td>Temple</td>
    </tr>
    <tr>
      <th>Count</th>
      <td>1060</td>
      <td>71</td>
      <td>45</td>
      <td>20</td>
      <td>9</td>
      <td>6</td>
      <td>5</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



### Top Religious Place Names


```python
c.execute("select name, count(type) as count from religious_places group by name order by count desc")
pd.DataFrame(c.fetchall(),columns=["Type","Count"]).head(10).transpose()
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
      <th>0</th>
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>4</th>
      <th>5</th>
      <th>6</th>
      <th>7</th>
      <th>8</th>
      <th>9</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Type</th>
      <td>Cami</td>
      <td>Mezarlık</td>
      <td>Mevlana Cami</td>
      <td>Fatih cami</td>
      <td>Yunus Emre Cami</td>
      <td>Akşemsettin Cami</td>
      <td>Berat Cami</td>
      <td>Huzur Cami</td>
      <td>Hz. Ali Cami</td>
      <td>Hz. Ebubekir cami</td>
    </tr>
    <tr>
      <th>Count</th>
      <td>219</td>
      <td>8</td>
      <td>6</td>
      <td>4</td>
      <td>4</td>
      <td>3</td>
      <td>3</td>
      <td>3</td>
      <td>3</td>
      <td>3</td>
    </tr>
  </tbody>
</table>
</div>



### Religion Rank by # of Places


```python
c.execute("select religion, count(type) as count from religious_places group by religion order by count desc")
pd.DataFrame(c.fetchall(),columns=["Type","Count"]).transpose()
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
      <th>0</th>
      <th>1</th>
      <th>2</th>
      <th>3</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Type</th>
      <td>muslim</td>
      <td>christian</td>
      <td>jewish</td>
      <td>pastafarian</td>
    </tr>
    <tr>
      <th>Count</th>
      <td>1108</td>
      <td>96</td>
      <td>12</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



# Additional Ideas

### Places with few Attributes

There are lots of places with a single attribute which provides no insight into the place itself. Most of these places are ignored in our data exploration stages. These entries either belong to some incomplete data or they are garbage as a whole. 

I think some incentives could be taken to clean or complete these entries. Gamification and AutoBots could be two of possible solutions.

||Pros|Cons|
|-|-|-|
|Gamification|Users will be motivated to contribute more|The abundance of similar types of missing entries could annoy users|
|AutoBots|Very fast resolution|Contributions being little of value to the completeness of the data|

A hybrid solution could potentially improve overall results better.


# Conclusion

Data set seems to be filled with incomplete and garbage entries. This limits our ability to extract all information in addition to our ability to distinguish incomplete data from abundant data.

A quick check on Wikipedia gives us the [List of Churches](https://tr.wikipedia.org/wiki/%C4%B0stanbul%27daki_kiliseler_listesi) and the [List of Mosques](https://tr.wikipedia.org/wiki/%C4%B0stanbul%27daki_camiler_listesi) in Istanbul. This shows that there is around 110-120 churches in Istanbul where as our data set has 71 with comlete data. In addition the second list provides names of around 3k mosques in Istanbul. We were able to extract data only for 1060 of them. This shows that our dataset is incomplete to a great extent.
