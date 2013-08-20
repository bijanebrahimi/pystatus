import re
from BeautifulSoup import BeautifulSoup
from convert import str_to_datetime

# Error Classes
class Error(Exception):
    def __init__(self):
        Exception.__init__(self)

class ActivityStreamsMissingError(Error):
    def __init__(self, missing):
        self.missing = missing
        Error.__init__(self)
    def __str__(self):
        return 'ActivityStream is missing `%s`' % self.missing

# ActivityStreams Extension
class ActivityStreamsExtension(object):
    pass

# GeoRSS: http://www.georss.org/georss
class GeoRSS(ActivityStreamsExtension):
    def __init__(self):
        ActitivityStreamsExtension.__init__(self)
    @staticmethod
    def parse_xml(xml, object_construct={}):
        try:
            lon, lat = xml.find('georss:where').find('gml:Point').find('gml:pos').text.split(' ')
            object_construct['point'] = (lon, lat)
            return object_construct
        except:
            return object_construct

# Atom Threading Extension: www.ietf.org/rfc/rfc4685.txt
class AtomThreadingExtensions(ActivityStreamsExtension):
    def __init__(self):
        ActitivityStreamsExtension.__init__(self)
    @staticmethod
    def parse_xml(xml, object_construct={}):
        try:
            if xml.name == 'thr:in-reply-to':
                object_construct['ref'] = xml.get('ref')
                object_construct['href'] = xml.get('href')
                object_construct['source'] = xml.get('source')
                object_construct['type'] = 'application/atom+xml'
                object_construct['type'] = xml.get('type')
        except:
            pass
        return object_construct

# Portable Contacts: http://portablecontacts.net/draft-spec.html
class PortableContactsExtensions(ActivityStreamsExtension):
    def __init__(self):
        ActitivityStreamsExtension.__init__(self)
    @staticmethod
    def parse_xml(xml, object_construct={}):
        parent_name = xml.name
        username = xml.findChildren('poco:preferredusername')
        if username:
            object_construct['username'] = username[0].text.strip()
        displayname = xml.findChildren('poco:displayname')
        if displayname:
            object_construct['name'] = displayname[0].text.strip()
        note = xml.findChildren('poco:note')
        if note:
            object_construct['note'] = note[0].text.strip()
        address = xml.findChildren('poco:address')
        if address:
            # TODO: saerch for streetAddress, localirt, region, postalCode and countery
            object_construct['address'] = address[0].find('poco:formatted').text.strip()
        urls = xml.findChildren('poco:urls')
        object_construct['urls'] = []
        for url in urls:
            object_construct['urls'].append(dict(type=url.find('poco:type').text.strip(),
                                               value=url.find('poco:value').text.strip(),
                                               primary=url.find('poco:primary').text.strip().lower()=='true'))
        return object_construct

# Ostatus: http://ostatus.org/schema/1.0
class OStatusExtensions(ActivityStreamsExtension):
    def __init__(self):
        ActitivityStreamsExtension.__init__(self)
    @staticmethod
    def parse_xml(xml, object_construct={}):
        parent_name = xml.name
        conversation = xml.findChildren('ostatus:conversation')
        if conversation:
            object_construct['conversation'] = conversation[0].get('href')
        attention = xml.findChildren('ostatus:attention')
        if conversation:
            object_construct['attention'] = attention[0].get('href')
        return object_construct

# ActivityStreams
class ActivityStreams(object):
    def __init__(self, source):
        xml = BeautifulSoup(source)
        self.activity = ActivityStreams.parse_xml(xml)
    @staticmethod
    def parse_xml(xml, object_construct={}):
        parent_name = xml.name
        for element in xml.findAll():
            if element.name == 'id':
                # TODO: Invalid AS if id existed
                object_construct['id'] = element.text
            elif element.name == 'title':
                # TODO: convert to HTML
                object_construct['title'] = element.text
            elif element.name == 'published':
                # TODO: convert to Time
                object_construct['published'] = element.text
            elif element.name == 'summary':
                # TODO: convert to HTML
                object_construct['summary'] = element.text
            elif element.name == 'content' and object_construct.get('summary') is None:
                # TODO: convert to HTML
                object_construct['summary'] = element.text
            elif element.name == 'link' and element.get('rel') == 'preview':
                # TODO: type should be image/*
                object_construct['image'] = element.text
            elif element.name == 'link' and element.get('rel') == 'alternative':
                object_construct['permalink'] = element.text
            elif element.name == 'activity:object-type':
                object_construct['type'] = element.text.replace('http://activitystrea.ms/schema/1.0/', '').strip()
            elif element.name == 'activity:verb':
                object_construct['verb'] = element.text.replace('http://activitystrea.ms/schema/1.0/', '').strip()
            elif element.name == 'name' and parent_name == 'author':
                object_construct['name'] = element.text.strip()
            elif element.name == 'author':
                object_construct['author'] = ActivityStreams.parse_xml(element)
            elif element.name == 'activity:object':
                object_construct['object'] = ActivityStreams.parse_xml(element)
            elif element.name == 'activity:target':
                object_construct['target'] = ActivityStreams.parse_xml(element)
        
        object_construct['poco'] = PortableContactsExtensions.parse_xml(xml)
        object_construct['ostatus'] = OStatusExtensions.parse_xml(xml)
        object_construct['thr'] = AtomThreadingExtensions.parse_xml(element)
        object_construct['georss'] = GeoRSS.parse_xml(element)
        
        if parent_name == 'author' and object_construct.get('permalink') is None:
            object_construct['permalink'] = xml.find('uri').text
        return object_construct        

# Atom Feed
class AtomFeed(object):
    def __init__(self, data):
        if isinstance(data, str):
            xml = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
            self.atom_type = xml.findChild().name
            self.atom = AtomFeed.parse_xml(xml)
    @staticmethod
    def parse_personconstruct(element):
        personconstruct = {}
        for child_element in element.findAll():
            if child_element.name == 'name':
                personconstruct['name'] = child_element.text.strip()
            elif child_element.name == 'uri':
                personconstruct['uri'] = child_element.text.strip()
            elif child_element.name == 'email':
                personconstruct['email'] = child_element.text.strip()
        return personconstruct
        
    @staticmethod
    def parse_xml(xml):
        atom = {}
        for element in xml.findAll():
            if element.name == 'author':
                atom['author'] = AtomFeed.parse_personconstruct(element)
            elif element.name == 'category':
                if atom.get('category') is None:
                    atom['category'] = []
                atom['category'].append(element.text.strip())
            elif element.name == 'content':
                # TODO:xhtml type will be ignored
                if element.get('type') in ['text', '', None]: 
                    atom['content'] = dict(type='text',
                                           value=element.text)
                elif element.get('type') in ['html']:
                    # TODO: html unescape the value
                    atom['content'] = dict(type='html',
                                           value=element.text)
            elif element.name == 'contributor':
                if atom.get('contributor') is None:
                    atom['contributor'] = []
                atom['contributor'].append(AtomFeed.parse_personconstruct(element))
            elif element.name == 'id':
                atom['contributor'] = element.text.strip()
            elif element.name == 'link':
                # type `via` will be ignored
                if atom.get('link') is None:
                    atom['link'] = {}
                if element.get('rel') == 'alternate':
                    atom['link']['alternate'] = dict(value=element.get('href'),
                                                     type=element.get('type'))
                elif element.get('rel') == 'self':
                    atom['link']['self'] = dict(value=element.get('href'),
                                                type=element.get('type'))
                elif element.get('rel') == 'related':
                    atom['link']['related'] = dict(value=element.get('href'),
                                                   type=element.get('type'))
                elif element.get('rel') == 'enclosure':
                    if atom['link'].get('enclosure') is None:
                        atom['link']['enclosure'] = []
                    atom['link']['enclosure'].append(dict(value=element.get('href'),
                                                          length=element.get('length'),
                                                          title=element.get('title'),
                                                          type=element.get('type')))
            elif element.name == 'published':
                atom['published'] = str_to_datetime(element.text)
            elif element.name == 'rights':
                atom['rights'] = str_to_datetime(element.text)
            elif element.name == 'source':
                # TODO: implement it
                pass
            elif element.name == 'summary':
                atom['summary'] = element.text
            elif element.name == 'title':
                atom['title'] = element.text
            elif element.name == 'updated':
                atom['updated'] = str_to_datetime(element.text)
            elif element.name == 'entry':
                atom['updated'] = AtomFeed.parse_xml(element)
        atom = ActivityStreams.parse_xml(xml, atom)
        return atom

salmon = '<?xml version="1.0" encoding="UTF-8"?><me:env xmlns:me="http://salmon-protocol.org/ns/magic-env"><me:data type="application/atom+xml">PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiID8-PGVudHJ5IHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDA1L0F0b20iIHhtbG5zOnRocj0iaHR0cDovL3B1cmwub3JnL3N5bmRpY2F0aW9uL3RocmVhZC8xLjAiIHhtbG5zOmFjdGl2aXR5PSJodHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zcGVjLzEuMC8iIHhtbG5zOmdlb3Jzcz0iaHR0cDovL3d3dy5nZW9yc3Mub3JnL2dlb3JzcyIgeG1sbnM6b3N0YXR1cz0iaHR0cDovL29zdGF0dXMub3JnL3NjaGVtYS8xLjAiIHhtbG5zOnBvY289Imh0dHA6Ly9wb3J0YWJsZWNvbnRhY3RzLm5ldC9zcGVjLzEuMCIgeG1sbnM6bWVkaWE9Imh0dHA6Ly9wdXJsLm9yZy9zeW5kaWNhdGlvbi9hdG9tbWVkaWEiIHhtbG5zOnN0YXR1c25ldD0iaHR0cDovL3N0YXR1cy5uZXQvc2NoZW1hL2FwaS8xLyI-CiA8YWN0aXZpdHk6b2JqZWN0LXR5cGU-aHR0cDovL2FjdGl2aXR5c3RyZWEubXMvc2NoZW1hLzEuMC9ub3RlPC9hY3Rpdml0eTpvYmplY3QtdHlwZT4KIDxpZD5odHRwOi8vc24vbm90aWNlLzE1PC9pZD4KIDxjb250ZW50IHR5cGU9Imh0bWwiPmhpIEAmbHQ7c3BhbiBjbGFzcz0mcXVvdDt2Y2FyZCZxdW90OyZndDsmbHQ7YSBocmVmPSZxdW90O2h0dHA6Ly8xMjcuMC4wLjIvYmlqYW4mcXVvdDsgY2xhc3M9JnF1b3Q7dXJsJnF1b3Q7Jmd0OyZsdDtzcGFuIGNsYXNzPSZxdW90O2ZuIG5pY2tuYW1lIG1lbnRpb24mcXVvdDsmZ3Q7YmlqYW4mbHQ7L3NwYW4mZ3Q7Jmx0Oy9hJmd0OyZsdDsvc3BhbiZndDs8L2NvbnRlbnQ-CiA8bGluayByZWw9ImFsdGVybmF0ZSIgdHlwZT0idGV4dC9odG1sIiBocmVmPSJodHRwOi8vc24vbm90aWNlLzE1Ii8-CiA8c3RhdHVzX25ldCBub3RpY2VfaWQ9IjE1Ij48L3N0YXR1c19uZXQ-CiA8YWN0aXZpdHk6dmVyYj5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3Bvc3Q8L2FjdGl2aXR5OnZlcmI-CiA8cHVibGlzaGVkPjIwMTMtMDgtMTdUMTE6NDg6MDgrMDA6MDA8L3B1Ymxpc2hlZD4KIDx1cGRhdGVkPjIwMTMtMDgtMTdUMTE6NDg6MDgrMDA6MDA8L3VwZGF0ZWQ-CiA8YXV0aG9yPgogIDxhY3Rpdml0eTpvYmplY3QtdHlwZT5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3BlcnNvbjwvYWN0aXZpdHk6b2JqZWN0LXR5cGU-CiAgPHVyaT5odHRwOi8vc24vdXNlci8xPC91cmk-CiAgPG5hbWU-c248L25hbWU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovL3NuL3NuIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL3BuZyIgbWVkaWE6d2lkdGg9Ijk2IiBtZWRpYTpoZWlnaHQ9Ijk2IiBocmVmPSJodHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLXByb2ZpbGUucG5nIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL3BuZyIgbWVkaWE6d2lkdGg9IjQ4IiBtZWRpYTpoZWlnaHQ9IjQ4IiBocmVmPSJodHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLXN0cmVhbS5wbmciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvcG5nIiBtZWRpYTp3aWR0aD0iMjQiIG1lZGlhOmhlaWdodD0iMjQiIGhyZWY9Imh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItbWluaS5wbmciLz4KICA8cG9jbzpwcmVmZXJyZWRVc2VybmFtZT5zbjwvcG9jbzpwcmVmZXJyZWRVc2VybmFtZT4KICA8cG9jbzpkaXNwbGF5TmFtZT5iaWphbjwvcG9jbzpkaXNwbGF5TmFtZT4KICA8Zm9sbG93ZXJzIHVybD0iaHR0cDovL3NuL3NuL3N1YnNjcmliZXJzIj48L2ZvbGxvd2Vycz4KICA8c3RhdHVzbmV0OnByb2ZpbGVfaW5mbyBsb2NhbF9pZD0iMSI-PC9zdGF0dXNuZXQ6cHJvZmlsZV9pbmZvPgogPC9hdXRob3I-CiA8bGluayByZWw9Im9zdGF0dXM6Y29udmVyc2F0aW9uIiBocmVmPSJodHRwOi8vc24vY29udmVyc2F0aW9uLzE1Ii8-CiA8bGluayByZWw9Im9zdGF0dXM6YXR0ZW50aW9uIiBocmVmPSJodHRwOi8vMTI3LjAuMC4yL2JpamFuIi8-CiA8bGluayByZWw9Im1lbnRpb25lZCIgaHJlZj0iaHR0cDovLzEyNy4wLjAuMi9iaWphbiIvPgogPGxpbmsgcmVsPSJvc3RhdHVzOmF0dGVudGlvbiIgaHJlZj0iaHR0cDovL2FjdGl2aXR5c2NoZW1hLm9yZy9jb2xsZWN0aW9uL3B1YmxpYyIvPgogPGxpbmsgcmVsPSJtZW50aW9uZWQiIGhyZWY9Imh0dHA6Ly9hY3Rpdml0eXNjaGVtYS5vcmcvY29sbGVjdGlvbi9wdWJsaWMiLz4KIDxjYXRlZ29yeSB0ZXJtPSIiPjwvY2F0ZWdvcnk-CiA8c291cmNlPgogIDxpZD5odHRwOi8vc24vYXBpL3N0YXR1c2VzL3VzZXJfdGltZWxpbmUvMS5hdG9tPC9pZD4KICA8dGl0bGU-YmlqYW48L3RpdGxlPgogIDxsaW5rIHJlbD0iYWx0ZXJuYXRlIiB0eXBlPSJ0ZXh0L2h0bWwiIGhyZWY9Imh0dHA6Ly9zbi9zbiIvPgogIDxsaW5rIHJlbD0ic2VsZiIgdHlwZT0iYXBwbGljYXRpb24vYXRvbSt4bWwiIGhyZWY9Imh0dHA6Ly9zbi9hcGkvc3RhdHVzZXMvdXNlcl90aW1lbGluZS8xLmF0b20iLz4KICA8bGluayByZWw9ImxpY2Vuc2UiIGhyZWY9Imh0dHA6Ly9jcmVhdGl2ZWNvbW1vbnMub3JnL2xpY2Vuc2VzL2J5LzMuMC8iLz4KICA8aWNvbj5odHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLXByb2ZpbGUucG5nPC9pY29uPgogIDx1cGRhdGVkPjIwMTMtMDgtMTdUMTE6NDg6MDgrMDA6MDA8L3VwZGF0ZWQ-CiA8L3NvdXJjZT4KIDxsaW5rIHJlbD0ic2VsZiIgdHlwZT0iYXBwbGljYXRpb24vYXRvbSt4bWwiIGhyZWY9Imh0dHA6Ly9zbi9hcGkvc3RhdHVzZXMvc2hvdy8xNS5hdG9tIi8-CiA8bGluayByZWw9ImVkaXQiIHR5cGU9ImFwcGxpY2F0aW9uL2F0b20reG1sIiBocmVmPSJodHRwOi8vc24vYXBpL3N0YXR1c2VzL3Nob3cvMTUuYXRvbSIvPgogPHN0YXR1c25ldDpub3RpY2VfaW5mbyBsb2NhbF9pZD0iMTUiIHNvdXJjZT0id2ViIj48L3N0YXR1c25ldDpub3RpY2VfaW5mbz4KPC9lbnRyeT4K</me:data><me:encoding>base64url</me:encoding><me:alg>RSA-SHA256</me:alg><me:sig>AynbA2UncLlsnggO53swWisIko_533RQ107uTteK-tX_eKf9x2Gz3zvQu4U-MO7EoozpJ1JzRGXnc0mbxK2LzzfOoYziovpissGkaCfuPp85jL8LFk9pzv3Qwn4ZqvYBAtE9MqZtwLjx-eFUxoPyEWfoZGihmTTXbNCubEvp8JM=</me:sig></me:env>'
salmon1='<?xml version="1.0" encoding="UTF-8"?><me:env xmlns:me="http://salmon-protocol.org/ns/magic-env"><me:data type="application/atom+xml">PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiID8-PGVudHJ5IHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDA1L0F0b20iIHhtbG5zOnRocj0iaHR0cDovL3B1cmwub3JnL3N5bmRpY2F0aW9uL3RocmVhZC8xLjAiIHhtbG5zOmFjdGl2aXR5PSJodHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zcGVjLzEuMC8iIHhtbG5zOmdlb3Jzcz0iaHR0cDovL3d3dy5nZW9yc3Mub3JnL2dlb3JzcyIgeG1sbnM6b3N0YXR1cz0iaHR0cDovL29zdGF0dXMub3JnL3NjaGVtYS8xLjAiIHhtbG5zOnBvY289Imh0dHA6Ly9wb3J0YWJsZWNvbnRhY3RzLm5ldC9zcGVjLzEuMCIgeG1sbnM6bWVkaWE9Imh0dHA6Ly9wdXJsLm9yZy9zeW5kaWNhdGlvbi9hdG9tbWVkaWEiIHhtbG5zOnN0YXR1c25ldD0iaHR0cDovL3N0YXR1cy5uZXQvc2NoZW1hL2FwaS8xLyI-CiA8aWQ-dGFnOnNuLDIwMTMtMDgtMTg6cG9zdDoxPC9pZD4KIDx0aXRsZT48L3RpdGxlPgogPGNvbnRlbnQgdHlwZT0iaHRtbCI-Jmx0O2EgaHJlZj0mcXVvdDtodHRwOi8vc24vc24mcXVvdDsmZ3Q7c24mbHQ7L2EmZ3Q7IHN0YXJ0ZWQgZm9sbG93aW5nICZsdDthIGhyZWY9JnF1b3Q7aHR0cDovLzEyNy4wLjAuMi9iaWphbiZxdW90OyZndDtiaWphbiZsdDsvYSZndDsuPC9jb250ZW50PgogPGFjdGl2aXR5OnZlcmI-aHR0cDovL2FjdGl2aXR5c3RyZWEubXMvc2NoZW1hLzEuMC9mb2xsb3c8L2FjdGl2aXR5OnZlcmI-CiA8cHVibGlzaGVkPjIwMTMtMDgtMThUMDg6NTc6MzkrMDA6MDA8L3B1Ymxpc2hlZD4KIDx1cGRhdGVkPjIwMTMtMDgtMThUMDg6NTc6MzkrMDA6MDA8L3VwZGF0ZWQ-CiA8YXV0aG9yPgogIDxhY3Rpdml0eTpvYmplY3QtdHlwZT5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3BlcnNvbjwvYWN0aXZpdHk6b2JqZWN0LXR5cGU-CiAgPHVyaT5odHRwOi8vc24vdXNlci8xPC91cmk-CiAgPG5hbWU-c248L25hbWU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovL3NuL3NuIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL3BuZyIgbWVkaWE6d2lkdGg9Ijk2IiBtZWRpYTpoZWlnaHQ9Ijk2IiBocmVmPSJodHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLXByb2ZpbGUucG5nIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL3BuZyIgbWVkaWE6d2lkdGg9IjQ4IiBtZWRpYTpoZWlnaHQ9IjQ4IiBocmVmPSJodHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLXN0cmVhbS5wbmciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvcG5nIiBtZWRpYTp3aWR0aD0iMjQiIG1lZGlhOmhlaWdodD0iMjQiIGhyZWY9Imh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItbWluaS5wbmciLz4KICA8cG9jbzpwcmVmZXJyZWRVc2VybmFtZT5zbjwvcG9jbzpwcmVmZXJyZWRVc2VybmFtZT4KICA8cG9jbzpkaXNwbGF5TmFtZT5zbjwvcG9jbzpkaXNwbGF5TmFtZT4KICA8Zm9sbG93ZXJzIHVybD0iaHR0cDovL3NuL3NuL3N1YnNjcmliZXJzIj48L2ZvbGxvd2Vycz4KICA8c3RhdHVzbmV0OnByb2ZpbGVfaW5mbyBsb2NhbF9pZD0iMSI-PC9zdGF0dXNuZXQ6cHJvZmlsZV9pbmZvPgogPC9hdXRob3I-CiA8YWN0aXZpdHk6b2JqZWN0PgogIDxhY3Rpdml0eTpvYmplY3QtdHlwZT5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3BlcnNvbjwvYWN0aXZpdHk6b2JqZWN0LXR5cGU-CiAgPGlkPmh0dHA6Ly8xMjcuMC4wLjIvYmlqYW48L2lkPgogIDx0aXRsZT5iaWphbjwvdGl0bGU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovLzEyNy4wLjAuMi9iaWphbiIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9qcGVnIiBtZWRpYTp3aWR0aD0iOTYiIG1lZGlhOmhlaWdodD0iOTYiIGhyZWY9Imh0dHA6Ly9zbi9hdmF0YXIvMi1vcmlnaW5hbC0yMDEzMDgxODA4NTYxMy5qcGVnIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL2pwZWciIG1lZGlhOndpZHRoPSI5NiIgbWVkaWE6aGVpZ2h0PSI5NiIgaHJlZj0iaHR0cDovL3NuL2F2YXRhci8yLW9yaWdpbmFsLTIwMTMwODE4MDg1NjEzLmpwZWciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvanBlZyIgbWVkaWE6d2lkdGg9IjQ4IiBtZWRpYTpoZWlnaHQ9IjQ4IiBocmVmPSJodHRwOi8vc24vYXZhdGFyLzItNDgtMjAxMzA4MTgwODU2MTQuanBlZyIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9qcGVnIiBtZWRpYTp3aWR0aD0iMjQiIG1lZGlhOmhlaWdodD0iMjQiIGhyZWY9Imh0dHA6Ly9zbi9hdmF0YXIvMi0yNC0yMDEzMDgxODA4NTYxNC5qcGVnIi8-CiAgPHBvY286cHJlZmVycmVkVXNlcm5hbWU-YmlqYW48L3BvY286cHJlZmVycmVkVXNlcm5hbWU-CiAgPHBvY286ZGlzcGxheU5hbWU-YmlqYW48L3BvY286ZGlzcGxheU5hbWU-CiAgPHBvY286bm90ZT5ubyBkZXNjcmlwdGlvbiBpcyBwcm92aWRlZDwvcG9jbzpub3RlPgogIDxwb2NvOmFkZHJlc3M-CiAgIDxwb2NvOmZvcm1hdHRlZD5ubyBsb2NhdGlvbiBpcyBwcm92aWRlZDwvcG9jbzpmb3JtYXR0ZWQ-CiAgPC9wb2NvOmFkZHJlc3M-CiAgPHBvY286dXJscz4KICAgPHBvY286dHlwZT5ob21lcGFnZTwvcG9jbzp0eXBlPgogICA8cG9jbzp2YWx1ZT5odHRwOi8vZXhhbXBsZS5jb208L3BvY286dmFsdWU-CiAgIDxwb2NvOnByaW1hcnk-dHJ1ZTwvcG9jbzpwcmltYXJ5PgogIDwvcG9jbzp1cmxzPgogPC9hY3Rpdml0eTpvYmplY3Q-CiA8bGluayByZWw9Im9zdGF0dXM6Y29udmVyc2F0aW9uIiBocmVmPSJodHRwOi8vc24vY29udmVyc2F0aW9uLzEiLz4KIDxsaW5rIHJlbD0ib3N0YXR1czphdHRlbnRpb24iIGhyZWY9Imh0dHA6Ly8xMjcuMC4wLjIvYmlqYW4iLz4KIDxsaW5rIHJlbD0ibWVudGlvbmVkIiBocmVmPSJodHRwOi8vMTI3LjAuMC4yL2JpamFuIi8-CiA8bGluayByZWw9Im9zdGF0dXM6YXR0ZW50aW9uIiBocmVmPSJodHRwOi8vYWN0aXZpdHlzY2hlbWEub3JnL2NvbGxlY3Rpb24vcHVibGljIi8-CiA8bGluayByZWw9Im1lbnRpb25lZCIgaHJlZj0iaHR0cDovL2FjdGl2aXR5c2NoZW1hLm9yZy9jb2xsZWN0aW9uL3B1YmxpYyIvPgogPGNhdGVnb3J5IHRlcm09IiI-PC9jYXRlZ29yeT4KIDxzb3VyY2U-CiAgPGlkPmh0dHA6Ly9zbi9hcGkvc3RhdHVzZXMvdXNlcl90aW1lbGluZS8xLmF0b208L2lkPgogIDx0aXRsZT5zbjwvdGl0bGU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovL3NuL3NuIi8-CiAgPGxpbmsgcmVsPSJzZWxmIiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNlcy91c2VyX3RpbWVsaW5lLzEuYXRvbSIvPgogIDxsaW5rIHJlbD0ibGljZW5zZSIgaHJlZj0iaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvbGljZW5zZXMvYnkvMy4wLyIvPgogIDxpY29uPmh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItcHJvZmlsZS5wbmc8L2ljb24-CiAgPHVwZGF0ZWQ-MjAxMy0wOC0xOFQwODo1NzozOSswMDowMDwvdXBkYXRlZD4KIDwvc291cmNlPgogPGxpbmsgcmVsPSJzZWxmIiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNlcy9zaG93LzEuYXRvbSIvPgogPGxpbmsgcmVsPSJlZGl0IiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNlcy9zaG93LzEuYXRvbSIvPgogPHN0YXR1c25ldDpub3RpY2VfaW5mbyBsb2NhbF9pZD0iMSIgc291cmNlPSJhY3Rpdml0eSI-PC9zdGF0dXNuZXQ6bm90aWNlX2luZm8-CjwvZW50cnk-Cg==</me:data><me:encoding>base64url</me:encoding><me:alg>RSA-SHA256</me:alg><me:sig>jLsQxPL648cWNCVhRlhS6kOSPh1yKyT4sYdRTFGoj0vaW2wmqAHeZD8lnMnp6b7QdMs8n4P9uGaDT9_3BRJraDkEMa5IuRloChPFml0kxhlGl2iBlixGeiXbcl-TUB3yXp5KBOcJ6il7s2i32kaalUNvP9V7Z1Cob0eHdcRyF2s=</me:sig></me:env>'
salmon2='<?xml version="1.0" encoding="UTF-8"?><me:env xmlns:me="http://salmon-protocol.org/ns/magic-env"><me:data type="application/atom+xml">PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiID8-PGVudHJ5IHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDA1L0F0b20iIHhtbG5zOnRocj0iaHR0cDovL3B1cmwub3JnL3N5bmRpY2F0aW9uL3RocmVhZC8xLjAiIHhtbG5zOmFjdGl2aXR5PSJodHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zcGVjLzEuMC8iIHhtbG5zOmdlb3Jzcz0iaHR0cDovL3d3dy5nZW9yc3Mub3JnL2dlb3JzcyIgeG1sbnM6b3N0YXR1cz0iaHR0cDovL29zdGF0dXMub3JnL3NjaGVtYS8xLjAiIHhtbG5zOnBvY289Imh0dHA6Ly9wb3J0YWJsZWNvbnRhY3RzLm5ldC9zcGVjLzEuMCIgeG1sbnM6bWVkaWE9Imh0dHA6Ly9wdXJsLm9yZy9zeW5kaWNhdGlvbi9hdG9tbWVkaWEiIHhtbG5zOnN0YXR1c25ldD0iaHR0cDovL3N0YXR1cy5uZXQvc2NoZW1hL2FwaS8xLyI-CiA8aWQ-dGFnOnNuLDIwMTMtMDgtMTg6Zm9sbG93OjE6MjoyMDEzLTA4LTE4VDA4OjU3OjE1KzAwOjAwPC9pZD4KIDx0aXRsZT5Gb2xsb3c8L3RpdGxlPgogPGNvbnRlbnQgdHlwZT0iaHRtbCI-c24gaXMgbm93IGZvbGxvd2luZyBiaWphbi48L2NvbnRlbnQ-CiA8YWN0aXZpdHk6dmVyYj5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL2ZvbGxvdzwvYWN0aXZpdHk6dmVyYj4KIDxwdWJsaXNoZWQ-MjAxMy0wOC0xOFQwODo1NzoxNSswMDowMDwvcHVibGlzaGVkPgogPHVwZGF0ZWQ-MjAxMy0wOC0xOFQwODo1NzoxNSswMDowMDwvdXBkYXRlZD4KIDxhdXRob3I-CiAgPGFjdGl2aXR5Om9iamVjdC10eXBlPmh0dHA6Ly9hY3Rpdml0eXN0cmVhLm1zL3NjaGVtYS8xLjAvcGVyc29uPC9hY3Rpdml0eTpvYmplY3QtdHlwZT4KICA8dXJpPmh0dHA6Ly9zbi91c2VyLzE8L3VyaT4KICA8bmFtZT5zbjwvbmFtZT4KICA8bGluayByZWw9ImFsdGVybmF0ZSIgdHlwZT0idGV4dC9odG1sIiBocmVmPSJodHRwOi8vc24vc24iLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvcG5nIiBtZWRpYTp3aWR0aD0iOTYiIG1lZGlhOmhlaWdodD0iOTYiIGhyZWY9Imh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItcHJvZmlsZS5wbmciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvcG5nIiBtZWRpYTp3aWR0aD0iNDgiIG1lZGlhOmhlaWdodD0iNDgiIGhyZWY9Imh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItc3RyZWFtLnBuZyIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9wbmciIG1lZGlhOndpZHRoPSIyNCIgbWVkaWE6aGVpZ2h0PSIyNCIgaHJlZj0iaHR0cDovL3NuL3RoZW1lL25lby9kZWZhdWx0LWF2YXRhci1taW5pLnBuZyIvPgogIDxwb2NvOnByZWZlcnJlZFVzZXJuYW1lPnNuPC9wb2NvOnByZWZlcnJlZFVzZXJuYW1lPgogIDxwb2NvOmRpc3BsYXlOYW1lPnNuPC9wb2NvOmRpc3BsYXlOYW1lPgogIDxmb2xsb3dlcnMgdXJsPSJodHRwOi8vc24vc24vc3Vic2NyaWJlcnMiPjwvZm9sbG93ZXJzPgogPC9hdXRob3I-CiA8YWN0aXZpdHk6b2JqZWN0PgogIDxhY3Rpdml0eTpvYmplY3QtdHlwZT5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3BlcnNvbjwvYWN0aXZpdHk6b2JqZWN0LXR5cGU-CiAgPGlkPmh0dHA6Ly8xMjcuMC4wLjIvYmlqYW48L2lkPgogIDx0aXRsZT5iaWphbjwvdGl0bGU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovLzEyNy4wLjAuMi9iaWphbiIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9qcGVnIiBtZWRpYTp3aWR0aD0iOTYiIG1lZGlhOmhlaWdodD0iOTYiIGhyZWY9Imh0dHA6Ly9zbi9hdmF0YXIvMi1vcmlnaW5hbC0yMDEzMDgxODA4NTYxMy5qcGVnIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL2pwZWciIG1lZGlhOndpZHRoPSI5NiIgbWVkaWE6aGVpZ2h0PSI5NiIgaHJlZj0iaHR0cDovL3NuL2F2YXRhci8yLW9yaWdpbmFsLTIwMTMwODE4MDg1NjEzLmpwZWciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvanBlZyIgbWVkaWE6d2lkdGg9IjQ4IiBtZWRpYTpoZWlnaHQ9IjQ4IiBocmVmPSJodHRwOi8vc24vYXZhdGFyLzItNDgtMjAxMzA4MTgwODU2MTQuanBlZyIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9qcGVnIiBtZWRpYTp3aWR0aD0iMjQiIG1lZGlhOmhlaWdodD0iMjQiIGhyZWY9Imh0dHA6Ly9zbi9hdmF0YXIvMi0yNC0yMDEzMDgxODA4NTYxNC5qcGVnIi8-CiAgPHBvY286cHJlZmVycmVkVXNlcm5hbWU-YmlqYW48L3BvY286cHJlZmVycmVkVXNlcm5hbWU-CiAgPHBvY286ZGlzcGxheU5hbWU-YmlqYW48L3BvY286ZGlzcGxheU5hbWU-CiAgPHBvY286bm90ZT5ubyBkZXNjcmlwdGlvbiBpcyBwcm92aWRlZDwvcG9jbzpub3RlPgogIDxwb2NvOmFkZHJlc3M-CiAgIDxwb2NvOmZvcm1hdHRlZD5ubyBsb2NhdGlvbiBpcyBwcm92aWRlZDwvcG9jbzpmb3JtYXR0ZWQ-CiAgPC9wb2NvOmFkZHJlc3M-CiAgPHBvY286dXJscz4KICAgPHBvY286dHlwZT5ob21lcGFnZTwvcG9jbzp0eXBlPgogICA8cG9jbzp2YWx1ZT5odHRwOi8vZXhhbXBsZS5jb208L3BvY286dmFsdWU-CiAgIDxwb2NvOnByaW1hcnk-dHJ1ZTwvcG9jbzpwcmltYXJ5PgogIDwvcG9jbzp1cmxzPgogPC9hY3Rpdml0eTpvYmplY3Q-CiA8bGluayByZWw9InNlbGYiIHR5cGU9ImFwcGxpY2F0aW9uL2F0b20reG1sIiBocmVmPSJodHRwOi8vc24vYXBpL3N0YXR1c25ldC9hcHAvc3Vic2NyaXB0aW9ucy8xLzIuYXRvbSIvPgogPGxpbmsgcmVsPSJlZGl0IiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNuZXQvYXBwL3N1YnNjcmlwdGlvbnMvMS8yLmF0b20iLz4KPC9lbnRyeT4K</me:data><me:encoding>base64url</me:encoding><me:alg>RSA-SHA256</me:alg><me:sig>ZWy5MOMbGjuLPBCsXrQujwPwYDWUyGjVlCnALFF1lCXkM4vY3_AEsUUJaX_QDwab4R6wd6Eg36RwmQKCdxp8QXtvPkBp4RqLwbwgtjX4udU6EusISb2Xgc_vzDVcqb9eAIPsHaFbH0I8M15FTS7GkWQ-2ot9_ZvQbPXv06cwGO4=</me:sig></me:env>'
salmon3='<?xml version="1.0" encoding="UTF-8"?><me:env xmlns:me="http://salmon-protocol.org/ns/magic-env"><me:data type="application/atom+xml">PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiID8-PGVudHJ5IHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDA1L0F0b20iIHhtbG5zOnRocj0iaHR0cDovL3B1cmwub3JnL3N5bmRpY2F0aW9uL3RocmVhZC8xLjAiIHhtbG5zOmFjdGl2aXR5PSJodHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zcGVjLzEuMC8iIHhtbG5zOmdlb3Jzcz0iaHR0cDovL3d3dy5nZW9yc3Mub3JnL2dlb3JzcyIgeG1sbnM6b3N0YXR1cz0iaHR0cDovL29zdGF0dXMub3JnL3NjaGVtYS8xLjAiIHhtbG5zOnBvY289Imh0dHA6Ly9wb3J0YWJsZWNvbnRhY3RzLm5ldC9zcGVjLzEuMCIgeG1sbnM6bWVkaWE9Imh0dHA6Ly9wdXJsLm9yZy9zeW5kaWNhdGlvbi9hdG9tbWVkaWEiIHhtbG5zOnN0YXR1c25ldD0iaHR0cDovL3N0YXR1cy5uZXQvc2NoZW1hL2FwaS8xLyI-CiA8aWQ-dGFnOnNuLDIwMTMtMDgtMTg6dW5mb2xsb3c6MToyOjE5NzAtMDEtMDFUMDA6MDA6MDArMDA6MDA8L2lkPgogPHRpdGxlPlVuZm9sbG93PC90aXRsZT4KIDxjb250ZW50IHR5cGU9Imh0bWwiPnNuIHN0b3BwZWQgZm9sbG93aW5nIGJpamFuLjwvY29udGVudD4KIDxhY3Rpdml0eTp2ZXJiPmh0dHA6Ly9vc3RhdHVzLm9yZy9zY2hlbWEvMS4wL3VuZm9sbG93PC9hY3Rpdml0eTp2ZXJiPgogPHB1Ymxpc2hlZD4yMDEzLTA4LTE4VDA5OjI3OjMyKzAwOjAwPC9wdWJsaXNoZWQ-CiA8dXBkYXRlZD4yMDEzLTA4LTE4VDA5OjI3OjMyKzAwOjAwPC91cGRhdGVkPgogPGF1dGhvcj4KICA8YWN0aXZpdHk6b2JqZWN0LXR5cGU-aHR0cDovL2FjdGl2aXR5c3RyZWEubXMvc2NoZW1hLzEuMC9wZXJzb248L2FjdGl2aXR5Om9iamVjdC10eXBlPgogIDx1cmk-aHR0cDovL3NuL3VzZXIvMTwvdXJpPgogIDxuYW1lPnNuPC9uYW1lPgogIDxsaW5rIHJlbD0iYWx0ZXJuYXRlIiB0eXBlPSJ0ZXh0L2h0bWwiIGhyZWY9Imh0dHA6Ly9zbi9zbiIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9wbmciIG1lZGlhOndpZHRoPSI5NiIgbWVkaWE6aGVpZ2h0PSI5NiIgaHJlZj0iaHR0cDovL3NuL3RoZW1lL25lby9kZWZhdWx0LWF2YXRhci1wcm9maWxlLnBuZyIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9wbmciIG1lZGlhOndpZHRoPSI0OCIgbWVkaWE6aGVpZ2h0PSI0OCIgaHJlZj0iaHR0cDovL3NuL3RoZW1lL25lby9kZWZhdWx0LWF2YXRhci1zdHJlYW0ucG5nIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL3BuZyIgbWVkaWE6d2lkdGg9IjI0IiBtZWRpYTpoZWlnaHQ9IjI0IiBocmVmPSJodHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLW1pbmkucG5nIi8-CiAgPHBvY286cHJlZmVycmVkVXNlcm5hbWU-c248L3BvY286cHJlZmVycmVkVXNlcm5hbWU-CiAgPHBvY286ZGlzcGxheU5hbWU-c248L3BvY286ZGlzcGxheU5hbWU-CiAgPGZvbGxvd2VycyB1cmw9Imh0dHA6Ly9zbi9zbi9zdWJzY3JpYmVycyI-PC9mb2xsb3dlcnM-CiA8L2F1dGhvcj4KPC9lbnRyeT4K</me:data><me:encoding>base64url</me:encoding><me:alg>RSA-SHA256</me:alg><me:sig>gGyvo_44iNV5O5V5SQwzp5vnOvvBP74-ks3hgvGUBNQ1TQSZUrq7M1bDXN5A5ttf2j7P_mO96f9T5aQqE7qxoLk4w1E4YE6RZrOFG_Kj5mMU2E-O5SKQmZP2tf7OUQX343n_Wifhy-128YKaOTkjJc2hORbWpJj5wHx6CzuNi_c=</me:sig></me:env>'


salmon4='<?xml version="1.0" encoding="UTF-8"?><me:env xmlns:me="http://salmon-protocol.org/ns/magic-env"><me:data type="application/atom+xml">PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiID8-PGVudHJ5IHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDA1L0F0b20iIHhtbG5zOnRocj0iaHR0cDovL3B1cmwub3JnL3N5bmRpY2F0aW9uL3RocmVhZC8xLjAiIHhtbG5zOmFjdGl2aXR5PSJodHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zcGVjLzEuMC8iIHhtbG5zOmdlb3Jzcz0iaHR0cDovL3d3dy5nZW9yc3Mub3JnL2dlb3JzcyIgeG1sbnM6b3N0YXR1cz0iaHR0cDovL29zdGF0dXMub3JnL3NjaGVtYS8xLjAiIHhtbG5zOnBvY289Imh0dHA6Ly9wb3J0YWJsZWNvbnRhY3RzLm5ldC9zcGVjLzEuMCIgeG1sbnM6bWVkaWE9Imh0dHA6Ly9wdXJsLm9yZy9zeW5kaWNhdGlvbi9hdG9tbWVkaWEiIHhtbG5zOnN0YXR1c25ldD0iaHR0cDovL3N0YXR1cy5uZXQvc2NoZW1hL2FwaS8xLyI-CiA8aWQ-dGFnOnNuLDIwMTMtMDgtMTk6cG9zdDoyPC9pZD4KIDx0aXRsZT48L3RpdGxlPgogPGNvbnRlbnQgdHlwZT0iaHRtbCI-Jmx0O2EgaHJlZj0mcXVvdDtodHRwOi8vc24vc24mcXVvdDsmZ3Q7c24mbHQ7L2EmZ3Q7IHN0YXJ0ZWQgZm9sbG93aW5nICZsdDthIGhyZWY9JnF1b3Q7aHR0cDovLzEyNy4wLjAuMi9iaWphbiZxdW90OyZndDtiaWphbiZsdDsvYSZndDsuPC9jb250ZW50PgogPGFjdGl2aXR5OnZlcmI-aHR0cDovL2FjdGl2aXR5c3RyZWEubXMvc2NoZW1hLzEuMC9mb2xsb3c8L2FjdGl2aXR5OnZlcmI-CiA8cHVibGlzaGVkPjIwMTMtMDgtMTlUMDY6MzU6NDIrMDA6MDA8L3B1Ymxpc2hlZD4KIDx1cGRhdGVkPjIwMTMtMDgtMTlUMDY6MzU6NDIrMDA6MDA8L3VwZGF0ZWQ-CiA8YXV0aG9yPgogIDxhY3Rpdml0eTpvYmplY3QtdHlwZT5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3BlcnNvbjwvYWN0aXZpdHk6b2JqZWN0LXR5cGU-CiAgPHVyaT5odHRwOi8vc24vdXNlci8xPC91cmk-CiAgPG5hbWU-c248L25hbWU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovL3NuL3NuIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL3BuZyIgbWVkaWE6d2lkdGg9Ijk2IiBtZWRpYTpoZWlnaHQ9Ijk2IiBocmVmPSJodHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLXByb2ZpbGUucG5nIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL3BuZyIgbWVkaWE6d2lkdGg9IjQ4IiBtZWRpYTpoZWlnaHQ9IjQ4IiBocmVmPSJodHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLXN0cmVhbS5wbmciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvcG5nIiBtZWRpYTp3aWR0aD0iMjQiIG1lZGlhOmhlaWdodD0iMjQiIGhyZWY9Imh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItbWluaS5wbmciLz4KICA8cG9jbzpwcmVmZXJyZWRVc2VybmFtZT5zbjwvcG9jbzpwcmVmZXJyZWRVc2VybmFtZT4KICA8cG9jbzpkaXNwbGF5TmFtZT5zbjwvcG9jbzpkaXNwbGF5TmFtZT4KICA8Zm9sbG93ZXJzIHVybD0iaHR0cDovL3NuL3NuL3N1YnNjcmliZXJzIj48L2ZvbGxvd2Vycz4KICA8c3RhdHVzbmV0OnByb2ZpbGVfaW5mbyBsb2NhbF9pZD0iMSI-PC9zdGF0dXNuZXQ6cHJvZmlsZV9pbmZvPgogPC9hdXRob3I-CiA8YWN0aXZpdHk6b2JqZWN0PgogIDxhY3Rpdml0eTpvYmplY3QtdHlwZT5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3BlcnNvbjwvYWN0aXZpdHk6b2JqZWN0LXR5cGU-CiAgPGlkPmh0dHA6Ly8xMjcuMC4wLjIvYmlqYW48L2lkPgogIDx0aXRsZT5iaWphbjwvdGl0bGU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovLzEyNy4wLjAuMi9iaWphbiIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9qcGVnIiBtZWRpYTp3aWR0aD0iOTYiIG1lZGlhOmhlaWdodD0iOTYiIGhyZWY9Imh0dHA6Ly9zbi9hdmF0YXIvMi1vcmlnaW5hbC0yMDEzMDgxODA4NTYxMy5qcGVnIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL2pwZWciIG1lZGlhOndpZHRoPSI5NiIgbWVkaWE6aGVpZ2h0PSI5NiIgaHJlZj0iaHR0cDovL3NuL2F2YXRhci8yLW9yaWdpbmFsLTIwMTMwODE4MDg1NjEzLmpwZWciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvanBlZyIgbWVkaWE6d2lkdGg9IjQ4IiBtZWRpYTpoZWlnaHQ9IjQ4IiBocmVmPSJodHRwOi8vc24vYXZhdGFyLzItNDgtMjAxMzA4MTgwODU2MTQuanBlZyIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9qcGVnIiBtZWRpYTp3aWR0aD0iMjQiIG1lZGlhOmhlaWdodD0iMjQiIGhyZWY9Imh0dHA6Ly9zbi9hdmF0YXIvMi0yNC0yMDEzMDgxODA4NTYxNC5qcGVnIi8-CiAgPHBvY286cHJlZmVycmVkVXNlcm5hbWU-YmlqYW48L3BvY286cHJlZmVycmVkVXNlcm5hbWU-CiAgPHBvY286ZGlzcGxheU5hbWU-YmlqYW48L3BvY286ZGlzcGxheU5hbWU-CiAgPHBvY286bm90ZT5ubyBkZXNjcmlwdGlvbiBpcyBwcm92aWRlZDwvcG9jbzpub3RlPgogIDxwb2NvOmFkZHJlc3M-CiAgIDxwb2NvOmZvcm1hdHRlZD5ubyBsb2NhdGlvbiBpcyBwcm92aWRlZDwvcG9jbzpmb3JtYXR0ZWQ-CiAgPC9wb2NvOmFkZHJlc3M-CiAgPHBvY286dXJscz4KICAgPHBvY286dHlwZT5ob21lcGFnZTwvcG9jbzp0eXBlPgogICA8cG9jbzp2YWx1ZT5odHRwOi8vZXhhbXBsZS5jb208L3BvY286dmFsdWU-CiAgIDxwb2NvOnByaW1hcnk-dHJ1ZTwvcG9jbzpwcmltYXJ5PgogIDwvcG9jbzp1cmxzPgogPC9hY3Rpdml0eTpvYmplY3Q-CiA8bGluayByZWw9Im9zdGF0dXM6Y29udmVyc2F0aW9uIiBocmVmPSJodHRwOi8vc24vY29udmVyc2F0aW9uLzIiLz4KIDxsaW5rIHJlbD0ib3N0YXR1czphdHRlbnRpb24iIGhyZWY9Imh0dHA6Ly8xMjcuMC4wLjIvYmlqYW4iLz4KIDxsaW5rIHJlbD0ibWVudGlvbmVkIiBocmVmPSJodHRwOi8vMTI3LjAuMC4yL2JpamFuIi8-CiA8bGluayByZWw9Im9zdGF0dXM6YXR0ZW50aW9uIiBocmVmPSJodHRwOi8vYWN0aXZpdHlzY2hlbWEub3JnL2NvbGxlY3Rpb24vcHVibGljIi8-CiA8bGluayByZWw9Im1lbnRpb25lZCIgaHJlZj0iaHR0cDovL2FjdGl2aXR5c2NoZW1hLm9yZy9jb2xsZWN0aW9uL3B1YmxpYyIvPgogPGNhdGVnb3J5IHRlcm09IiI-PC9jYXRlZ29yeT4KIDxzb3VyY2U-CiAgPGlkPmh0dHA6Ly9zbi9hcGkvc3RhdHVzZXMvdXNlcl90aW1lbGluZS8xLmF0b208L2lkPgogIDx0aXRsZT5zbjwvdGl0bGU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovL3NuL3NuIi8-CiAgPGxpbmsgcmVsPSJzZWxmIiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNlcy91c2VyX3RpbWVsaW5lLzEuYXRvbSIvPgogIDxsaW5rIHJlbD0ibGljZW5zZSIgaHJlZj0iaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvbGljZW5zZXMvYnkvMy4wLyIvPgogIDxpY29uPmh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItcHJvZmlsZS5wbmc8L2ljb24-CiAgPHVwZGF0ZWQ-MjAxMy0wOC0xOVQwNjozNTo0MiswMDowMDwvdXBkYXRlZD4KIDwvc291cmNlPgogPGxpbmsgcmVsPSJzZWxmIiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNlcy9zaG93LzIuYXRvbSIvPgogPGxpbmsgcmVsPSJlZGl0IiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNlcy9zaG93LzIuYXRvbSIvPgogPHN0YXR1c25ldDpub3RpY2VfaW5mbyBsb2NhbF9pZD0iMiIgc291cmNlPSJhY3Rpdml0eSI-PC9zdGF0dXNuZXQ6bm90aWNlX2luZm8-CjwvZW50cnk-Cg==</me:data><me:encoding>base64url</me:encoding><me:alg>RSA-SHA256</me:alg><me:sig>iVNeJvZeXBHQaJU55XrLq1cV2AP42W081lX-Eb9bi9v7JtL4skc6pRjbMW7G_NHKCNznxZ9w78cOiPaM-4IQQM-mQbs0rWXirNtaPa6-fIhiNioCpQYJnk2y8azLRfxTxbOukHrDVG1pjRRQiJaEHtgNd62BwLiVAR0sdXOwoYI=</me:sig></me:env>'
salmon5='<?xml version="1.0" encoding="UTF-8"?><me:env xmlns:me="http://salmon-protocol.org/ns/magic-env"><me:data type="application/atom+xml">PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiID8-PGVudHJ5IHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDA1L0F0b20iIHhtbG5zOnRocj0iaHR0cDovL3B1cmwub3JnL3N5bmRpY2F0aW9uL3RocmVhZC8xLjAiIHhtbG5zOmFjdGl2aXR5PSJodHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zcGVjLzEuMC8iIHhtbG5zOmdlb3Jzcz0iaHR0cDovL3d3dy5nZW9yc3Mub3JnL2dlb3JzcyIgeG1sbnM6b3N0YXR1cz0iaHR0cDovL29zdGF0dXMub3JnL3NjaGVtYS8xLjAiIHhtbG5zOnBvY289Imh0dHA6Ly9wb3J0YWJsZWNvbnRhY3RzLm5ldC9zcGVjLzEuMCIgeG1sbnM6bWVkaWE9Imh0dHA6Ly9wdXJsLm9yZy9zeW5kaWNhdGlvbi9hdG9tbWVkaWEiIHhtbG5zOnN0YXR1c25ldD0iaHR0cDovL3N0YXR1cy5uZXQvc2NoZW1hL2FwaS8xLyI-CiA8aWQ-dGFnOnNuLDIwMTMtMDgtMTk6Zm9sbG93OjE6MjoyMDEzLTA4LTE5VDA2OjM1OjQxKzAwOjAwPC9pZD4KIDx0aXRsZT5Gb2xsb3c8L3RpdGxlPgogPGNvbnRlbnQgdHlwZT0iaHRtbCI-c24gaXMgbm93IGZvbGxvd2luZyBiaWphbi48L2NvbnRlbnQ-CiA8YWN0aXZpdHk6dmVyYj5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL2ZvbGxvdzwvYWN0aXZpdHk6dmVyYj4KIDxwdWJsaXNoZWQ-MjAxMy0wOC0xOVQwNjozNTo0MSswMDowMDwvcHVibGlzaGVkPgogPHVwZGF0ZWQ-MjAxMy0wOC0xOVQwNjozNTo0MSswMDowMDwvdXBkYXRlZD4KIDxhdXRob3I-CiAgPGFjdGl2aXR5Om9iamVjdC10eXBlPmh0dHA6Ly9hY3Rpdml0eXN0cmVhLm1zL3NjaGVtYS8xLjAvcGVyc29uPC9hY3Rpdml0eTpvYmplY3QtdHlwZT4KICA8dXJpPmh0dHA6Ly9zbi91c2VyLzE8L3VyaT4KICA8bmFtZT5zbjwvbmFtZT4KICA8bGluayByZWw9ImFsdGVybmF0ZSIgdHlwZT0idGV4dC9odG1sIiBocmVmPSJodHRwOi8vc24vc24iLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvcG5nIiBtZWRpYTp3aWR0aD0iOTYiIG1lZGlhOmhlaWdodD0iOTYiIGhyZWY9Imh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItcHJvZmlsZS5wbmciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvcG5nIiBtZWRpYTp3aWR0aD0iNDgiIG1lZGlhOmhlaWdodD0iNDgiIGhyZWY9Imh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItc3RyZWFtLnBuZyIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9wbmciIG1lZGlhOndpZHRoPSIyNCIgbWVkaWE6aGVpZ2h0PSIyNCIgaHJlZj0iaHR0cDovL3NuL3RoZW1lL25lby9kZWZhdWx0LWF2YXRhci1taW5pLnBuZyIvPgogIDxwb2NvOnByZWZlcnJlZFVzZXJuYW1lPnNuPC9wb2NvOnByZWZlcnJlZFVzZXJuYW1lPgogIDxwb2NvOmRpc3BsYXlOYW1lPnNuPC9wb2NvOmRpc3BsYXlOYW1lPgogIDxmb2xsb3dlcnMgdXJsPSJodHRwOi8vc24vc24vc3Vic2NyaWJlcnMiPjwvZm9sbG93ZXJzPgogPC9hdXRob3I-CiA8YWN0aXZpdHk6b2JqZWN0PgogIDxhY3Rpdml0eTpvYmplY3QtdHlwZT5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3BlcnNvbjwvYWN0aXZpdHk6b2JqZWN0LXR5cGU-CiAgPGlkPmh0dHA6Ly8xMjcuMC4wLjIvYmlqYW48L2lkPgogIDx0aXRsZT5iaWphbjwvdGl0bGU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovLzEyNy4wLjAuMi9iaWphbiIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9qcGVnIiBtZWRpYTp3aWR0aD0iOTYiIG1lZGlhOmhlaWdodD0iOTYiIGhyZWY9Imh0dHA6Ly9zbi9hdmF0YXIvMi1vcmlnaW5hbC0yMDEzMDgxODA4NTYxMy5qcGVnIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL2pwZWciIG1lZGlhOndpZHRoPSI5NiIgbWVkaWE6aGVpZ2h0PSI5NiIgaHJlZj0iaHR0cDovL3NuL2F2YXRhci8yLW9yaWdpbmFsLTIwMTMwODE4MDg1NjEzLmpwZWciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvanBlZyIgbWVkaWE6d2lkdGg9IjQ4IiBtZWRpYTpoZWlnaHQ9IjQ4IiBocmVmPSJodHRwOi8vc24vYXZhdGFyLzItNDgtMjAxMzA4MTgwODU2MTQuanBlZyIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9qcGVnIiBtZWRpYTp3aWR0aD0iMjQiIG1lZGlhOmhlaWdodD0iMjQiIGhyZWY9Imh0dHA6Ly9zbi9hdmF0YXIvMi0yNC0yMDEzMDgxODA4NTYxNC5qcGVnIi8-CiAgPHBvY286cHJlZmVycmVkVXNlcm5hbWU-YmlqYW48L3BvY286cHJlZmVycmVkVXNlcm5hbWU-CiAgPHBvY286ZGlzcGxheU5hbWU-YmlqYW48L3BvY286ZGlzcGxheU5hbWU-CiAgPHBvY286bm90ZT5ubyBkZXNjcmlwdGlvbiBpcyBwcm92aWRlZDwvcG9jbzpub3RlPgogIDxwb2NvOmFkZHJlc3M-CiAgIDxwb2NvOmZvcm1hdHRlZD5ubyBsb2NhdGlvbiBpcyBwcm92aWRlZDwvcG9jbzpmb3JtYXR0ZWQ-CiAgPC9wb2NvOmFkZHJlc3M-CiAgPHBvY286dXJscz4KICAgPHBvY286dHlwZT5ob21lcGFnZTwvcG9jbzp0eXBlPgogICA8cG9jbzp2YWx1ZT5odHRwOi8vZXhhbXBsZS5jb208L3BvY286dmFsdWU-CiAgIDxwb2NvOnByaW1hcnk-dHJ1ZTwvcG9jbzpwcmltYXJ5PgogIDwvcG9jbzp1cmxzPgogPC9hY3Rpdml0eTpvYmplY3Q-CiA8bGluayByZWw9InNlbGYiIHR5cGU9ImFwcGxpY2F0aW9uL2F0b20reG1sIiBocmVmPSJodHRwOi8vc24vYXBpL3N0YXR1c25ldC9hcHAvc3Vic2NyaXB0aW9ucy8xLzIuYXRvbSIvPgogPGxpbmsgcmVsPSJlZGl0IiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNuZXQvYXBwL3N1YnNjcmlwdGlvbnMvMS8yLmF0b20iLz4KPC9lbnRyeT4K</me:data><me:encoding>base64url</me:encoding><me:alg>RSA-SHA256</me:alg><me:sig>FANSAxplS9lmzM2iPIQr6Vzie33V4TXWKi2QuK0Aj79AMkK2L0XoD9q_YAZBuHilkiKsKkUKMFV6xwKJEeLkP6DRnux5Ex61GqaOJzUunLRaL-rmKDxFy0g-CotQMBkjhHoTUMIiDgPD7MSLQmmCwlK9kLMTX42XUq-AnFQUz_w=</me:sig></me:env>'

salmon_mention='<me:env xmlns:me="http://salmon-protocol.org/ns/magic-env"><me:data type="application/atom+xml">PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiID8-PGVudHJ5IHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDA1L0F0b20iIHhtbG5zOnRocj0iaHR0cDovL3B1cmwub3JnL3N5bmRpY2F0aW9uL3RocmVhZC8xLjAiIHhtbG5zOmFjdGl2aXR5PSJodHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zcGVjLzEuMC8iIHhtbG5zOmdlb3Jzcz0iaHR0cDovL3d3dy5nZW9yc3Mub3JnL2dlb3JzcyIgeG1sbnM6b3N0YXR1cz0iaHR0cDovL29zdGF0dXMub3JnL3NjaGVtYS8xLjAiIHhtbG5zOnBvY289Imh0dHA6Ly9wb3J0YWJsZWNvbnRhY3RzLm5ldC9zcGVjLzEuMCIgeG1sbnM6bWVkaWE9Imh0dHA6Ly9wdXJsLm9yZy9zeW5kaWNhdGlvbi9hdG9tbWVkaWEiIHhtbG5zOnN0YXR1c25ldD0iaHR0cDovL3N0YXR1cy5uZXQvc2NoZW1hL2FwaS8xLyI-CiA8YWN0aXZpdHk6b2JqZWN0LXR5cGU-aHR0cDovL2FjdGl2aXR5c3RyZWEubXMvc2NoZW1hLzEuMC9ub3RlPC9hY3Rpdml0eTpvYmplY3QtdHlwZT4KIDxpZD5odHRwOi8vc24vbm90aWNlLzM8L2lkPgogPGNvbnRlbnQgdHlwZT0iaHRtbCI-aGVsbG8gQCZsdDtzcGFuIGNsYXNzPSZxdW90O3ZjYXJkJnF1b3Q7Jmd0OyZsdDthIGhyZWY9JnF1b3Q7aHR0cDovLzEyNy4wLjAuMi9iaWphbiZxdW90OyBjbGFzcz0mcXVvdDt1cmwmcXVvdDsmZ3Q7Jmx0O3NwYW4gY2xhc3M9JnF1b3Q7Zm4gbmlja25hbWUgbWVudGlvbiZxdW90OyZndDtiaWphbiZsdDsvc3BhbiZndDsmbHQ7L2EmZ3Q7Jmx0Oy9zcGFuJmd0OzwvY29udGVudD4KIDxsaW5rIHJlbD0iYWx0ZXJuYXRlIiB0eXBlPSJ0ZXh0L2h0bWwiIGhyZWY9Imh0dHA6Ly9zbi9ub3RpY2UvMyIvPgogPHN0YXR1c19uZXQgbm90aWNlX2lkPSIzIj48L3N0YXR1c19uZXQ-CiA8YWN0aXZpdHk6dmVyYj5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3Bvc3Q8L2FjdGl2aXR5OnZlcmI-CiA8cHVibGlzaGVkPjIwMTMtMDgtMTlUMDY6Mzk6MzYrMDA6MDA8L3B1Ymxpc2hlZD4KIDx1cGRhdGVkPjIwMTMtMDgtMTlUMDY6Mzk6MzYrMDA6MDA8L3VwZGF0ZWQ-CiA8YXV0aG9yPgogIDxhY3Rpdml0eTpvYmplY3QtdHlwZT5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3BlcnNvbjwvYWN0aXZpdHk6b2JqZWN0LXR5cGU-CiAgPHVyaT5odHRwOi8vc24vdXNlci8xPC91cmk-CiAgPG5hbWU-c248L25hbWU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovL3NuL3NuIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL3BuZyIgbWVkaWE6d2lkdGg9Ijk2IiBtZWRpYTpoZWlnaHQ9Ijk2IiBocmVmPSJodHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLXByb2ZpbGUucG5nIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL3BuZyIgbWVkaWE6d2lkdGg9IjQ4IiBtZWRpYTpoZWlnaHQ9IjQ4IiBocmVmPSJodHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLXN0cmVhbS5wbmciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvcG5nIiBtZWRpYTp3aWR0aD0iMjQiIG1lZGlhOmhlaWdodD0iMjQiIGhyZWY9Imh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItbWluaS5wbmciLz4KICA8cG9jbzpwcmVmZXJyZWRVc2VybmFtZT5zbjwvcG9jbzpwcmVmZXJyZWRVc2VybmFtZT4KICA8cG9jbzpkaXNwbGF5TmFtZT5zbjwvcG9jbzpkaXNwbGF5TmFtZT4KICA8Zm9sbG93ZXJzIHVybD0iaHR0cDovL3NuL3NuL3N1YnNjcmliZXJzIj48L2ZvbGxvd2Vycz4KICA8c3RhdHVzbmV0OnByb2ZpbGVfaW5mbyBsb2NhbF9pZD0iMSI-PC9zdGF0dXNuZXQ6cHJvZmlsZV9pbmZvPgogPC9hdXRob3I-CiA8bGluayByZWw9Im9zdGF0dXM6Y29udmVyc2F0aW9uIiBocmVmPSJodHRwOi8vc24vY29udmVyc2F0aW9uLzMiLz4KIDxsaW5rIHJlbD0ib3N0YXR1czphdHRlbnRpb24iIGhyZWY9Imh0dHA6Ly8xMjcuMC4wLjIvYmlqYW4iLz4KIDxsaW5rIHJlbD0ibWVudGlvbmVkIiBocmVmPSJodHRwOi8vMTI3LjAuMC4yL2JpamFuIi8-CiA8bGluayByZWw9Im9zdGF0dXM6YXR0ZW50aW9uIiBocmVmPSJodHRwOi8vYWN0aXZpdHlzY2hlbWEub3JnL2NvbGxlY3Rpb24vcHVibGljIi8-CiA8bGluayByZWw9Im1lbnRpb25lZCIgaHJlZj0iaHR0cDovL2FjdGl2aXR5c2NoZW1hLm9yZy9jb2xsZWN0aW9uL3B1YmxpYyIvPgogPGNhdGVnb3J5IHRlcm09IiI-PC9jYXRlZ29yeT4KIDxzb3VyY2U-CiAgPGlkPmh0dHA6Ly9zbi9hcGkvc3RhdHVzZXMvdXNlcl90aW1lbGluZS8xLmF0b208L2lkPgogIDx0aXRsZT5zbjwvdGl0bGU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovL3NuL3NuIi8-CiAgPGxpbmsgcmVsPSJzZWxmIiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNlcy91c2VyX3RpbWVsaW5lLzEuYXRvbSIvPgogIDxsaW5rIHJlbD0ibGljZW5zZSIgaHJlZj0iaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvbGljZW5zZXMvYnkvMy4wLyIvPgogIDxpY29uPmh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItcHJvZmlsZS5wbmc8L2ljb24-CiAgPHVwZGF0ZWQ-MjAxMy0wOC0xOVQwNjozOTozNiswMDowMDwvdXBkYXRlZD4KIDwvc291cmNlPgogPGxpbmsgcmVsPSJzZWxmIiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNlcy9zaG93LzMuYXRvbSIvPgogPGxpbmsgcmVsPSJlZGl0IiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNlcy9zaG93LzMuYXRvbSIvPgogPHN0YXR1c25ldDpub3RpY2VfaW5mbyBsb2NhbF9pZD0iMyIgc291cmNlPSJ3ZWIiPjwvc3RhdHVzbmV0Om5vdGljZV9pbmZvPgo8L2VudHJ5Pgo=</me:data><me:encoding>base64url</me:encoding><me:alg>RSA-SHA256</me:alg><me:sig>PJ4o4UN1hyGEzWWbfpIlO75axZW2YAhznpXuq_MJ83-eOYTDB2ZJWlGdW9Hg_lY_4ceYzMUkYZxR4PFD2M77XyMFjnDayzgjWDeTTOKAmA4S1OKLVPZFEGEghMjkMmpYWAasNCyImIO1dIqAaGSmC8xYQqQEnFYnvM8dp3E2Hyc=</me:sig></me:env>'
