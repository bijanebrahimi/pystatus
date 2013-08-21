# -*- coding: UTF-8 -*-
import re
import simplejson as json
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from convert import str_to_datetime, str_to_xml
from datetime import datetime

class ActivityStreamObject(object):
    # TODO: `title` and `summary` were skipped
    json = {}
    type = 'object'

    def get_type(self):
        if self.type in ['author', 'actor']:
            return 'actor'
        elif self.type == 'activity:object':
            return 'object'
        else:
            return 'target'
    def set_type(self, name):
        if name in ['author', 'actor']:
            self.type = 'actor'
        elif self.type == 'activity:object':
            self.type = 'object'
        else:
            self.type = 'target'

    def set_objectType(self, object_type):
        if not object_type.startswith('http'):
            object_type = 'http://activitystrea.ms/schema/1.0/%s' % object_type
        self.json['objectType'] = object_type
    def get_objectType(self):
        return self.json.get('objectType')
    def set_uri(self, uri):
        # in XMl <uri>
        self.json['uri'] = uri
    def get_uri(self):
        return self.json.get('uri')
    def set_id(self, id):
        # in XMl <uri>
        self.json['id'] = id
    def get_id(self):
        return self.json.get('id')
    def set_name(self, name):
        # in XMl <name>
        self.json['displayName'] = name
    def get_name(self):
        return self.json.get('displayName')
    def set_title(self, title):
        self.json['title'] = title
    def get_title(self):
        return self.json.get('title')
    def set_url(self, url):
        # in XMl <link rel='alternate'>
        self.json['url'] = url
    def get_url(self):
        return self.json.get('url')
    def add_avatar(self, url, type='image/png', width=None, height=None):
        if self.get_avatars() is None:
            self.json['avatarLinks'] = []
        # TODO: what is avatar's width was None
        self.json['avatarLinks'].append(dict(url=url,
                                             type=type,
                                             width=width,
                                             height=width))
    def get_avatars(self):
        return self.json.get('avatarLinks')
    def set_followers(self, url):
        # Only in XML representation
        self.json['followers'] = url
    def get_followers(self):
        return self.json.get('followers')
    def set_content(self, content):
        # Only in XML representation
        self.json['content'] = url
    def get_content(self):
        return self.json.get('content')

    # Extension: Portable Contacts
    def set_portableContact(self, preferredUsername=None, displayName=None, note=None, address=None, url=None):
        if self.get_portableContact() is None:
            self.json['contact'] = {}
        if preferredUsername:
            self.json['contact']['preferredUsername'] = preferredUsername
        if displayName:
            self.json['contact']['displayName'] = displayName
        if note:
            self.json['contact']['note'] = note
        if xml.name == 'poco:address':
            # TODO: region, postalCode, country is missing
            if self.json['contact'].get('addresses') is None and address:
                self.json['contact']['addresses'] = dict(formatted=address)
        if urls:
            if self.json['contact'].get('urls') is None:
                self.json['contact']['urls'] = []
            self.json['contact']['urls'].append(dict(type=url.get('type'),
                                                     value=url.get('value'),
                                                     primary=url.get('primary')))
    def add_portableContact(self, xml):
        # TODO: xml should be BeautifulSoup.*
        if self.get_portableContact() is None:
            self.json['contact'] = {}
        if xml.name == 'poco:preferredusername':
            self.json['contact']['preferredUsername'] = xml.text
        if xml.name == 'poco:displayname':
            self.json['contact']['displayName'] = xml.text
        if xml.name == 'poco:note':
            self.json['contact']['note'] = xml.text
        if xml.name == 'poco:address':
            # TODO: region, postalCode, country is missing
            if self.json['contact'].get('addresses') is None and xml.findChildren('poco:formatted'):
                self.json['contact']['addresses'] = dict(formatted=xml.findChildren('poco:formatted')[0].text)
        if xml.name == 'poco:urls':
            if self.json['contact'].get('urls') is None:
                self.json['contact']['urls'] = []
            self.json['contact']['urls'].append(dict(type=xml.findChildren('poco:type')[0].text,
                                                     value=xml.findChildren('poco:value')[0].text,
                                                     primary=xml.findChildren('poco:primary')[0].text))
    def get_portableContact(self):
        return self.json.get('contact')
    def set_statusnet(self, local_id=None, source=None):
        if self.get_statusnet() is None:
            self.json['statusnet:profile_info'] = {}
        if source:
            self.json['statusnet:profile_info']['source'] = source
        if local_id:
            self.json['statusnet:profile_info']['local_id'] = local_id
    def add_statusnet(self, xml):
        if self.get_statusnet() is None and xml.name == 'statusnet:profile_info':
            self.json['statusnet:profile_info'] = dict(local_id=xml.get('local_id'),
                                                       source=xml.get('source'))
    def get_statusnet(self):
        return self.json.get('statusnet:profile_info')
    
    def from_xml(self, xml):
        self.json = {}
        if isinstance(xml, unicode):
            xml = xml.encode('utf-8')
        if isinstance(xml, str):
            # xml = BeautifulSoup(xml)
            xml = str_to_xml(xml)
            if xml.name == '[document]':
                xml = xml.findChild()
        self.set_type(xml.name)
        el = xml.findChild()
        while el is not None:
            if el.name == 'activity:object-type':
                self.set_objectType(el.text)
            elif el.name == 'uri':
                self.set_uri(el.text)
            elif el.name == 'id':
                self.set_id(el.text)
            elif el.name == 'title':
                self.set_title(el.text)
            elif el.name == 'name':
                self.set_name(el.text)
            elif el.name == 'followers':
                self.set_followers(el.get('url'))
            elif el.name == 'link' and el.get('rel') == 'alternate':
                self.set_url(el.get('href'))
            elif el.name == 'link' and el.get('rel') == 'avatar':
                self.add_avatar(el.get('href'), el.get('type'), el.get('media:width'), el.get('media:height'))
            elif el.name.startswith('poco'):
                self.add_portableContact(el)
            elif el.name.startswith('statusnet'):
                self.add_statusnet(el)
            else:
                print 'Object leftovers ', el
            
            el = el.findNextSibling()
    def from_json(self, xml):
        pass
    
    def to_string(self):
        if self.get_type() == 'actor':
            string = '<author>'
        else:
            string = '<activity:%s>' % self.get_type()
            

        if self.get_objectType():
            string += '<activity:object-type>%s</activity:object-type>' % self.get_objectType()
        if self.get_uri():
            string += '<uri>%s</uri>' % self.get_uri()
        if self.get_id():
            string += '<id>%s</id>' % self.get_id()
        if self.get_name():
            string += '<name>%s</name>' % self.get_name()
        if self.get_title():
            string += '<title>%s</title>' % self.get_title()
        if self.get_content():
            string += '<content type="html">%s</content>' % self.get_content()
        if self.get_url():
            string += '<link rel="alternate" type="text/html" href="%s"/>' % self.get_url()
        if self.get_followers():
            string += '<followers url="%s" />' % self.get_followers()
        if self.get_avatars():
            for avatar in self.get_avatars():
                string += '<link rel="avatar" type="%s" href="%s" media:width="%s" media:height="%s"/>' % (avatar.get('type'), avatar.get('url'), avatar.get('width'), avatar.get('height'))
        if self.get_portableContact():
            contact = self.get_portableContact()
            if contact.get('preferredUsername'):
                string += '<poco:preferredUsername>%s</poco:preferredUsername>' % contact.get('preferredUsername')
            if contact.get('displayName'):
                string += '<poco:displayName>%s</poco:displayName>' % contact.get('displayName')
            if contact.get('note'):
                string += '<poco:note>%s</poco:note>' % contact.get('note')
            if contact.get('addresses'):
                string += '<poco:address><poco:formatted>%s</poco:formatted></poco:address>' % contact['addresses'].get('formatted')
            if(contact.get('urls')):
                for url in contact.get('urls'):
                    string += '<poco:urls><poco:type>%s</poco:type><poco:value>%s</poco:value><poco:primary>%s</poco:primary></poco:urls>' % (url.get('type'), url.get('value'), url.get('primary'))
        if self.get_statusnet():
            if self.get_statusnet().get('local_id'):
                string += '<statusnet:profile_info local_id="%s"></statusnet:profile_info>' % self.get_statusnet().get('local_id')

        if self.get_type() == 'actor':
            string += '</author>'
        else:
            string += '</activity:%s>' % self.get_type()
        return string
    def to_xml(self):
        return str_to_xml(self.to_string())
    def to_json(self):
        # TODO: escape strings like "image\/png"
        skip = ['followers']
        # FIXME: is it necessary
        if self.get_type() == 'actor':
            skip.append('id')
        else:
            skip.append('uri')
        json_result = dict( (key, value) for (key, value) in self.json.iteritems() if key not in [skip] )
        if json_result.get('avatarLinks'):
            json_result['image'] = json_result.get('avatarLinks')[0]
        return json.dumps(json_result)
    def to_list(self):
        return self.json

class ActivityStreamEntry(object):
    json = {}
    type = ''
    def get_type(self):
        return self.type
    def set_type(self, is_feed):
        if is_feed:
            self.type = 'feed'
        else:
            self.type = 'entry'

    # Objects
    def set_actor(self, actor):
        self.json['actor'] = None
        if isinstance(actor, unicode):
            actor = actor.encode('utf-8')
        if isinstance(actor, str):
            actor = str_to_xml(actor)
        if isinstance(actor, ActivityStreamObject):
            self.json['actor'] = actor
        else:
            # it's gotta be BeautifulSoup
            tmp = ActivityStreamObject()
            if actor.name == '[document]':
                actor = actor.findChild()
            tmp.from_xml(actor)
            tmp.set_type('actor')
            self.json['actor'] = tmp
    def get_actor(self):
        return self.json.get('actor')
    def set_object(self, obj):
        self.json['object'] = None
        if isinstance(obj, unicode):
            obj = obj.encode('utf-8')
        if isinstance(obj, str):
            obj = str_to_xml(obj)
        if isinstance(obj, ActivityStreamObject):
            self.json['object'] = obj
        else:
            # it's gotta be BeautifulSoup
            tmp = ActivityStreamObject()
            if obj.name == '[document]':
                obj = obj.findChild()
            tmp.from_xml(obj)
            tmp.set_type('object')
            self.json['object'] = tmp
    def get_object(self):
        return self.json.get('object')
    # FIXME: this should be an array (in JSON)?
    def set_target(self, target):
        self.json['to'] = None
        if isinstance(target, unicode):
            target = target.encode('utf-8')
        if isinstance(target, str):
            target = str_to_xml(target)
        if isinstance(target, ActivityStreamObject):
            self.json['to'] = target
        else:
            # it's gotta be BeautifulSoup
            tmp = ActivityStreamObject()
            if target.name == '[document]':
                target = target.findChild()
            tmp.from_xml(target)
            tmp.set_type('target')
            self.json['to'] = tmp
    def get_target(self):
        return self.json.get('to')

    # Properties
    def set_id(self, id):
        self.json['id'] = id
    def get_id(self):
        return self.json.get('id')
    def set_url(self, url):
        # in XMl <link rel='alternate'>
        self.json['url'] = url
    def get_url(self):
        return self.json.get('url')
    def get_self(self):
        # Only in XML (Feed) representation
        return self.json.get('self')
    def set_self(self, self_url, type=''):
        self.json['self'] = dict(href=self_url, type=type)
    def set_verb(self, verb):
        if not verb.startswith('http'):
            verb = 'http://activitystrea.ms/schema/1.0/%s' % verb
        self.json['verb'] = verb
    def get_verb(self):
        return self.json.get('verb')
    def set_published(self, published):
        if isinstance(published, datetime):
            published = datetime_to_rfc3339(published)
        self.json['published'] = published
    def get_published(self):
        return self.json.get('published')
    def set_title(self, title):
        self.json['title'] = title
    def get_title(self):
        return self.json.get('title')
    def set_content(self, content):
        self.json['content'] = content
    def get_content(self):
        return self.json.get('content')
    # FIXME: hot wo show category in JSON representation
    def add_category(self, category):
        # TODO: check for empty category
        if self.get_categories() is None:
            self.json['category'] = []
        self.json['category'].append(category)
    def get_categories(self):
        return self.json.get('category')
    def set_objectType(self, object_type):
        if not object_type.startswith('http'):
            object_type = 'http://activitystrea.ms/schema/1.0/%s' % object_type
        self.json['objectType'] = object_type
    def get_objectType(self):
        return self.json.get('objectType')
    
    # Extensions
    def set_ostatus(self, conversation=None, attentions=None, mentioneds=None):
        if self.json.get('context') is None:
            self.json['context'] = {}
        if conversation:
            self.json['context']['conversation'] = conversation
        if attentions:
            if self.json['context'].get('attention') is None:
                self.json['context']['attention'] = []
            for attention in attentions:
                self.json['context']['attention'].append(attention)
        if mentioneds:
            if self.json['context'].get('mentioned') is None:
                self.json['context']['mentioned'] = []
            for mentioned in mentioneds:
                self.json['context']['mentioned'].append(mentioned)
    def add_ostatus(self, xml):
        # FIXME: how to represent attention/mentioned in JSON representation
        if self.json.get('context') is None:
            self.json['context'] = {}
        if xml.get('rel') == 'ostatus:conversation':
            self.json['context']['conversation'] = xml.get('href')
        elif xml.get('rel') == 'ostatus:attention':
            if self.json['context'].get('attention') is None:
                self.json['context']['attention'] = []
            self.json['context']['attention'].append(xml.get('href'))
        elif xml.get('rel') == 'mentioned':
            if self.json['context'].get('mentioned') is None:
                self.json['context']['mentioned'] = []
            self.json['context']['mentioned'].append(xml.get('href'))
    def get_ostatus(self):
        return self.json.get('context')
    def set_statusnet(self, local_id=None, source=None):
        if self.get_statusnet() is None:
            self.json['statusnet:profile_info'] = {}
        if source:
            self.json['statusnet:profile_info']['source'] = source
        if local_id:
            self.json['statusnet:profile_info']['local_id'] = local_id
    def add_statusnet(self, xml):
        if self.get_statusnet() is None and xml.name == 'statusnet:profile_info':
            self.json['statusnet:profile_info'] = dict(local_id=xml.get('local_id'),
                                                       source=xml.get('source'))
    def get_statusnet(self):
        return self.json.get('statusnet:profile_info')
    def set_thr(self, id, url):
        if self.json.get('context') is None:
            self.json['context'] = {}
        self.json['context']['inReplyTo'] = dict(id=id,
                                                 url=url)
    def add_thr(self, xml):
        if self.json.get('context') is None:
            self.json['context'] = {}
        self.json['context']['inReplyTo'] = dict(id=xml.get('href'),
                                                 url=xml.get('ref'))
    def get_thr(self):
        if self.json.get('context'):
            return self.json['context'].get('inReplyTo')
    # Entry generator
    def from_xml(self, xml):
        self.json = {}
        if isinstance(xml, unicode):
            xml = xml.encode('utf-8')
        if isinstance(xml, str):
            xml = str_to_xml(xml)
            if xml.name == '[document]':
                xml = xml.findChild()
        self.set_type(xml.name=='entry')
        # for el in xml.findAll():
        el = xml.findChild()
        while el is not None:
            if el.name == 'author':
                self.set_actor(el)
            elif el.name == 'activity:object':
                self.set_object(el)
            elif el.name == 'activity:target':
                self.set_target(el)
            if el.name == 'activity:object-type':
                self.set_objectType(el.text)
            elif el.name == 'id':
                self.set_id(el.text)
            elif el.name == 'activity:verb':
                self.set_verb(el.text)
            elif el.name == 'published':
                self.set_published(el.text)
            elif el.name == 'title':
                self.set_title(el.text)
            elif el.name == 'content':
                self.set_content(el.text)
            elif el.name == 'category':
                self.add_category(el.get('term'))
            elif el.name == 'link' and el.get('rel') == 'alternate':
                self.set_url(el.get('href'))
            elif el.name == 'link' and el.get('rel') == 'self':
                self.set_self(el.get('href'))
            elif el.get('rel') and (el.get('rel').startswith('ostatus') or el.get('rel').startswith('mentioned')):
                self.add_ostatus(el)
            elif el.name.startswith('statusnet:notice_info'):
                self.add_statusnet(el)
            elif el.name.startswith('thr:in-reply-to'):
                self.add_thr(el)
            else:
                print 'Entry leftover ', el
            
            el = el.findNextSibling()
    def from_json(self, json):
        pass

    # Entry Representations
    def to_string(self):
        if self.get_type() == 'feed':
            string = '<?xml version="1.0" encoding="UTF-8"?><entry xmlns="http://www.w3.org/2005/Atom" xmlns:activity="http://activitystrea.ms/spec/1.0/">'
        else:
            string = '<entry>'
        
        # Objects
        if self.get_actor():
            string += self.get_actor().to_string()
        if self.get_object():
            string += self.get_object().to_string()
        if self.get_target():
            string += self.get_target().to_string()
        
        # Properties
        if self.get_objectType():
            string += '<activity:object-type>%s</activity:object-type>' % self.get_objectType()
        if self.get_id():
            string += '<id>%s</id>' % self.get_id()
        if self.get_url():
            string += '<link rel="alternate" type="text/html" href="%s"/>' % self.get_url()
        if self.get_self():
            string += '<link rel="self" type="%s" href="%s"/>' % (self.get_self()['type'], self.get_self()['href'])
        if self.get_verb():
            string += '<activity:verb>%s</activity:verb>' % self.get_verb()
        if self.get_published():
            string += '<published>%s</published>' % self.get_published()
        if self.get_title():
            string += '<title>%s</title>' % self.get_title()
        if self.get_content():
            string += '<content type="html">%s</content>' % self.get_content()
        if self.get_categories():
            for category in self.get_categories():
                string += '<category term="%s"></category>' % category
        
        # Extensions
        if self.get_statusnet():
            string += '<statusnet:notice_info local_id="%s" source="%s" />' % (self.get_statusnet().get('local_id'),
                                                                               self.get_statusnet().get('source'))
        if self.get_ostatus():
            if self.get_ostatus().get('conversation'):
                string += '<link rel="ostatus:conversation" href="%s" />' % self.get_ostatus().get('conversation')
            if self.get_ostatus().get('attention'):
                for attention in self.get_ostatus().get('attention'):
                    string += '<link rel="ostatus:attention" href="%s" />' % attention
            if self.get_ostatus().get('mentioned'):
                for mentioned in self.get_ostatus().get('mentioned'):
                    string += '<link rel="mentioned" href="%s" />' % mentioned
        if self.get_thr():
            string += '<thr:in-reply-to ref="%s" href="%s" />' % (self.get_thr()['id'], self.get_thr()['url'])
        string += '</entry>'
        return string
    def to_xml(self):
        return str_to_xml(self.to_string())
    def to_json(self):
        pass
    def to_list(self):
        return  self.json

class ActivityStreamFeed(object):
    json = {}
    def get_namespaces(self, name=None):
        if name is None:
            return self.json.get('ns')
        elif name is not None and self.json.get('ns') is None:
            self.json['ns'].get(name)
    def append_namespaces(self, value, name='xml'):
        if value is None:
            return None
        if self.get_namespaces() is None:
            self.json['ns'] = {}
        # TODO: check for fuplidated namespaces
        self.json['ns'][name]=value
    # Properties
    def set_generator(self, generator):
        self.json['generator'] = generator
    def get_generator(self):
        return self.json.get('generator')
    def set_title(self, title):
        self.json['title'] = title
    def get_title(self):
        return self.json.get('title')
    # Feed id getter/setter (ONLY FOR XML REPRESENTATION)
    def set_id(self, id):
        self.json['id'] = id
    def get_id(self):
        return self.json.get('id')
    # Feed updated/published getter/setter (ONLY FOR XML REPRESENTATION)
    def set_published(self, published):
        if isinstance(published, datetime):
            published = datetime_to_rfc3339(published)
        self.json['published'] = published
    def get_published(self):
        return self.json.get('published')
    def set_updated(self, updated):
        if isinstance(updated, datetime):
            updated = datetime_to_rfc3339(updated)
        self.json['updated'] = updated
    def get_updated(self):
        return self.json.get('updated')

    # Feed Links (ONLY FOR XML REPRESENTATION)
    def get_alternate(self):
        return self.json.get('url')
    def set_alternate(self, alternate, type=''):
        self.json['url'] = dict(href=alternate, type=type)
    def get_self(self):
        return self.json.get('self')
    def set_self(self, self_url, type=''):
        self.json['self'] = dict(href=self_url, type=type)
    def get_subscription(self):
        return self.json.get('subscription')
    def set_subscription(self, subscription, type=''):
        self.json['subscription'] = dict(href=subscription, type=type)
    def get_hub(self):
        return self.json.get('hub')
    def set_hub(self, hub):
        self.json['hub'] = hub
    def get_salmon(self):
        return self.json.get('salmon')
    def set_salmon(self, salmon=None, mention=None, reply=None):
        if not (salmon or mention or reply):
            return None
        if self.get_salmon() is None:
            self.json['salmon'] = []
        if salmon:
            self.json['salmon'].append(dict(href=salmon,rel='salmon'))
        if mention:
            self.json['salmon'].append(dict(href=mention, rel='http://salmon-protocol.org/ns/salmon-mention'))
        if reply:
            self.json['salmon'].append(dict(href=reply, rel='http://salmon-protocol.org/ns/salmon-replies'))
    
    # Object [ONLY in XML]
    # Objects
    def set_actor(self, actor):
        self.json['actor'] = None
        if isinstance(actor, unicode):
            actor = actor.encode('utf-8')
        if isinstance(actor, str):
            actor = str_to_xml(actor)
        if isinstance(actor, ActivityStreamObject):
            self.json['actor'] = actor
        else:
            # it's gotta be BeautifulSoup
            tmp = ActivityStreamObject()
            if actor.name == '[document]':
                actor = actor.findChild()
            tmp.from_xml(actor)
            tmp.set_type('actor')
            self.json['actor'] = tmp
    def get_actor(self):
        return self.json.get('actor')
    def set_object(self, obj):
        self.json['object'] = None
        if isinstance(obj, unicode):
            obj = obj.encode('utf-8')
        if isinstance(obj, str):
            obj = str_to_xml(obj)
        if isinstance(obj, ActivityStreamObject):
            self.json['object'] = obj
        else:
            # it's gotta be BeautifulSoup
            tmp = ActivityStreamObject()
            if obj.name == '[document]':
                obj = obj.findChild()
            tmp.from_xml(obj)
            tmp.set_type('object')
            self.json['object'] = tmp
    def get_object(self):
        return self.json.get('object')
    # FIXME: this should be an array (in JSON)?
    def set_target(self, target):
        self.json['to'] = None
        if isinstance(target, unicode):
            target = target.encode('utf-8')
        if isinstance(target, str):
            target = str_to_xml(target)
        if isinstance(target, ActivityStreamObject):
            self.json['to'] = target
        else:
            # it's gotta be BeautifulSoup
            tmp = ActivityStreamObject()
            if target.name == '[document]':
                target = target.findChild()
            tmp.from_xml(target)
            tmp.set_type('target')
            self.json['to'] = tmp
    def get_target(self):
        return self.json.get('to')
    def add_entry(self, entry):
        if self.get_entry() is None:
            self.json['items'] = []
        tmp = ActivityStreamEntry()
        tmp.from_xml(entry)
        tmp.set_type(False)
        self.json['items'].append(tmp)
    def get_entry(self):
        return self.json.get('items')
    
    # convert
    def from_xml(self, xml):
        self.json = {}

        if isinstance(xml, unicode):
            xml = xml.encode('utf-8')
        if isinstance(xml, str):
            xml = str_to_xml(xml)
        if xml.name == '[document]':
            xml = xml.findChild()
        el = xml.findChild()
        while el is not None:
            if el.name == 'generator':
                self.set_generator(el.text)
            elif el.name == 'title':
                self.set_id(el.text)
            elif el.name == 'id':
                self.set_id(el.text)
            elif el.name == 'published':
                self.set_published(el.text)
            elif el.name == 'updated':
                self.set_updated(el.text)
            elif el.name == 'link' and el.get('rel') == 'alternate':
                self.set_alternate(el.get('href'), el.get('type'))
            elif el.name == 'link' and el.get('rel') == 'self':
                self.set_self(el.get('href'), el.get('type'))
            elif el.name == 'link' and el.get('rel') == 'http://api.friendfeed.com/2008/03#sup':
                self.set_subscription(el.get('href'), el.get('type'))
            elif el.name == 'link' and el.get('rel') == 'hub':
                self.set_hub(el.get('href'))
            elif el.name == 'link' and el.get('rel') == 'salmon':
                self.set_salmon(salmon=el.get('href'))
            elif el.name == 'link' and el.get('rel') == 'http://salmon-protocol.org/ns/salmon-replies':
                self.set_salmon(reply=el.get('href'))
            elif el.name == 'link' and el.get('rel') == 'http://salmon-protocol.org/ns/salmon-mention':
                self.set_salmon(mention=el.get('href'))
            elif el.name == 'entry':
                self.add_entry(el)
            elif el.name == 'author':
                self.set_actor(el)
            elif el.name == 'activity:object':
                self.set_object(el)
            elif el.name == 'activity:target':
                self.set_target(el)
            else:
                print 'Feed leftover ', el
            el = el.findNextSibling()
    def from_json(self, json):
        pass

    # Feed Representations
    def to_string(self):
        string = '<?xml version="1.0" encoding="UTF-8"?>'
        # TODO: generate XML namespaces
        string += '<feed xml:lang="en-US" xmlns="http://www.w3.org/2005/Atom" xmlns:activity="http://activitystrea.ms/spec/1.0/">'
        # Headers
        if self.get_generator():
            string += '<generator uri="" version="">%s</generator>' % self.get_generator()
        if self.get_title():
            string += '<title>%s</title>' % self.get_title()
        if self.get_id():
            string += '<id>%s</id>' % self.get_id()
        if self.get_published():
            string += '<published>%s</published>' % self.get_published()
        if self.get_updated():
            string += '<updated>%s</updated>' % self.get_updated()
        if self.get_title():
            string += '<title>%s</title>' % self.get_title()
        
        # Links
        if self.get_alternate():
            string += '<link rel="alternate" type="%s" href="%s"/>' % (self.get_alternate()['type'], self.get_alternate()['href'])
        if self.get_self():
            string += '<link rel="self" type="%s" href="%s"/>' % (self.get_self()['type'], self.get_self()['href'])
        if self.get_subscription():
            string += '<link rel="http://api.friendfeed.com/2008/03#sup" type="%s" href="%s"/>' % (self.get_subscription()['type'], self.get_subscription()['href'])
        if self.get_hub():
            string += '<link rel="hub" href="%s"/>' % self.get_hub()
        for salmon in self.get_salmon():
            string += '<link rel="%s" href="%s"/>' % (salmon['rel'], salmon['href'])
        
        # Objects
        if self.get_actor():
            string += self.get_actor().to_string()
        if self.get_object():
            string += self.get_object().to_string()
        if self.get_target():
            string += self.get_target().to_string()
        if self.get_entry():
            for entry in self.get_entry():
                string += entry.to_string()
        string += '</feed>'
        return string
    def to_xml(self):
        return str_to_xml(self.to_string())
    def to_json(self):
        json_result = dict( (key, value) for (key, value) in self.json.iteritems() if key not in ['ns, id', 'published', 'updated', 'alternate', 'self', 'subscription', 'salmon', 'hub'] )
        # TODO: include totalItems
        return json.dumps(json_result)
    def to_list(self):
        return self.json

salmon = '<?xml version="1.0" encoding="UTF-8"?><me:env xmlns:me="http://salmon-protocol.org/ns/magic-env"><me:data type="application/atom+xml">PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiID8-PGVudHJ5IHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDA1L0F0b20iIHhtbG5zOnRocj0iaHR0cDovL3B1cmwub3JnL3N5bmRpY2F0aW9uL3RocmVhZC8xLjAiIHhtbG5zOmFjdGl2aXR5PSJodHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zcGVjLzEuMC8iIHhtbG5zOmdlb3Jzcz0iaHR0cDovL3d3dy5nZW9yc3Mub3JnL2dlb3JzcyIgeG1sbnM6b3N0YXR1cz0iaHR0cDovL29zdGF0dXMub3JnL3NjaGVtYS8xLjAiIHhtbG5zOnBvY289Imh0dHA6Ly9wb3J0YWJsZWNvbnRhY3RzLm5ldC9zcGVjLzEuMCIgeG1sbnM6bWVkaWE9Imh0dHA6Ly9wdXJsLm9yZy9zeW5kaWNhdGlvbi9hdG9tbWVkaWEiIHhtbG5zOnN0YXR1c25ldD0iaHR0cDovL3N0YXR1cy5uZXQvc2NoZW1hL2FwaS8xLyI-CiA8YWN0aXZpdHk6b2JqZWN0LXR5cGU-aHR0cDovL2FjdGl2aXR5c3RyZWEubXMvc2NoZW1hLzEuMC9ub3RlPC9hY3Rpdml0eTpvYmplY3QtdHlwZT4KIDxpZD5odHRwOi8vc24vbm90aWNlLzE1PC9pZD4KIDxjb250ZW50IHR5cGU9Imh0bWwiPmhpIEAmbHQ7c3BhbiBjbGFzcz0mcXVvdDt2Y2FyZCZxdW90OyZndDsmbHQ7YSBocmVmPSZxdW90O2h0dHA6Ly8xMjcuMC4wLjIvYmlqYW4mcXVvdDsgY2xhc3M9JnF1b3Q7dXJsJnF1b3Q7Jmd0OyZsdDtzcGFuIGNsYXNzPSZxdW90O2ZuIG5pY2tuYW1lIG1lbnRpb24mcXVvdDsmZ3Q7YmlqYW4mbHQ7L3NwYW4mZ3Q7Jmx0Oy9hJmd0OyZsdDsvc3BhbiZndDs8L2NvbnRlbnQ-CiA8bGluayByZWw9ImFsdGVybmF0ZSIgdHlwZT0idGV4dC9odG1sIiBocmVmPSJodHRwOi8vc24vbm90aWNlLzE1Ii8-CiA8c3RhdHVzX25ldCBub3RpY2VfaWQ9IjE1Ij48L3N0YXR1c19uZXQ-CiA8YWN0aXZpdHk6dmVyYj5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3Bvc3Q8L2FjdGl2aXR5OnZlcmI-CiA8cHVibGlzaGVkPjIwMTMtMDgtMTdUMTE6NDg6MDgrMDA6MDA8L3B1Ymxpc2hlZD4KIDx1cGRhdGVkPjIwMTMtMDgtMTdUMTE6NDg6MDgrMDA6MDA8L3VwZGF0ZWQ-CiA8YXV0aG9yPgogIDxhY3Rpdml0eTpvYmplY3QtdHlwZT5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3BlcnNvbjwvYWN0aXZpdHk6b2JqZWN0LXR5cGU-CiAgPHVyaT5odHRwOi8vc24vdXNlci8xPC91cmk-CiAgPG5hbWU-c248L25hbWU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovL3NuL3NuIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL3BuZyIgbWVkaWE6d2lkdGg9Ijk2IiBtZWRpYTpoZWlnaHQ9Ijk2IiBocmVmPSJodHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLXByb2ZpbGUucG5nIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL3BuZyIgbWVkaWE6d2lkdGg9IjQ4IiBtZWRpYTpoZWlnaHQ9IjQ4IiBocmVmPSJodHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLXN0cmVhbS5wbmciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvcG5nIiBtZWRpYTp3aWR0aD0iMjQiIG1lZGlhOmhlaWdodD0iMjQiIGhyZWY9Imh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItbWluaS5wbmciLz4KICA8cG9jbzpwcmVmZXJyZWRVc2VybmFtZT5zbjwvcG9jbzpwcmVmZXJyZWRVc2VybmFtZT4KICA8cG9jbzpkaXNwbGF5TmFtZT5iaWphbjwvcG9jbzpkaXNwbGF5TmFtZT4KICA8Zm9sbG93ZXJzIHVybD0iaHR0cDovL3NuL3NuL3N1YnNjcmliZXJzIj48L2ZvbGxvd2Vycz4KICA8c3RhdHVzbmV0OnByb2ZpbGVfaW5mbyBsb2NhbF9pZD0iMSI-PC9zdGF0dXNuZXQ6cHJvZmlsZV9pbmZvPgogPC9hdXRob3I-CiA8bGluayByZWw9Im9zdGF0dXM6Y29udmVyc2F0aW9uIiBocmVmPSJodHRwOi8vc24vY29udmVyc2F0aW9uLzE1Ii8-CiA8bGluayByZWw9Im9zdGF0dXM6YXR0ZW50aW9uIiBocmVmPSJodHRwOi8vMTI3LjAuMC4yL2JpamFuIi8-CiA8bGluayByZWw9Im1lbnRpb25lZCIgaHJlZj0iaHR0cDovLzEyNy4wLjAuMi9iaWphbiIvPgogPGxpbmsgcmVsPSJvc3RhdHVzOmF0dGVudGlvbiIgaHJlZj0iaHR0cDovL2FjdGl2aXR5c2NoZW1hLm9yZy9jb2xsZWN0aW9uL3B1YmxpYyIvPgogPGxpbmsgcmVsPSJtZW50aW9uZWQiIGhyZWY9Imh0dHA6Ly9hY3Rpdml0eXNjaGVtYS5vcmcvY29sbGVjdGlvbi9wdWJsaWMiLz4KIDxjYXRlZ29yeSB0ZXJtPSIiPjwvY2F0ZWdvcnk-CiA8c291cmNlPgogIDxpZD5odHRwOi8vc24vYXBpL3N0YXR1c2VzL3VzZXJfdGltZWxpbmUvMS5hdG9tPC9pZD4KICA8dGl0bGU-YmlqYW48L3RpdGxlPgogIDxsaW5rIHJlbD0iYWx0ZXJuYXRlIiB0eXBlPSJ0ZXh0L2h0bWwiIGhyZWY9Imh0dHA6Ly9zbi9zbiIvPgogIDxsaW5rIHJlbD0ic2VsZiIgdHlwZT0iYXBwbGljYXRpb24vYXRvbSt4bWwiIGhyZWY9Imh0dHA6Ly9zbi9hcGkvc3RhdHVzZXMvdXNlcl90aW1lbGluZS8xLmF0b20iLz4KICA8bGluayByZWw9ImxpY2Vuc2UiIGhyZWY9Imh0dHA6Ly9jcmVhdGl2ZWNvbW1vbnMub3JnL2xpY2Vuc2VzL2J5LzMuMC8iLz4KICA8aWNvbj5odHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLXByb2ZpbGUucG5nPC9pY29uPgogIDx1cGRhdGVkPjIwMTMtMDgtMTdUMTE6NDg6MDgrMDA6MDA8L3VwZGF0ZWQ-CiA8L3NvdXJjZT4KIDxsaW5rIHJlbD0ic2VsZiIgdHlwZT0iYXBwbGljYXRpb24vYXRvbSt4bWwiIGhyZWY9Imh0dHA6Ly9zbi9hcGkvc3RhdHVzZXMvc2hvdy8xNS5hdG9tIi8-CiA8bGluayByZWw9ImVkaXQiIHR5cGU9ImFwcGxpY2F0aW9uL2F0b20reG1sIiBocmVmPSJodHRwOi8vc24vYXBpL3N0YXR1c2VzL3Nob3cvMTUuYXRvbSIvPgogPHN0YXR1c25ldDpub3RpY2VfaW5mbyBsb2NhbF9pZD0iMTUiIHNvdXJjZT0id2ViIj48L3N0YXR1c25ldDpub3RpY2VfaW5mbz4KPC9lbnRyeT4K</me:data><me:encoding>base64url</me:encoding><me:alg>RSA-SHA256</me:alg><me:sig>AynbA2UncLlsnggO53swWisIko_533RQ107uTteK-tX_eKf9x2Gz3zvQu4U-MO7EoozpJ1JzRGXnc0mbxK2LzzfOoYziovpissGkaCfuPp85jL8LFk9pzv3Qwn4ZqvYBAtE9MqZtwLjx-eFUxoPyEWfoZGihmTTXbNCubEvp8JM=</me:sig></me:env>'
salmon1='<?xml version="1.0" encoding="UTF-8"?><me:env xmlns:me="http://salmon-protocol.org/ns/magic-env"><me:data type="application/atom+xml">PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiID8-PGVudHJ5IHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDA1L0F0b20iIHhtbG5zOnRocj0iaHR0cDovL3B1cmwub3JnL3N5bmRpY2F0aW9uL3RocmVhZC8xLjAiIHhtbG5zOmFjdGl2aXR5PSJodHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zcGVjLzEuMC8iIHhtbG5zOmdlb3Jzcz0iaHR0cDovL3d3dy5nZW9yc3Mub3JnL2dlb3JzcyIgeG1sbnM6b3N0YXR1cz0iaHR0cDovL29zdGF0dXMub3JnL3NjaGVtYS8xLjAiIHhtbG5zOnBvY289Imh0dHA6Ly9wb3J0YWJsZWNvbnRhY3RzLm5ldC9zcGVjLzEuMCIgeG1sbnM6bWVkaWE9Imh0dHA6Ly9wdXJsLm9yZy9zeW5kaWNhdGlvbi9hdG9tbWVkaWEiIHhtbG5zOnN0YXR1c25ldD0iaHR0cDovL3N0YXR1cy5uZXQvc2NoZW1hL2FwaS8xLyI-CiA8aWQ-dGFnOnNuLDIwMTMtMDgtMTg6cG9zdDoxPC9pZD4KIDx0aXRsZT48L3RpdGxlPgogPGNvbnRlbnQgdHlwZT0iaHRtbCI-Jmx0O2EgaHJlZj0mcXVvdDtodHRwOi8vc24vc24mcXVvdDsmZ3Q7c24mbHQ7L2EmZ3Q7IHN0YXJ0ZWQgZm9sbG93aW5nICZsdDthIGhyZWY9JnF1b3Q7aHR0cDovLzEyNy4wLjAuMi9iaWphbiZxdW90OyZndDtiaWphbiZsdDsvYSZndDsuPC9jb250ZW50PgogPGFjdGl2aXR5OnZlcmI-aHR0cDovL2FjdGl2aXR5c3RyZWEubXMvc2NoZW1hLzEuMC9mb2xsb3c8L2FjdGl2aXR5OnZlcmI-CiA8cHVibGlzaGVkPjIwMTMtMDgtMThUMDg6NTc6MzkrMDA6MDA8L3B1Ymxpc2hlZD4KIDx1cGRhdGVkPjIwMTMtMDgtMThUMDg6NTc6MzkrMDA6MDA8L3VwZGF0ZWQ-CiA8YXV0aG9yPgogIDxhY3Rpdml0eTpvYmplY3QtdHlwZT5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3BlcnNvbjwvYWN0aXZpdHk6b2JqZWN0LXR5cGU-CiAgPHVyaT5odHRwOi8vc24vdXNlci8xPC91cmk-CiAgPG5hbWU-c248L25hbWU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovL3NuL3NuIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL3BuZyIgbWVkaWE6d2lkdGg9Ijk2IiBtZWRpYTpoZWlnaHQ9Ijk2IiBocmVmPSJodHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLXByb2ZpbGUucG5nIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL3BuZyIgbWVkaWE6d2lkdGg9IjQ4IiBtZWRpYTpoZWlnaHQ9IjQ4IiBocmVmPSJodHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLXN0cmVhbS5wbmciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvcG5nIiBtZWRpYTp3aWR0aD0iMjQiIG1lZGlhOmhlaWdodD0iMjQiIGhyZWY9Imh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItbWluaS5wbmciLz4KICA8cG9jbzpwcmVmZXJyZWRVc2VybmFtZT5zbjwvcG9jbzpwcmVmZXJyZWRVc2VybmFtZT4KICA8cG9jbzpkaXNwbGF5TmFtZT5zbjwvcG9jbzpkaXNwbGF5TmFtZT4KICA8Zm9sbG93ZXJzIHVybD0iaHR0cDovL3NuL3NuL3N1YnNjcmliZXJzIj48L2ZvbGxvd2Vycz4KICA8c3RhdHVzbmV0OnByb2ZpbGVfaW5mbyBsb2NhbF9pZD0iMSI-PC9zdGF0dXNuZXQ6cHJvZmlsZV9pbmZvPgogPC9hdXRob3I-CiA8YWN0aXZpdHk6b2JqZWN0PgogIDxhY3Rpdml0eTpvYmplY3QtdHlwZT5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3BlcnNvbjwvYWN0aXZpdHk6b2JqZWN0LXR5cGU-CiAgPGlkPmh0dHA6Ly8xMjcuMC4wLjIvYmlqYW48L2lkPgogIDx0aXRsZT5iaWphbjwvdGl0bGU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovLzEyNy4wLjAuMi9iaWphbiIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9qcGVnIiBtZWRpYTp3aWR0aD0iOTYiIG1lZGlhOmhlaWdodD0iOTYiIGhyZWY9Imh0dHA6Ly9zbi9hdmF0YXIvMi1vcmlnaW5hbC0yMDEzMDgxODA4NTYxMy5qcGVnIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL2pwZWciIG1lZGlhOndpZHRoPSI5NiIgbWVkaWE6aGVpZ2h0PSI5NiIgaHJlZj0iaHR0cDovL3NuL2F2YXRhci8yLW9yaWdpbmFsLTIwMTMwODE4MDg1NjEzLmpwZWciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvanBlZyIgbWVkaWE6d2lkdGg9IjQ4IiBtZWRpYTpoZWlnaHQ9IjQ4IiBocmVmPSJodHRwOi8vc24vYXZhdGFyLzItNDgtMjAxMzA4MTgwODU2MTQuanBlZyIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9qcGVnIiBtZWRpYTp3aWR0aD0iMjQiIG1lZGlhOmhlaWdodD0iMjQiIGhyZWY9Imh0dHA6Ly9zbi9hdmF0YXIvMi0yNC0yMDEzMDgxODA4NTYxNC5qcGVnIi8-CiAgPHBvY286cHJlZmVycmVkVXNlcm5hbWU-YmlqYW48L3BvY286cHJlZmVycmVkVXNlcm5hbWU-CiAgPHBvY286ZGlzcGxheU5hbWU-YmlqYW48L3BvY286ZGlzcGxheU5hbWU-CiAgPHBvY286bm90ZT5ubyBkZXNjcmlwdGlvbiBpcyBwcm92aWRlZDwvcG9jbzpub3RlPgogIDxwb2NvOmFkZHJlc3M-CiAgIDxwb2NvOmZvcm1hdHRlZD5ubyBsb2NhdGlvbiBpcyBwcm92aWRlZDwvcG9jbzpmb3JtYXR0ZWQ-CiAgPC9wb2NvOmFkZHJlc3M-CiAgPHBvY286dXJscz4KICAgPHBvY286dHlwZT5ob21lcGFnZTwvcG9jbzp0eXBlPgogICA8cG9jbzp2YWx1ZT5odHRwOi8vZXhhbXBsZS5jb208L3BvY286dmFsdWU-CiAgIDxwb2NvOnByaW1hcnk-dHJ1ZTwvcG9jbzpwcmltYXJ5PgogIDwvcG9jbzp1cmxzPgogPC9hY3Rpdml0eTpvYmplY3Q-CiA8bGluayByZWw9Im9zdGF0dXM6Y29udmVyc2F0aW9uIiBocmVmPSJodHRwOi8vc24vY29udmVyc2F0aW9uLzEiLz4KIDxsaW5rIHJlbD0ib3N0YXR1czphdHRlbnRpb24iIGhyZWY9Imh0dHA6Ly8xMjcuMC4wLjIvYmlqYW4iLz4KIDxsaW5rIHJlbD0ibWVudGlvbmVkIiBocmVmPSJodHRwOi8vMTI3LjAuMC4yL2JpamFuIi8-CiA8bGluayByZWw9Im9zdGF0dXM6YXR0ZW50aW9uIiBocmVmPSJodHRwOi8vYWN0aXZpdHlzY2hlbWEub3JnL2NvbGxlY3Rpb24vcHVibGljIi8-CiA8bGluayByZWw9Im1lbnRpb25lZCIgaHJlZj0iaHR0cDovL2FjdGl2aXR5c2NoZW1hLm9yZy9jb2xsZWN0aW9uL3B1YmxpYyIvPgogPGNhdGVnb3J5IHRlcm09IiI-PC9jYXRlZ29yeT4KIDxzb3VyY2U-CiAgPGlkPmh0dHA6Ly9zbi9hcGkvc3RhdHVzZXMvdXNlcl90aW1lbGluZS8xLmF0b208L2lkPgogIDx0aXRsZT5zbjwvdGl0bGU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovL3NuL3NuIi8-CiAgPGxpbmsgcmVsPSJzZWxmIiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNlcy91c2VyX3RpbWVsaW5lLzEuYXRvbSIvPgogIDxsaW5rIHJlbD0ibGljZW5zZSIgaHJlZj0iaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvbGljZW5zZXMvYnkvMy4wLyIvPgogIDxpY29uPmh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItcHJvZmlsZS5wbmc8L2ljb24-CiAgPHVwZGF0ZWQ-MjAxMy0wOC0xOFQwODo1NzozOSswMDowMDwvdXBkYXRlZD4KIDwvc291cmNlPgogPGxpbmsgcmVsPSJzZWxmIiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNlcy9zaG93LzEuYXRvbSIvPgogPGxpbmsgcmVsPSJlZGl0IiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNlcy9zaG93LzEuYXRvbSIvPgogPHN0YXR1c25ldDpub3RpY2VfaW5mbyBsb2NhbF9pZD0iMSIgc291cmNlPSJhY3Rpdml0eSI-PC9zdGF0dXNuZXQ6bm90aWNlX2luZm8-CjwvZW50cnk-Cg==</me:data><me:encoding>base64url</me:encoding><me:alg>RSA-SHA256</me:alg><me:sig>jLsQxPL648cWNCVhRlhS6kOSPh1yKyT4sYdRTFGoj0vaW2wmqAHeZD8lnMnp6b7QdMs8n4P9uGaDT9_3BRJraDkEMa5IuRloChPFml0kxhlGl2iBlixGeiXbcl-TUB3yXp5KBOcJ6il7s2i32kaalUNvP9V7Z1Cob0eHdcRyF2s=</me:sig></me:env>'
salmon2='<?xml version="1.0" encoding="UTF-8"?><me:env xmlns:me="http://salmon-protocol.org/ns/magic-env"><me:data type="application/atom+xml">PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiID8-PGVudHJ5IHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDA1L0F0b20iIHhtbG5zOnRocj0iaHR0cDovL3B1cmwub3JnL3N5bmRpY2F0aW9uL3RocmVhZC8xLjAiIHhtbG5zOmFjdGl2aXR5PSJodHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zcGVjLzEuMC8iIHhtbG5zOmdlb3Jzcz0iaHR0cDovL3d3dy5nZW9yc3Mub3JnL2dlb3JzcyIgeG1sbnM6b3N0YXR1cz0iaHR0cDovL29zdGF0dXMub3JnL3NjaGVtYS8xLjAiIHhtbG5zOnBvY289Imh0dHA6Ly9wb3J0YWJsZWNvbnRhY3RzLm5ldC9zcGVjLzEuMCIgeG1sbnM6bWVkaWE9Imh0dHA6Ly9wdXJsLm9yZy9zeW5kaWNhdGlvbi9hdG9tbWVkaWEiIHhtbG5zOnN0YXR1c25ldD0iaHR0cDovL3N0YXR1cy5uZXQvc2NoZW1hL2FwaS8xLyI-CiA8aWQ-dGFnOnNuLDIwMTMtMDgtMTg6Zm9sbG93OjE6MjoyMDEzLTA4LTE4VDA4OjU3OjE1KzAwOjAwPC9pZD4KIDx0aXRsZT5Gb2xsb3c8L3RpdGxlPgogPGNvbnRlbnQgdHlwZT0iaHRtbCI-c24gaXMgbm93IGZvbGxvd2luZyBiaWphbi48L2NvbnRlbnQ-CiA8YWN0aXZpdHk6dmVyYj5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL2ZvbGxvdzwvYWN0aXZpdHk6dmVyYj4KIDxwdWJsaXNoZWQ-MjAxMy0wOC0xOFQwODo1NzoxNSswMDowMDwvcHVibGlzaGVkPgogPHVwZGF0ZWQ-MjAxMy0wOC0xOFQwODo1NzoxNSswMDowMDwvdXBkYXRlZD4KIDxhdXRob3I-CiAgPGFjdGl2aXR5Om9iamVjdC10eXBlPmh0dHA6Ly9hY3Rpdml0eXN0cmVhLm1zL3NjaGVtYS8xLjAvcGVyc29uPC9hY3Rpdml0eTpvYmplY3QtdHlwZT4KICA8dXJpPmh0dHA6Ly9zbi91c2VyLzE8L3VyaT4KICA8bmFtZT5zbjwvbmFtZT4KICA8bGluayByZWw9ImFsdGVybmF0ZSIgdHlwZT0idGV4dC9odG1sIiBocmVmPSJodHRwOi8vc24vc24iLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvcG5nIiBtZWRpYTp3aWR0aD0iOTYiIG1lZGlhOmhlaWdodD0iOTYiIGhyZWY9Imh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItcHJvZmlsZS5wbmciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvcG5nIiBtZWRpYTp3aWR0aD0iNDgiIG1lZGlhOmhlaWdodD0iNDgiIGhyZWY9Imh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItc3RyZWFtLnBuZyIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9wbmciIG1lZGlhOndpZHRoPSIyNCIgbWVkaWE6aGVpZ2h0PSIyNCIgaHJlZj0iaHR0cDovL3NuL3RoZW1lL25lby9kZWZhdWx0LWF2YXRhci1taW5pLnBuZyIvPgogIDxwb2NvOnByZWZlcnJlZFVzZXJuYW1lPnNuPC9wb2NvOnByZWZlcnJlZFVzZXJuYW1lPgogIDxwb2NvOmRpc3BsYXlOYW1lPnNuPC9wb2NvOmRpc3BsYXlOYW1lPgogIDxmb2xsb3dlcnMgdXJsPSJodHRwOi8vc24vc24vc3Vic2NyaWJlcnMiPjwvZm9sbG93ZXJzPgogPC9hdXRob3I-CiA8YWN0aXZpdHk6b2JqZWN0PgogIDxhY3Rpdml0eTpvYmplY3QtdHlwZT5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3BlcnNvbjwvYWN0aXZpdHk6b2JqZWN0LXR5cGU-CiAgPGlkPmh0dHA6Ly8xMjcuMC4wLjIvYmlqYW48L2lkPgogIDx0aXRsZT5iaWphbjwvdGl0bGU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovLzEyNy4wLjAuMi9iaWphbiIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9qcGVnIiBtZWRpYTp3aWR0aD0iOTYiIG1lZGlhOmhlaWdodD0iOTYiIGhyZWY9Imh0dHA6Ly9zbi9hdmF0YXIvMi1vcmlnaW5hbC0yMDEzMDgxODA4NTYxMy5qcGVnIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL2pwZWciIG1lZGlhOndpZHRoPSI5NiIgbWVkaWE6aGVpZ2h0PSI5NiIgaHJlZj0iaHR0cDovL3NuL2F2YXRhci8yLW9yaWdpbmFsLTIwMTMwODE4MDg1NjEzLmpwZWciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvanBlZyIgbWVkaWE6d2lkdGg9IjQ4IiBtZWRpYTpoZWlnaHQ9IjQ4IiBocmVmPSJodHRwOi8vc24vYXZhdGFyLzItNDgtMjAxMzA4MTgwODU2MTQuanBlZyIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9qcGVnIiBtZWRpYTp3aWR0aD0iMjQiIG1lZGlhOmhlaWdodD0iMjQiIGhyZWY9Imh0dHA6Ly9zbi9hdmF0YXIvMi0yNC0yMDEzMDgxODA4NTYxNC5qcGVnIi8-CiAgPHBvY286cHJlZmVycmVkVXNlcm5hbWU-YmlqYW48L3BvY286cHJlZmVycmVkVXNlcm5hbWU-CiAgPHBvY286ZGlzcGxheU5hbWU-YmlqYW48L3BvY286ZGlzcGxheU5hbWU-CiAgPHBvY286bm90ZT5ubyBkZXNjcmlwdGlvbiBpcyBwcm92aWRlZDwvcG9jbzpub3RlPgogIDxwb2NvOmFkZHJlc3M-CiAgIDxwb2NvOmZvcm1hdHRlZD5ubyBsb2NhdGlvbiBpcyBwcm92aWRlZDwvcG9jbzpmb3JtYXR0ZWQ-CiAgPC9wb2NvOmFkZHJlc3M-CiAgPHBvY286dXJscz4KICAgPHBvY286dHlwZT5ob21lcGFnZTwvcG9jbzp0eXBlPgogICA8cG9jbzp2YWx1ZT5odHRwOi8vZXhhbXBsZS5jb208L3BvY286dmFsdWU-CiAgIDxwb2NvOnByaW1hcnk-dHJ1ZTwvcG9jbzpwcmltYXJ5PgogIDwvcG9jbzp1cmxzPgogPC9hY3Rpdml0eTpvYmplY3Q-CiA8bGluayByZWw9InNlbGYiIHR5cGU9ImFwcGxpY2F0aW9uL2F0b20reG1sIiBocmVmPSJodHRwOi8vc24vYXBpL3N0YXR1c25ldC9hcHAvc3Vic2NyaXB0aW9ucy8xLzIuYXRvbSIvPgogPGxpbmsgcmVsPSJlZGl0IiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNuZXQvYXBwL3N1YnNjcmlwdGlvbnMvMS8yLmF0b20iLz4KPC9lbnRyeT4K</me:data><me:encoding>base64url</me:encoding><me:alg>RSA-SHA256</me:alg><me:sig>ZWy5MOMbGjuLPBCsXrQujwPwYDWUyGjVlCnALFF1lCXkM4vY3_AEsUUJaX_QDwab4R6wd6Eg36RwmQKCdxp8QXtvPkBp4RqLwbwgtjX4udU6EusISb2Xgc_vzDVcqb9eAIPsHaFbH0I8M15FTS7GkWQ-2ot9_ZvQbPXv06cwGO4=</me:sig></me:env>'
salmon3='<?xml version="1.0" encoding="UTF-8"?><me:env xmlns:me="http://salmon-protocol.org/ns/magic-env"><me:data type="application/atom+xml">PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiID8-PGVudHJ5IHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDA1L0F0b20iIHhtbG5zOnRocj0iaHR0cDovL3B1cmwub3JnL3N5bmRpY2F0aW9uL3RocmVhZC8xLjAiIHhtbG5zOmFjdGl2aXR5PSJodHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zcGVjLzEuMC8iIHhtbG5zOmdlb3Jzcz0iaHR0cDovL3d3dy5nZW9yc3Mub3JnL2dlb3JzcyIgeG1sbnM6b3N0YXR1cz0iaHR0cDovL29zdGF0dXMub3JnL3NjaGVtYS8xLjAiIHhtbG5zOnBvY289Imh0dHA6Ly9wb3J0YWJsZWNvbnRhY3RzLm5ldC9zcGVjLzEuMCIgeG1sbnM6bWVkaWE9Imh0dHA6Ly9wdXJsLm9yZy9zeW5kaWNhdGlvbi9hdG9tbWVkaWEiIHhtbG5zOnN0YXR1c25ldD0iaHR0cDovL3N0YXR1cy5uZXQvc2NoZW1hL2FwaS8xLyI-CiA8aWQ-dGFnOnNuLDIwMTMtMDgtMTg6dW5mb2xsb3c6MToyOjE5NzAtMDEtMDFUMDA6MDA6MDArMDA6MDA8L2lkPgogPHRpdGxlPlVuZm9sbG93PC90aXRsZT4KIDxjb250ZW50IHR5cGU9Imh0bWwiPnNuIHN0b3BwZWQgZm9sbG93aW5nIGJpamFuLjwvY29udGVudD4KIDxhY3Rpdml0eTp2ZXJiPmh0dHA6Ly9vc3RhdHVzLm9yZy9zY2hlbWEvMS4wL3VuZm9sbG93PC9hY3Rpdml0eTp2ZXJiPgogPHB1Ymxpc2hlZD4yMDEzLTA4LTE4VDA5OjI3OjMyKzAwOjAwPC9wdWJsaXNoZWQ-CiA8dXBkYXRlZD4yMDEzLTA4LTE4VDA5OjI3OjMyKzAwOjAwPC91cGRhdGVkPgogPGF1dGhvcj4KICA8YWN0aXZpdHk6b2JqZWN0LXR5cGU-aHR0cDovL2FjdGl2aXR5c3RyZWEubXMvc2NoZW1hLzEuMC9wZXJzb248L2FjdGl2aXR5Om9iamVjdC10eXBlPgogIDx1cmk-aHR0cDovL3NuL3VzZXIvMTwvdXJpPgogIDxuYW1lPnNuPC9uYW1lPgogIDxsaW5rIHJlbD0iYWx0ZXJuYXRlIiB0eXBlPSJ0ZXh0L2h0bWwiIGhyZWY9Imh0dHA6Ly9zbi9zbiIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9wbmciIG1lZGlhOndpZHRoPSI5NiIgbWVkaWE6aGVpZ2h0PSI5NiIgaHJlZj0iaHR0cDovL3NuL3RoZW1lL25lby9kZWZhdWx0LWF2YXRhci1wcm9maWxlLnBuZyIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9wbmciIG1lZGlhOndpZHRoPSI0OCIgbWVkaWE6aGVpZ2h0PSI0OCIgaHJlZj0iaHR0cDovL3NuL3RoZW1lL25lby9kZWZhdWx0LWF2YXRhci1zdHJlYW0ucG5nIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL3BuZyIgbWVkaWE6d2lkdGg9IjI0IiBtZWRpYTpoZWlnaHQ9IjI0IiBocmVmPSJodHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLW1pbmkucG5nIi8-CiAgPHBvY286cHJlZmVycmVkVXNlcm5hbWU-c248L3BvY286cHJlZmVycmVkVXNlcm5hbWU-CiAgPHBvY286ZGlzcGxheU5hbWU-c248L3BvY286ZGlzcGxheU5hbWU-CiAgPGZvbGxvd2VycyB1cmw9Imh0dHA6Ly9zbi9zbi9zdWJzY3JpYmVycyI-PC9mb2xsb3dlcnM-CiA8L2F1dGhvcj4KPC9lbnRyeT4K</me:data><me:encoding>base64url</me:encoding><me:alg>RSA-SHA256</me:alg><me:sig>gGyvo_44iNV5O5V5SQwzp5vnOvvBP74-ks3hgvGUBNQ1TQSZUrq7M1bDXN5A5ttf2j7P_mO96f9T5aQqE7qxoLk4w1E4YE6RZrOFG_Kj5mMU2E-O5SKQmZP2tf7OUQX343n_Wifhy-128YKaOTkjJc2hORbWpJj5wHx6CzuNi_c=</me:sig></me:env>'


salmon4='<?xml version="1.0" encoding="UTF-8"?><me:env xmlns:me="http://salmon-protocol.org/ns/magic-env"><me:data type="application/atom+xml">PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiID8-PGVudHJ5IHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDA1L0F0b20iIHhtbG5zOnRocj0iaHR0cDovL3B1cmwub3JnL3N5bmRpY2F0aW9uL3RocmVhZC8xLjAiIHhtbG5zOmFjdGl2aXR5PSJodHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zcGVjLzEuMC8iIHhtbG5zOmdlb3Jzcz0iaHR0cDovL3d3dy5nZW9yc3Mub3JnL2dlb3JzcyIgeG1sbnM6b3N0YXR1cz0iaHR0cDovL29zdGF0dXMub3JnL3NjaGVtYS8xLjAiIHhtbG5zOnBvY289Imh0dHA6Ly9wb3J0YWJsZWNvbnRhY3RzLm5ldC9zcGVjLzEuMCIgeG1sbnM6bWVkaWE9Imh0dHA6Ly9wdXJsLm9yZy9zeW5kaWNhdGlvbi9hdG9tbWVkaWEiIHhtbG5zOnN0YXR1c25ldD0iaHR0cDovL3N0YXR1cy5uZXQvc2NoZW1hL2FwaS8xLyI-CiA8aWQ-dGFnOnNuLDIwMTMtMDgtMTk6cG9zdDoyPC9pZD4KIDx0aXRsZT48L3RpdGxlPgogPGNvbnRlbnQgdHlwZT0iaHRtbCI-Jmx0O2EgaHJlZj0mcXVvdDtodHRwOi8vc24vc24mcXVvdDsmZ3Q7c24mbHQ7L2EmZ3Q7IHN0YXJ0ZWQgZm9sbG93aW5nICZsdDthIGhyZWY9JnF1b3Q7aHR0cDovLzEyNy4wLjAuMi9iaWphbiZxdW90OyZndDtiaWphbiZsdDsvYSZndDsuPC9jb250ZW50PgogPGFjdGl2aXR5OnZlcmI-aHR0cDovL2FjdGl2aXR5c3RyZWEubXMvc2NoZW1hLzEuMC9mb2xsb3c8L2FjdGl2aXR5OnZlcmI-CiA8cHVibGlzaGVkPjIwMTMtMDgtMTlUMDY6MzU6NDIrMDA6MDA8L3B1Ymxpc2hlZD4KIDx1cGRhdGVkPjIwMTMtMDgtMTlUMDY6MzU6NDIrMDA6MDA8L3VwZGF0ZWQ-CiA8YXV0aG9yPgogIDxhY3Rpdml0eTpvYmplY3QtdHlwZT5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3BlcnNvbjwvYWN0aXZpdHk6b2JqZWN0LXR5cGU-CiAgPHVyaT5odHRwOi8vc24vdXNlci8xPC91cmk-CiAgPG5hbWU-c248L25hbWU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovL3NuL3NuIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL3BuZyIgbWVkaWE6d2lkdGg9Ijk2IiBtZWRpYTpoZWlnaHQ9Ijk2IiBocmVmPSJodHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLXByb2ZpbGUucG5nIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL3BuZyIgbWVkaWE6d2lkdGg9IjQ4IiBtZWRpYTpoZWlnaHQ9IjQ4IiBocmVmPSJodHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLXN0cmVhbS5wbmciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvcG5nIiBtZWRpYTp3aWR0aD0iMjQiIG1lZGlhOmhlaWdodD0iMjQiIGhyZWY9Imh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItbWluaS5wbmciLz4KICA8cG9jbzpwcmVmZXJyZWRVc2VybmFtZT5zbjwvcG9jbzpwcmVmZXJyZWRVc2VybmFtZT4KICA8cG9jbzpkaXNwbGF5TmFtZT5zbjwvcG9jbzpkaXNwbGF5TmFtZT4KICA8Zm9sbG93ZXJzIHVybD0iaHR0cDovL3NuL3NuL3N1YnNjcmliZXJzIj48L2ZvbGxvd2Vycz4KICA8c3RhdHVzbmV0OnByb2ZpbGVfaW5mbyBsb2NhbF9pZD0iMSI-PC9zdGF0dXNuZXQ6cHJvZmlsZV9pbmZvPgogPC9hdXRob3I-CiA8YWN0aXZpdHk6b2JqZWN0PgogIDxhY3Rpdml0eTpvYmplY3QtdHlwZT5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3BlcnNvbjwvYWN0aXZpdHk6b2JqZWN0LXR5cGU-CiAgPGlkPmh0dHA6Ly8xMjcuMC4wLjIvYmlqYW48L2lkPgogIDx0aXRsZT5iaWphbjwvdGl0bGU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovLzEyNy4wLjAuMi9iaWphbiIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9qcGVnIiBtZWRpYTp3aWR0aD0iOTYiIG1lZGlhOmhlaWdodD0iOTYiIGhyZWY9Imh0dHA6Ly9zbi9hdmF0YXIvMi1vcmlnaW5hbC0yMDEzMDgxODA4NTYxMy5qcGVnIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL2pwZWciIG1lZGlhOndpZHRoPSI5NiIgbWVkaWE6aGVpZ2h0PSI5NiIgaHJlZj0iaHR0cDovL3NuL2F2YXRhci8yLW9yaWdpbmFsLTIwMTMwODE4MDg1NjEzLmpwZWciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvanBlZyIgbWVkaWE6d2lkdGg9IjQ4IiBtZWRpYTpoZWlnaHQ9IjQ4IiBocmVmPSJodHRwOi8vc24vYXZhdGFyLzItNDgtMjAxMzA4MTgwODU2MTQuanBlZyIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9qcGVnIiBtZWRpYTp3aWR0aD0iMjQiIG1lZGlhOmhlaWdodD0iMjQiIGhyZWY9Imh0dHA6Ly9zbi9hdmF0YXIvMi0yNC0yMDEzMDgxODA4NTYxNC5qcGVnIi8-CiAgPHBvY286cHJlZmVycmVkVXNlcm5hbWU-YmlqYW48L3BvY286cHJlZmVycmVkVXNlcm5hbWU-CiAgPHBvY286ZGlzcGxheU5hbWU-YmlqYW48L3BvY286ZGlzcGxheU5hbWU-CiAgPHBvY286bm90ZT5ubyBkZXNjcmlwdGlvbiBpcyBwcm92aWRlZDwvcG9jbzpub3RlPgogIDxwb2NvOmFkZHJlc3M-CiAgIDxwb2NvOmZvcm1hdHRlZD5ubyBsb2NhdGlvbiBpcyBwcm92aWRlZDwvcG9jbzpmb3JtYXR0ZWQ-CiAgPC9wb2NvOmFkZHJlc3M-CiAgPHBvY286dXJscz4KICAgPHBvY286dHlwZT5ob21lcGFnZTwvcG9jbzp0eXBlPgogICA8cG9jbzp2YWx1ZT5odHRwOi8vZXhhbXBsZS5jb208L3BvY286dmFsdWU-CiAgIDxwb2NvOnByaW1hcnk-dHJ1ZTwvcG9jbzpwcmltYXJ5PgogIDwvcG9jbzp1cmxzPgogPC9hY3Rpdml0eTpvYmplY3Q-CiA8bGluayByZWw9Im9zdGF0dXM6Y29udmVyc2F0aW9uIiBocmVmPSJodHRwOi8vc24vY29udmVyc2F0aW9uLzIiLz4KIDxsaW5rIHJlbD0ib3N0YXR1czphdHRlbnRpb24iIGhyZWY9Imh0dHA6Ly8xMjcuMC4wLjIvYmlqYW4iLz4KIDxsaW5rIHJlbD0ibWVudGlvbmVkIiBocmVmPSJodHRwOi8vMTI3LjAuMC4yL2JpamFuIi8-CiA8bGluayByZWw9Im9zdGF0dXM6YXR0ZW50aW9uIiBocmVmPSJodHRwOi8vYWN0aXZpdHlzY2hlbWEub3JnL2NvbGxlY3Rpb24vcHVibGljIi8-CiA8bGluayByZWw9Im1lbnRpb25lZCIgaHJlZj0iaHR0cDovL2FjdGl2aXR5c2NoZW1hLm9yZy9jb2xsZWN0aW9uL3B1YmxpYyIvPgogPGNhdGVnb3J5IHRlcm09IiI-PC9jYXRlZ29yeT4KIDxzb3VyY2U-CiAgPGlkPmh0dHA6Ly9zbi9hcGkvc3RhdHVzZXMvdXNlcl90aW1lbGluZS8xLmF0b208L2lkPgogIDx0aXRsZT5zbjwvdGl0bGU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovL3NuL3NuIi8-CiAgPGxpbmsgcmVsPSJzZWxmIiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNlcy91c2VyX3RpbWVsaW5lLzEuYXRvbSIvPgogIDxsaW5rIHJlbD0ibGljZW5zZSIgaHJlZj0iaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvbGljZW5zZXMvYnkvMy4wLyIvPgogIDxpY29uPmh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItcHJvZmlsZS5wbmc8L2ljb24-CiAgPHVwZGF0ZWQ-MjAxMy0wOC0xOVQwNjozNTo0MiswMDowMDwvdXBkYXRlZD4KIDwvc291cmNlPgogPGxpbmsgcmVsPSJzZWxmIiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNlcy9zaG93LzIuYXRvbSIvPgogPGxpbmsgcmVsPSJlZGl0IiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNlcy9zaG93LzIuYXRvbSIvPgogPHN0YXR1c25ldDpub3RpY2VfaW5mbyBsb2NhbF9pZD0iMiIgc291cmNlPSJhY3Rpdml0eSI-PC9zdGF0dXNuZXQ6bm90aWNlX2luZm8-CjwvZW50cnk-Cg==</me:data><me:encoding>base64url</me:encoding><me:alg>RSA-SHA256</me:alg><me:sig>iVNeJvZeXBHQaJU55XrLq1cV2AP42W081lX-Eb9bi9v7JtL4skc6pRjbMW7G_NHKCNznxZ9w78cOiPaM-4IQQM-mQbs0rWXirNtaPa6-fIhiNioCpQYJnk2y8azLRfxTxbOukHrDVG1pjRRQiJaEHtgNd62BwLiVAR0sdXOwoYI=</me:sig></me:env>'
salmon5='<?xml version="1.0" encoding="UTF-8"?><me:env xmlns:me="http://salmon-protocol.org/ns/magic-env"><me:data type="application/atom+xml">PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiID8-PGVudHJ5IHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDA1L0F0b20iIHhtbG5zOnRocj0iaHR0cDovL3B1cmwub3JnL3N5bmRpY2F0aW9uL3RocmVhZC8xLjAiIHhtbG5zOmFjdGl2aXR5PSJodHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zcGVjLzEuMC8iIHhtbG5zOmdlb3Jzcz0iaHR0cDovL3d3dy5nZW9yc3Mub3JnL2dlb3JzcyIgeG1sbnM6b3N0YXR1cz0iaHR0cDovL29zdGF0dXMub3JnL3NjaGVtYS8xLjAiIHhtbG5zOnBvY289Imh0dHA6Ly9wb3J0YWJsZWNvbnRhY3RzLm5ldC9zcGVjLzEuMCIgeG1sbnM6bWVkaWE9Imh0dHA6Ly9wdXJsLm9yZy9zeW5kaWNhdGlvbi9hdG9tbWVkaWEiIHhtbG5zOnN0YXR1c25ldD0iaHR0cDovL3N0YXR1cy5uZXQvc2NoZW1hL2FwaS8xLyI-CiA8aWQ-dGFnOnNuLDIwMTMtMDgtMTk6Zm9sbG93OjE6MjoyMDEzLTA4LTE5VDA2OjM1OjQxKzAwOjAwPC9pZD4KIDx0aXRsZT5Gb2xsb3c8L3RpdGxlPgogPGNvbnRlbnQgdHlwZT0iaHRtbCI-c24gaXMgbm93IGZvbGxvd2luZyBiaWphbi48L2NvbnRlbnQ-CiA8YWN0aXZpdHk6dmVyYj5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL2ZvbGxvdzwvYWN0aXZpdHk6dmVyYj4KIDxwdWJsaXNoZWQ-MjAxMy0wOC0xOVQwNjozNTo0MSswMDowMDwvcHVibGlzaGVkPgogPHVwZGF0ZWQ-MjAxMy0wOC0xOVQwNjozNTo0MSswMDowMDwvdXBkYXRlZD4KIDxhdXRob3I-CiAgPGFjdGl2aXR5Om9iamVjdC10eXBlPmh0dHA6Ly9hY3Rpdml0eXN0cmVhLm1zL3NjaGVtYS8xLjAvcGVyc29uPC9hY3Rpdml0eTpvYmplY3QtdHlwZT4KICA8dXJpPmh0dHA6Ly9zbi91c2VyLzE8L3VyaT4KICA8bmFtZT5zbjwvbmFtZT4KICA8bGluayByZWw9ImFsdGVybmF0ZSIgdHlwZT0idGV4dC9odG1sIiBocmVmPSJodHRwOi8vc24vc24iLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvcG5nIiBtZWRpYTp3aWR0aD0iOTYiIG1lZGlhOmhlaWdodD0iOTYiIGhyZWY9Imh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItcHJvZmlsZS5wbmciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvcG5nIiBtZWRpYTp3aWR0aD0iNDgiIG1lZGlhOmhlaWdodD0iNDgiIGhyZWY9Imh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItc3RyZWFtLnBuZyIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9wbmciIG1lZGlhOndpZHRoPSIyNCIgbWVkaWE6aGVpZ2h0PSIyNCIgaHJlZj0iaHR0cDovL3NuL3RoZW1lL25lby9kZWZhdWx0LWF2YXRhci1taW5pLnBuZyIvPgogIDxwb2NvOnByZWZlcnJlZFVzZXJuYW1lPnNuPC9wb2NvOnByZWZlcnJlZFVzZXJuYW1lPgogIDxwb2NvOmRpc3BsYXlOYW1lPnNuPC9wb2NvOmRpc3BsYXlOYW1lPgogIDxmb2xsb3dlcnMgdXJsPSJodHRwOi8vc24vc24vc3Vic2NyaWJlcnMiPjwvZm9sbG93ZXJzPgogPC9hdXRob3I-CiA8YWN0aXZpdHk6b2JqZWN0PgogIDxhY3Rpdml0eTpvYmplY3QtdHlwZT5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3BlcnNvbjwvYWN0aXZpdHk6b2JqZWN0LXR5cGU-CiAgPGlkPmh0dHA6Ly8xMjcuMC4wLjIvYmlqYW48L2lkPgogIDx0aXRsZT5iaWphbjwvdGl0bGU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovLzEyNy4wLjAuMi9iaWphbiIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9qcGVnIiBtZWRpYTp3aWR0aD0iOTYiIG1lZGlhOmhlaWdodD0iOTYiIGhyZWY9Imh0dHA6Ly9zbi9hdmF0YXIvMi1vcmlnaW5hbC0yMDEzMDgxODA4NTYxMy5qcGVnIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL2pwZWciIG1lZGlhOndpZHRoPSI5NiIgbWVkaWE6aGVpZ2h0PSI5NiIgaHJlZj0iaHR0cDovL3NuL2F2YXRhci8yLW9yaWdpbmFsLTIwMTMwODE4MDg1NjEzLmpwZWciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvanBlZyIgbWVkaWE6d2lkdGg9IjQ4IiBtZWRpYTpoZWlnaHQ9IjQ4IiBocmVmPSJodHRwOi8vc24vYXZhdGFyLzItNDgtMjAxMzA4MTgwODU2MTQuanBlZyIvPgogIDxsaW5rIHJlbD0iYXZhdGFyIiB0eXBlPSJpbWFnZS9qcGVnIiBtZWRpYTp3aWR0aD0iMjQiIG1lZGlhOmhlaWdodD0iMjQiIGhyZWY9Imh0dHA6Ly9zbi9hdmF0YXIvMi0yNC0yMDEzMDgxODA4NTYxNC5qcGVnIi8-CiAgPHBvY286cHJlZmVycmVkVXNlcm5hbWU-YmlqYW48L3BvY286cHJlZmVycmVkVXNlcm5hbWU-CiAgPHBvY286ZGlzcGxheU5hbWU-YmlqYW48L3BvY286ZGlzcGxheU5hbWU-CiAgPHBvY286bm90ZT5ubyBkZXNjcmlwdGlvbiBpcyBwcm92aWRlZDwvcG9jbzpub3RlPgogIDxwb2NvOmFkZHJlc3M-CiAgIDxwb2NvOmZvcm1hdHRlZD5ubyBsb2NhdGlvbiBpcyBwcm92aWRlZDwvcG9jbzpmb3JtYXR0ZWQ-CiAgPC9wb2NvOmFkZHJlc3M-CiAgPHBvY286dXJscz4KICAgPHBvY286dHlwZT5ob21lcGFnZTwvcG9jbzp0eXBlPgogICA8cG9jbzp2YWx1ZT5odHRwOi8vZXhhbXBsZS5jb208L3BvY286dmFsdWU-CiAgIDxwb2NvOnByaW1hcnk-dHJ1ZTwvcG9jbzpwcmltYXJ5PgogIDwvcG9jbzp1cmxzPgogPC9hY3Rpdml0eTpvYmplY3Q-CiA8bGluayByZWw9InNlbGYiIHR5cGU9ImFwcGxpY2F0aW9uL2F0b20reG1sIiBocmVmPSJodHRwOi8vc24vYXBpL3N0YXR1c25ldC9hcHAvc3Vic2NyaXB0aW9ucy8xLzIuYXRvbSIvPgogPGxpbmsgcmVsPSJlZGl0IiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNuZXQvYXBwL3N1YnNjcmlwdGlvbnMvMS8yLmF0b20iLz4KPC9lbnRyeT4K</me:data><me:encoding>base64url</me:encoding><me:alg>RSA-SHA256</me:alg><me:sig>FANSAxplS9lmzM2iPIQr6Vzie33V4TXWKi2QuK0Aj79AMkK2L0XoD9q_YAZBuHilkiKsKkUKMFV6xwKJEeLkP6DRnux5Ex61GqaOJzUunLRaL-rmKDxFy0g-CotQMBkjhHoTUMIiDgPD7MSLQmmCwlK9kLMTX42XUq-AnFQUz_w=</me:sig></me:env>'

salmon_mention='<me:env xmlns:me="http://salmon-protocol.org/ns/magic-env"><me:data type="application/atom+xml">PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiID8-PGVudHJ5IHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDA1L0F0b20iIHhtbG5zOnRocj0iaHR0cDovL3B1cmwub3JnL3N5bmRpY2F0aW9uL3RocmVhZC8xLjAiIHhtbG5zOmFjdGl2aXR5PSJodHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zcGVjLzEuMC8iIHhtbG5zOmdlb3Jzcz0iaHR0cDovL3d3dy5nZW9yc3Mub3JnL2dlb3JzcyIgeG1sbnM6b3N0YXR1cz0iaHR0cDovL29zdGF0dXMub3JnL3NjaGVtYS8xLjAiIHhtbG5zOnBvY289Imh0dHA6Ly9wb3J0YWJsZWNvbnRhY3RzLm5ldC9zcGVjLzEuMCIgeG1sbnM6bWVkaWE9Imh0dHA6Ly9wdXJsLm9yZy9zeW5kaWNhdGlvbi9hdG9tbWVkaWEiIHhtbG5zOnN0YXR1c25ldD0iaHR0cDovL3N0YXR1cy5uZXQvc2NoZW1hL2FwaS8xLyI-CiA8YWN0aXZpdHk6b2JqZWN0LXR5cGU-aHR0cDovL2FjdGl2aXR5c3RyZWEubXMvc2NoZW1hLzEuMC9ub3RlPC9hY3Rpdml0eTpvYmplY3QtdHlwZT4KIDxpZD5odHRwOi8vc24vbm90aWNlLzM8L2lkPgogPGNvbnRlbnQgdHlwZT0iaHRtbCI-aGVsbG8gQCZsdDtzcGFuIGNsYXNzPSZxdW90O3ZjYXJkJnF1b3Q7Jmd0OyZsdDthIGhyZWY9JnF1b3Q7aHR0cDovLzEyNy4wLjAuMi9iaWphbiZxdW90OyBjbGFzcz0mcXVvdDt1cmwmcXVvdDsmZ3Q7Jmx0O3NwYW4gY2xhc3M9JnF1b3Q7Zm4gbmlja25hbWUgbWVudGlvbiZxdW90OyZndDtiaWphbiZsdDsvc3BhbiZndDsmbHQ7L2EmZ3Q7Jmx0Oy9zcGFuJmd0OzwvY29udGVudD4KIDxsaW5rIHJlbD0iYWx0ZXJuYXRlIiB0eXBlPSJ0ZXh0L2h0bWwiIGhyZWY9Imh0dHA6Ly9zbi9ub3RpY2UvMyIvPgogPHN0YXR1c19uZXQgbm90aWNlX2lkPSIzIj48L3N0YXR1c19uZXQ-CiA8YWN0aXZpdHk6dmVyYj5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3Bvc3Q8L2FjdGl2aXR5OnZlcmI-CiA8cHVibGlzaGVkPjIwMTMtMDgtMTlUMDY6Mzk6MzYrMDA6MDA8L3B1Ymxpc2hlZD4KIDx1cGRhdGVkPjIwMTMtMDgtMTlUMDY6Mzk6MzYrMDA6MDA8L3VwZGF0ZWQ-CiA8YXV0aG9yPgogIDxhY3Rpdml0eTpvYmplY3QtdHlwZT5odHRwOi8vYWN0aXZpdHlzdHJlYS5tcy9zY2hlbWEvMS4wL3BlcnNvbjwvYWN0aXZpdHk6b2JqZWN0LXR5cGU-CiAgPHVyaT5odHRwOi8vc24vdXNlci8xPC91cmk-CiAgPG5hbWU-c248L25hbWU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovL3NuL3NuIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL3BuZyIgbWVkaWE6d2lkdGg9Ijk2IiBtZWRpYTpoZWlnaHQ9Ijk2IiBocmVmPSJodHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLXByb2ZpbGUucG5nIi8-CiAgPGxpbmsgcmVsPSJhdmF0YXIiIHR5cGU9ImltYWdlL3BuZyIgbWVkaWE6d2lkdGg9IjQ4IiBtZWRpYTpoZWlnaHQ9IjQ4IiBocmVmPSJodHRwOi8vc24vdGhlbWUvbmVvL2RlZmF1bHQtYXZhdGFyLXN0cmVhbS5wbmciLz4KICA8bGluayByZWw9ImF2YXRhciIgdHlwZT0iaW1hZ2UvcG5nIiBtZWRpYTp3aWR0aD0iMjQiIG1lZGlhOmhlaWdodD0iMjQiIGhyZWY9Imh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItbWluaS5wbmciLz4KICA8cG9jbzpwcmVmZXJyZWRVc2VybmFtZT5zbjwvcG9jbzpwcmVmZXJyZWRVc2VybmFtZT4KICA8cG9jbzpkaXNwbGF5TmFtZT5zbjwvcG9jbzpkaXNwbGF5TmFtZT4KICA8Zm9sbG93ZXJzIHVybD0iaHR0cDovL3NuL3NuL3N1YnNjcmliZXJzIj48L2ZvbGxvd2Vycz4KICA8c3RhdHVzbmV0OnByb2ZpbGVfaW5mbyBsb2NhbF9pZD0iMSI-PC9zdGF0dXNuZXQ6cHJvZmlsZV9pbmZvPgogPC9hdXRob3I-CiA8bGluayByZWw9Im9zdGF0dXM6Y29udmVyc2F0aW9uIiBocmVmPSJodHRwOi8vc24vY29udmVyc2F0aW9uLzMiLz4KIDxsaW5rIHJlbD0ib3N0YXR1czphdHRlbnRpb24iIGhyZWY9Imh0dHA6Ly8xMjcuMC4wLjIvYmlqYW4iLz4KIDxsaW5rIHJlbD0ibWVudGlvbmVkIiBocmVmPSJodHRwOi8vMTI3LjAuMC4yL2JpamFuIi8-CiA8bGluayByZWw9Im9zdGF0dXM6YXR0ZW50aW9uIiBocmVmPSJodHRwOi8vYWN0aXZpdHlzY2hlbWEub3JnL2NvbGxlY3Rpb24vcHVibGljIi8-CiA8bGluayByZWw9Im1lbnRpb25lZCIgaHJlZj0iaHR0cDovL2FjdGl2aXR5c2NoZW1hLm9yZy9jb2xsZWN0aW9uL3B1YmxpYyIvPgogPGNhdGVnb3J5IHRlcm09IiI-PC9jYXRlZ29yeT4KIDxzb3VyY2U-CiAgPGlkPmh0dHA6Ly9zbi9hcGkvc3RhdHVzZXMvdXNlcl90aW1lbGluZS8xLmF0b208L2lkPgogIDx0aXRsZT5zbjwvdGl0bGU-CiAgPGxpbmsgcmVsPSJhbHRlcm5hdGUiIHR5cGU9InRleHQvaHRtbCIgaHJlZj0iaHR0cDovL3NuL3NuIi8-CiAgPGxpbmsgcmVsPSJzZWxmIiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNlcy91c2VyX3RpbWVsaW5lLzEuYXRvbSIvPgogIDxsaW5rIHJlbD0ibGljZW5zZSIgaHJlZj0iaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvbGljZW5zZXMvYnkvMy4wLyIvPgogIDxpY29uPmh0dHA6Ly9zbi90aGVtZS9uZW8vZGVmYXVsdC1hdmF0YXItcHJvZmlsZS5wbmc8L2ljb24-CiAgPHVwZGF0ZWQ-MjAxMy0wOC0xOVQwNjozOTozNiswMDowMDwvdXBkYXRlZD4KIDwvc291cmNlPgogPGxpbmsgcmVsPSJzZWxmIiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNlcy9zaG93LzMuYXRvbSIvPgogPGxpbmsgcmVsPSJlZGl0IiB0eXBlPSJhcHBsaWNhdGlvbi9hdG9tK3htbCIgaHJlZj0iaHR0cDovL3NuL2FwaS9zdGF0dXNlcy9zaG93LzMuYXRvbSIvPgogPHN0YXR1c25ldDpub3RpY2VfaW5mbyBsb2NhbF9pZD0iMyIgc291cmNlPSJ3ZWIiPjwvc3RhdHVzbmV0Om5vdGljZV9pbmZvPgo8L2VudHJ5Pgo=</me:data><me:encoding>base64url</me:encoding><me:alg>RSA-SHA256</me:alg><me:sig>PJ4o4UN1hyGEzWWbfpIlO75axZW2YAhznpXuq_MJ83-eOYTDB2ZJWlGdW9Hg_lY_4ceYzMUkYZxR4PFD2M77XyMFjnDayzgjWDeTTOKAmA4S1OKLVPZFEGEghMjkMmpYWAasNCyImIO1dIqAaGSmC8xYQqQEnFYnvM8dp3E2Hyc=</me:sig></me:env>'
xml2 = '<?xml version="1.0" encoding="UTF-8"?><feed xml:lang="en-US" xmlns="http://www.w3.org/2005/Atom" xmlns:thr="http://purl.org/syndication/thread/1.0" xmlns:georss="http://www.georss.org/georss" xmlns:activity="http://activitystrea.ms/spec/1.0/" xmlns:media="http://purl.org/syndication/atommedia" xmlns:poco="http://portablecontacts.net/spec/1.0" xmlns:ostatus="http://ostatus.org/schema/1.0" xmlns:statusnet="http://status.net/schema/api/1/"> <generator uri="http://status.net" version="1.1.0-release">StatusNet</generator> <id>http://quitter.se/api/statuses/user_timeline/114757.atom</id> <title>bijan timeline</title> <subtitle>Updates from bijan on Quitter!</subtitle> <logo>http://quitter.se/avatar/114757-96-20130710202211.png</logo> <updated>2013-08-11T15:43:47+02:00</updated> <link href="http://quitter.se/bijan" rel="alternate" type="text/html"/> <link href="http://quitter.se/main/sup" rel="http://api.friendfeed.com/2008/03#sup" type="application/json"/> <link href="http://quitter.se/main/push/hub" rel="hub"/> <link href="http://quitter.se/main/salmon/user/114757" rel="salmon"/> <link href="http://quitter.se/main/salmon/user/114757" rel="http://salmon-protocol.org/ns/salmon-replies"/> <link href="http://quitter.se/main/salmon/user/114757" rel="http://salmon-protocol.org/ns/salmon-mention"/> <link href="http://quitter.se/api/statuses/user_timeline/114757.atom" rel="self" type="application/atom+xml"/></feed>'

author = '<author> <activity:object-type>http://activitystrea.ms/schema/1.0/person</activity:object-type> <uri>http://quitter.se/user/114757</uri> <name>bijan</name> <link rel="alternate" type="text/html" href="http://quitter.se/bijan"/> <link rel="avatar" type="image/png" media:width="170" media:height="170" href="http://quitter.se/avatar/114757-170-20130710202211.png"/> <link rel="avatar" type="image/png" media:width="96" media:height="96" href="http://quitter.se/avatar/114757-96-20130710202211.png"/> <link rel="avatar" type="image/png" media:width="48" media:height="48" href="http://quitter.se/avatar/114757-48-20130710202211.png"/> <link rel="avatar" type="image/png" media:width="24" media:height="24" href="http://quitter.se/avatar/114757-24-20130710202211.png"/> <poco:preferredUsername>bijan</poco:preferredUsername> <poco:displayName>bijan ebrahimi</poco:displayName> <poco:note>web developer and a FreeSoftware fan. developer of #crow and i surely love Linux so beware, i may bite ;)</poco:note> <poco:address>  <poco:formatted>open web, Internet</poco:formatted> </poco:address> <poco:urls>  <poco:type>homepage</poco:type>  <poco:value>http://RoutinesExcluded.tk/</poco:value>  <poco:primary>true</poco:primary> </poco:urls> <statusnet:profile_info local_id="114757"></statusnet:profile_info></author>'
author2 = '<author><activity:object-type>http://activitystrea.ms/schema/1.0/person</activity:object-type><uri>http://sn/user/1</uri><name>sn</name><link rel="alternate" type="text/html" href="http://sn/sn" /><link rel="avatar" type="image/png" media:width="96" media:height="96" href="http://sn/theme/neo/default-avatar-profile.png" /><link rel="avatar" type="image/png" media:width="48" media:height="48" href="http://sn/theme/neo/default-avatar-stream.png" /><link rel="avatar" type="image/png" media:width="24" media:height="24" href="http://sn/theme/neo/default-avatar-mini.png" /><poco:preferredUsername>sn</poco:preferredUsername><poco:displayName>sn</poco:displayName><followers url="http://sn/sn/subscribers" /><statusnet:profile_info local_id="1" />  </author>'


entry1 = '''<?xml version="1.0" encoding="UTF-8"?>
<entry xmlns="http://www.w3.org/2005/Atom" xmlns:thr="http://purl.org/syndication/thread/1.0" xmlns:activity="http://activitystrea.ms/spec/1.0/" xmlns:georss="http://www.georss.org/georss" xmlns:ostatus="http://ostatus.org/schema/1.0" xmlns:poco="http://portablecontacts.net/spec/1.0" xmlns:media="http://purl.org/syndication/atommedia" xmlns:statusnet="http://status.net/schema/api/1/">
  <id>tag:sn,2013-08-18:post:1</id>
  <title>Nothing</title>
  <content type="html">&lt;a href=&quot;http://sn/sn&quot;&gt;sn&lt;/a&gt; started following &lt;a href=&quot;http://127.0.0.2/bijan&quot;&gt;bijan&lt;/a&gt;.</content>
  <activity:verb>http://activitystrea.ms/schema/1.0/follow</activity:verb>
  <published>2013-08-18T08:57:39+00:00</published>
  <updated>2013-08-18T08:57:39+00:00</updated>
  <author>
    <activity:object-type>http://activitystrea.ms/schema/1.0/person</activity:object-type>
    <uri>http://sn/user/1</uri>
    <name>sn</name>
    <link rel="alternate" type="text/html" href="http://sn/sn" />
    <link rel="avatar" type="image/png" media:width="96" media:height="96" href="http://sn/theme/neo/default-avatar-profile.png" />
    <link rel="avatar" type="image/png" media:width="48" media:height="48" href="http://sn/theme/neo/default-avatar-stream.png" />
    <link rel="avatar" type="image/png" media:width="24" media:height="24" href="http://sn/theme/neo/default-avatar-mini.png" />
    <poco:preferredUsername>sn</poco:preferredUsername>
    <poco:displayName>sn</poco:displayName>
    <followers url="http://sn/sn/subscribers" />
    <statusnet:profile_info local_id="1" />
  </author>
  <activity:object>
    <activity:object-type>http://activitystrea.ms/schema/1.0/person</activity:object-type>
    <id>http://127.0.0.2/bijan</id>
    <title>bijan</title>
    <link rel="alternate" type="text/html" href="http://127.0.0.2/bijan" />
    <link rel="avatar" type="image/jpeg" media:width="96" media:height="96" href="http://sn/avatar/2-original-20130818085613.jpeg" />
    <link rel="avatar" type="image/jpeg" media:width="96" media:height="96" href="http://sn/avatar/2-original-20130818085613.jpeg" />
    <link rel="avatar" type="image/jpeg" media:width="48" media:height="48" href="http://sn/avatar/2-48-20130818085614.jpeg" />
    <link rel="avatar" type="image/jpeg" media:width="24" media:height="24" href="http://sn/avatar/2-24-20130818085614.jpeg" />
    <poco:preferredUsername>bijan</poco:preferredUsername>
    <poco:displayName>bijan</poco:displayName>
    <poco:note>no description is provided</poco:note>
    <poco:address>
      <poco:formatted>no location is provided</poco:formatted>
    </poco:address>
    <poco:urls>
      <poco:type>homepage</poco:type>
      <poco:value>http://example.com</poco:value>
      <poco:primary>true</poco:primary>
    </poco:urls>
  </activity:object>
  <link rel="ostatus:conversation" href="http://sn/conversation/1" />
  <link rel="ostatus:attention" href="http://127.0.0.2/bijan" />
  <link rel="mentioned" href="http://127.0.0.2/bijan" />
  <link rel="ostatus:attention" href="http://activityschema.org/collection/public" />
  <link rel="mentioned" href="http://activityschema.org/collection/public" />
  <category term="" />
  <source>
    <id>http://sn/api/statuses/user_timeline/1.atom</id>
    <title>sn</title>
    <link rel="alternate" type="text/html" href="http://sn/sn" />
    <link rel="self" type="application/atom+xml" href="http://sn/api/statuses/user_timeline/1.atom" />
    <link rel="license" href="http://creativecommons.org/licenses/by/3.0/" />
    <icon>http://sn/theme/neo/default-avatar-profile.png</icon>
    <updated>2013-08-18T08:57:39+00:00</updated>
  </source>
  <link rel="self" type="application/atom+xml" href="http://sn/api/statuses/show/1.atom" />
  <link rel="edit" type="application/atom+xml" href="http://sn/api/statuses/show/1.atom" />
  <statusnet:notice_info local_id="1" source="activity" />
</entry>'''
entry2 = '''<?xml version="1.0" encoding="UTF-8"?>
<entry>
  <activity:object-type>http://activitystrea.ms/schema/1.0/note</activity:object-type>
  <id>http://quitter.se/notice/2104527</id>
  <title>soon i\'ll freeze new features on !Crow and will be ready for new stable version with lots of features and bug fixes. i\'m pretty excited :D</title>
  <content type="html">soon i\'ll freeze new features on !&lt;span class=&quot;vcard&quot;&gt;&lt;a href=&quot;http://quitter.se/group/1107/id&quot; class=&quot;url&quot; title=&quot;crow (crow)&quot;&gt;&lt;span class=&quot;fn nickname group&quot;&gt;Crow&lt;/span&gt;&lt;/a&gt;&lt;/span&gt; and will be ready for new stable version with lots of features and bug fixes. i\'m pretty excited :D</content>
  <link rel="alternate" type="text/html" href="http://quitter.se/notice/2104527" />
  <activity:verb>http://activitystrea.ms/schema/1.0/post</activity:verb>
  <published>2013-08-11T08:52:17+00:00</published>
  <updated>2013-08-11T08:52:17+00:00</updated>
  <link rel="ostatus:conversation" href="http://quitter.se/conversation/1898390" />
  <link rel="ostatus:attention" href="http://quitter.se/group/1107/id" />
  <link rel="mentioned" href="http://quitter.se/group/1107/id" />
  <link rel="self" type="application/atom+xml" href="http://quitter.se/api/statuses/show/2104527.atom" />
  <link rel="edit" type="application/atom+xml" href="http://quitter.se/api/statuses/show/2104527.atom" />
</entry>'''
entry3 = '''<?xml version="1.0" encoding="UTF-8"?>
<entry>
  <activity:object-type>http://activitystrea.ms/schema/1.0/comment</activity:object-type>
  <id>http://quitter.se/notice/2104525</id>
  <title>@mcscx well, (Twitter compatible) API is broken for the internal #quitter TL too since !crow uses that. i hope it\'s something temporary :)</title>
  <content type="html">@&lt;span class=&quot;vcard&quot;&gt;&lt;a href=&quot;http://quitter.se/user/113454&quot; class=&quot;url&quot; title=&quot;McScx&quot;&gt;&lt;span class=&quot;fn nickname mention&quot;&gt;mcscx&lt;/span&gt;&lt;/a&gt;&lt;/span&gt; well, (Twitter compatible) API is broken for the internal #&lt;span class=&quot;tag&quot;&gt;&lt;a href=&quot;http://quitter.se/tag/quitter&quot; rel=&quot;tag&quot;&gt;quitter&lt;/a&gt;&lt;/span&gt; TL too since !&lt;span class=&quot;vcard&quot;&gt;&lt;a href=&quot;http://quitter.se/group/1107/id&quot; class=&quot;url&quot; title=&quot;crow (crow)&quot;&gt;&lt;span class=&quot;fn nickname group&quot;&gt;crow&lt;/span&gt;&lt;/a&gt;&lt;/span&gt; uses that. i hope it\'s something temporary :)</content>
  <link rel="alternate" type="text/html" href="http://quitter.se/notice/2104525" />
  <activity:verb>http://activitystrea.ms/schema/1.0/post</activity:verb>
  <published>2013-08-11T08:49:23+00:00</published>
  <updated>2013-08-11T08:49:23+00:00</updated>
  <thr:in-reply-to ref="http://quitter.se/notice/2104517" href="http://quitter.se/notice/2104517" />
  <link rel="related" href="http://quitter.se/notice/2104517" />
  <link rel="ostatus:conversation" href="http://quitter.se/conversation/1898370" />
  <link rel="ostatus:attention" href="http://quitter.se/user/113454" />
  <link rel="mentioned" href="http://quitter.se/user/113454" />
  <link rel="ostatus:attention" href="http://quitter.se/group/1107/id" />
  <link rel="mentioned" href="http://quitter.se/group/1107/id" />
  <category term="quitter" />
  <link rel="self" type="application/atom+xml" href="http://quitter.se/api/statuses/show/2104525.atom" />
  <link rel="edit" type="application/atom+xml" href="http://quitter.se/api/statuses/show/2104525.atom" />
</entry>'''
feed1 = '''<?xml version="1.0" encoding="UTF-8"?>
<feed xml:lang="en-US" xmlns="http://www.w3.org/2005/Atom" xmlns:thr="http://purl.org/syndication/thread/1.0" xmlns:georss="http://www.georss.org/georss" xmlns:activity="http://activitystrea.ms/spec/1.0/" xmlns:media="http://purl.org/syndication/atommedia" xmlns:poco="http://portablecontacts.net/spec/1.0" xmlns:ostatus="http://ostatus.org/schema/1.0" xmlns:statusnet="http://status.net/schema/api/1/">
 <generator uri="http://status.net" version="1.1.0-release">StatusNet</generator>
 <id>http://quitter.se/api/statuses/user_timeline/114757.atom</id>
 <title>bijan timeline</title>
 <subtitle>Updates from bijan on Quitter!</subtitle>
 <logo>http://quitter.se/avatar/114757-96-20130710202211.png</logo>
 <updated>2013-08-11T15:43:47+02:00</updated> <link href="http://quitter.se/bijan" rel="alternate" type="text/html"/>
 <link href="http://quitter.se/main/sup" rel="http://api.friendfeed.com/2008/03#sup" type="application/json"/>
 <link href="http://quitter.se/main/push/hub" rel="hub"/>
 <link href="http://quitter.se/main/salmon/user/114757" rel="salmon"/>
 <link href="http://quitter.se/main/salmon/user/114757" rel="http://salmon-protocol.org/ns/salmon-replies"/>
 <link href="http://quitter.se/main/salmon/user/114757" rel="http://salmon-protocol.org/ns/salmon-mention"/>
 <link href="http://quitter.se/api/statuses/user_timeline/114757.atom" rel="self" type="application/atom+xml"/>
<author>
 <activity:object-type>http://activitystrea.ms/schema/1.0/person</activity:object-type>
 <uri>http://quitter.se/user/114757</uri>
 <name>bijan</name>
 <link rel="alternate" type="text/html" href="http://quitter.se/bijan"/>
 <link rel="avatar" type="image/png" media:width="170" media:height="170" href="http://quitter.se/avatar/114757-170-20130710202211.png"/>
 <link rel="avatar" type="image/png" media:width="96" media:height="96" href="http://quitter.se/avatar/114757-96-20130710202211.png"/>
 <link rel="avatar" type="image/png" media:width="48" media:height="48" href="http://quitter.se/avatar/114757-48-20130710202211.png"/>
 <link rel="avatar" type="image/png" media:width="24" media:height="24" href="http://quitter.se/avatar/114757-24-20130710202211.png"/>
 <poco:preferredUsername>bijan</poco:preferredUsername>
 <poco:displayName>bijan ebrahimi</poco:displayName>
 <poco:note>web developer and a FreeSoftware fan. developer of #crow and i surely love Linux so beware, i may bite ;)</poco:note>
 <poco:address>
  <poco:formatted>open web, Internet</poco:formatted>
 </poco:address>
 <poco:urls>
  <poco:type>homepage</poco:type>
  <poco:value>http://RoutinesExcluded.tk/</poco:value>
  <poco:primary>true</poco:primary>
 </poco:urls>
 <statusnet:profile_info local_id="114757"></statusnet:profile_info>
</author>
 <entry>
  <activity:object-type>http://activitystrea.ms/schema/1.0/comment</activity:object-type>
  <id>http://quitter.se/notice/2104592</id>
  <title>@alireza ساکت نیست. از صبح یه مشکلی داره سرورشون که درست دنت‌ها رو نشون نمیده. تقریبا فقط دنت‌های خودت رو اگه دقیق بخوام بگم :(</title>
  <content type="html">&lt;span class=&quot;rtl&quot;&gt;@&lt;span class=&quot;vcard&quot;&gt;&lt;a href=&quot;http://quitter.se/user/114767&quot; class=&quot;url&quot; title=&quot;Alireza Hokmabadi&quot;&gt;&lt;span class=&quot;fn nickname mention&quot;&gt;alireza&lt;/span&gt;&lt;/a&gt;&lt;/span&gt; ساکت نیست. از صبح یه مشکلی داره سرورشون که درست دنت‌ها رو نشون نمیده. تقریبا فقط دنت‌های خودت رو اگه دقیق بخوام بگم :(&lt;/span&gt;</content>
  <link rel="alternate" type="text/html" href="http://quitter.se/notice/2104592"/>
  <activity:verb>http://activitystrea.ms/schema/1.0/post</activity:verb>
  <published>2013-08-11T13:02:10+00:00</published>
  <updated>2013-08-11T13:02:10+00:00</updated>
  <thr:in-reply-to ref="http://quitter.se/notice/2104590" href="http://quitter.se/notice/2104590"></thr:in-reply-to>
  <link rel="related" href="http://quitter.se/notice/2104590"/>
  <link rel="ostatus:conversation" href="http://quitter.se/conversation/1898424"/>
  <link rel="ostatus:attention" href="http://quitter.se/user/114767"/>
  <link rel="mentioned" href="http://quitter.se/user/114767"/>
  <link rel="self" type="application/atom+xml" href="http://quitter.se/api/statuses/show/2104592.atom"/>
  <link rel="edit" type="application/atom+xml" href="http://quitter.se/api/statuses/show/2104592.atom"/>
 </entry>
 <entry>
  <activity:object-type>http://activitystrea.ms/schema/1.0/note</activity:object-type>
  <id>http://quitter.se/notice/2104591</id>
  <title>@alireza ساکت نیست. از صبح یه مشکلی داره سرورشون که درست دنت‌ها رو نشون نمیده. تقریبا فقط دنت‌های خودت رو اگه دقیق بخوام بگم :(</title>
  <content type="html">&lt;span class=&quot;rtl&quot;&gt;@&lt;span class=&quot;vcard&quot;&gt;&lt;a href=&quot;http://quitter.se/user/114767&quot; class=&quot;url&quot; title=&quot;Alireza Hokmabadi&quot;&gt;&lt;span class=&quot;fn nickname mention&quot;&gt;alireza&lt;/span&gt;&lt;/a&gt;&lt;/span&gt; ساکت نیست. از صبح یه مشکلی داره سرورشون که درست دنت‌ها رو نشون نمیده. تقریبا فقط دنت‌های خودت رو اگه دقیق بخوام بگم :(&lt;/span&gt;</content>
  <link rel="alternate" type="text/html" href="http://quitter.se/notice/2104591"/>
  <activity:verb>http://activitystrea.ms/schema/1.0/post</activity:verb>
  <published>2013-08-11T13:01:30+00:00</published>
  <updated>2013-08-11T13:01:30+00:00</updated>
  <link rel="ostatus:conversation" href="http://quitter.se/conversation/1898425"/>
  <link rel="ostatus:attention" href="http://quitter.se/user/114767"/>
  <link rel="mentioned" href="http://quitter.se/user/114767"/>
  <link rel="self" type="application/atom+xml" href="http://quitter.se/api/statuses/show/2104591.atom"/>
  <link rel="edit" type="application/atom+xml" href="http://quitter.se/api/statuses/show/2104591.atom"/>
 </entry>
 <entry>
  <activity:object-type>http://activitystrea.ms/schema/1.0/comment</activity:object-type>
  <id>http://quitter.se/notice/2104589</id>
  <title>@inscius normally that\'s not very much but for a person with computers skill? very impressive :) i\'m very proud. actually i envy you ;)</title>
  <content type="html">@&lt;span class=&quot;vcard&quot;&gt;&lt;a href=&quot;http://quitter.se/user/111931&quot; class=&quot;url&quot; title=&quot;Mikael&quot;&gt;&lt;span class=&quot;fn nickname mention&quot;&gt;inscius&lt;/span&gt;&lt;/a&gt;&lt;/span&gt; normally that\'s not very much but for a person with computers skill? very impressive :) i\'m very proud. actually i envy you ;)</content>
  <link rel="alternate" type="text/html" href="http://quitter.se/notice/2104589"/>
  <activity:verb>http://activitystrea.ms/schema/1.0/post</activity:verb>
  <published>2013-08-11T12:53:40+00:00</published>
  <updated>2013-08-11T12:53:40+00:00</updated>
  <thr:in-reply-to ref="http://quitter.se/notice/2104580" href="http://quitter.se/notice/2104580"></thr:in-reply-to>
  <link rel="related" href="http://quitter.se/notice/2104580"/>
  <link rel="ostatus:conversation" href="http://quitter.se/conversation/1898418"/>
  <link rel="ostatus:attention" href="http://quitter.se/user/111931"/>
  <link rel="mentioned" href="http://quitter.se/user/111931"/>
  <link rel="self" type="application/atom+xml" href="http://quitter.se/api/statuses/show/2104589.atom"/>
  <link rel="edit" type="application/atom+xml" href="http://quitter.se/api/statuses/show/2104589.atom"/>
 </entry>
</feed>'''
