#!/usr/bin/env python3
import sys
import os
import pathlib
import time
import datetime
import json
import pytz
import re
from xml.dom import minidom
from dateutil import parser

os.environ['TZ'] = 'Europe/London'
time.tzset()

# check output with https://opds-validator.appspot.com/

def showUsage():
    print ('Usage: ' + sys.argv[0] + ' path/to/contents.opf path/to/epub.json')
    sys.exit(1)

def validateNamespaces(dictionary, jsonfile):
    if type(dictionary) != dict:
        print('The namespaces key in ' + jsonfile + ' does not point to a valid dictionary.')
        sys.exit(1)
    keylist = dictionary.keys()
    pattern = re.compile(r'^[a-z]+$')
    uripattern = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    for ns in keylist:
        match = re.search(pattern, ns)
        if not match:
            print('Error in ' + jsonfile + ': A namespaces key should only contain lower case letters.')
            sys.exit(1)
        if len(ns) > 12:
            print('Error in ' + jsonfile + ': A namespaces key really should not be more than twelve characters in length.')
            sys.exit(1)
        uri = dictionary.get(ns)
        if type(uri) != str:
            print('Error in ' + jsonfile + ': The value associated with the namespaces key ' + ns + ' is not a string.')
            sys.exit(1)
        match = re.search(uripattern, uri)
        if not match:
            print('Error in ' + jsonfile + ': The value associated with the namespaces key ' + ns + ' is not a valid uri.')
            sys.exit(1)

# Pipfrosch Press only uses Version 4 UUID
def validateUUID(string, jsonfile):
    if type(string) != str:
        print('Error in ' + jsonfile + ': ' + string + ' is not a valid UUID urn string.')
        sys.exit(1)
    if len(string) != 45:
        print('Error in ' + jsonfile + ': ' + string + ' is not a valid UUID urn string.')
        sys.exit(1)
    header = string[0:9]
    if header != 'urn:uuid:':
        print('Error in ' + jsonfile + ': ' + string + ' is not a valid UUID urn string.')
        sys.exit(1)
    uuidstring = string[9:]
    pattern = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)
    match = re.search(pattern, uuidstring)
    if not match:
        print('Error in ' + jsonfile + ': ' + string + ' is not a valid UUID urn string.')
        sys.exit(1)
    uuidlist = list(uuidstring)
    if uuidlist[14] != '4':
        print('Error in ' + jsonfile + ': ' + uuidstring + ' is not a valid Version 4 UUID.')
        sys.exit(1)
    if uuidlist[19] != '8':
        print('Error in ' + jsonfile + ': ' + 'first character of fourth block in ' + uuidstring + ' is not 8')
        sys.exit(1)

def validateAuthors(authors, jsonfile):
    if type(authors) != list:
        print('Error in ' + jsonfile + ': The authors key in ' + jsonfile + ' does not point to a valid list.')
        sys.exit(1)
    for author in authors:
        if type(author) != dict:
            print('Error in ' + jsonfile + ': Some author entries in ' + jsonfile + ' are not dictionaries.')
            sys.exit(1)
        keys = author.keys()
        if 'name' not in author:
            print('Error in ' + jsonfile + ': Some author entries in ' + jsonfile + ' do not have a name key.')
            sys.exit(1)
        for key in keys:
            if type(author.get(key)) != str:
                print('Error in ' + jsonfile + ': Some author keys in ' + jsonfile + ' do not have string values.')
                sys.exit(1)

def standardizeDateTime(string):
    dto = parser.parse(string)
    return dto.strftime('%Y-%m-%dT%H:%M:%SZ')

#def createEntry(atom, xml):
def createEntry(cwd, jsonfile, opffile):
    try:
        with open(jsonfile) as f:
            jsondata = json.load(f)
    except:
        print(jsonfile + ' does not appear to be valid JSON.')
        sys.exit(1)
    jsonkeys = jsondata.keys()
    try:
        opfdom = minidom.parse(opffile)
    except:
        print (opffile + ' is not a valid OPF file.')
        sys.exit(1)
    try:
        opfroot = opfdom.getElementsByTagName('package')[0]
    except:
        print ('Could not find root package node in ' + opffile)
        sys.exit(1)
    try:
        metadata = opfroot.getElementsByTagName('metadata')[0]
    except:
        print ('Could not find metadata node in ' + opffile)
        sys.exit(1)
    if 'output' not in jsonkeys:
        print(jsonfile + ' does not specify proper output file.')
        sys.exit(1)
    if type(jsondata.get('output')) != str:
        print('Value for output key in ' + jsonfile + ' is not a string.')
        sys.exit(1)
    string = jsondata.get('output')
    atom = os.path.join(cwd, string)
    if 'opdspath' not in jsonkeys:
        print(jsonfile + ' does not specify proper opdspath.')
        sys.exit(1)
    if type(jsondata.get('opdspath')) != str:
        print('Value for opdspath key in ' + jsonfile + ' is not a string.')
        sys.exit(1)
    opdspath = jsondata.get('opdspath')
    mydom = minidom.parseString('<entry/>')
    root = mydom.getElementsByTagName('entry')[0]
    root.setAttribute('xmlns', 'http://www.w3.org/2005/Atom')
    if 'namespaces' in jsonkeys:
        namespaces = jsondata.get('namespaces')
        validateNamespaces(namespaces, jsonfile)
        nskeys = namespaces.keys()
        for ns in nskeys:
            root.setAttribute('xmlns:' + ns, namespaces.get(ns))
    # get the title
    try:
        opftitle = opfdom.getElementsByTagNameNS('http://purl.org/dc/elements/1.1/', 'title')[0]
    except:
        print ('Could not extract title from OPF file.')
        sys.exit(1)
    nodevalue = opftitle.firstChild.nodeValue
    text = mydom.createTextNode(nodevalue)
    node = mydom.createElement('title')
    node.appendChild(text)
    root.appendChild(node)
    if 'id' not in jsonkeys:
        print(jsonfile + ' does not specify id.')
        sys.exit(1)
    validateUUID(jsondata.get('id'), jsonfile)
    stringlist = list(jsondata.get('id'))
    if '-noitalics' in opdspath:
        # indicate noitalics by changing first hex of fourth group to 9
        stringlist[28] = '9'
    string = ''.join(stringlist)
    text = mydom.createTextNode(string)
    node = mydom.createElement('id')
    node.appendChild(text)
    root.appendChild(node)
    # author
    if 'authors' not in jsonkeys:
        print(jsonfile + ' does not specify author(s).')
        sys.exit(1)
    authors = jsondata.get('authors')
    validateAuthors(authors, jsonfile)
    for author in authors:
        authornode = mydom.createElement('author')
        string = author.get('name')
        text = mydom.createTextNode(string)
        name = mydom.createElement('name')
        name.appendChild(text)
        authornode.appendChild(name)
        if 'uri' in author.keys():
            string = author.get('uri')
            text = mydom.createTextNode(string)
            uri = mydom.createElement('uri')
            uri.appendChild(text)
            authornode.appendChild(uri)
        root.appendChild(authornode)
    # published date
    try:
        datenode = opfdom.getElementsByTagNameNS('http://purl.org/dc/elements/1.1/', 'date')[0]
    except:
        print ('Could not find the dc:date from OPF file.')
        sys.exit(1)
    nodevalue = datenode.firstChild.nodeValue
    timestring = standardizeDateTime(nodevalue)
    text = mydom.createTextNode(timestring)
    node = mydom.createElement('published')
    node.appendChild(text)
    root.appendChild(node)
    # modified date
    metalist = metadata.getElementsByTagName('meta')
    found = False
    for meta in metalist:
        if meta.hasAttribute('property') and meta.getAttribute('property') == 'dc:mmodified':
            nodevalue = meta.firstChild.nodeValue
            timestring = standardizeDateTime(nodevalue)
            text = mydom.createTextNode(timestring)
            node = mydom.createElement('updated')
            node.appendChild(text)
            root.appendChild(node)
            found = True
            break
    if not found:
        print ('Could not find the dc:modified meta tag in ' + opffile)
        sys.exit(1)
    # get language
    try:
        language = opfdom.getElementsByTagNameNS('http://purl.org/dc/elements/1.1/', 'language')[0]
    except:
        print ('Could not find the dc:language from OPF file.')
        sys.exit(1)
    nodevalue = language.firstChild.nodeValue
    text = mydom.createTextNode(nodevalue)
    node = mydom.createElement('dc:language')
    node.appendChild(text)
    root.appendChild(node)
    # get the UUID
    try:
        opfuuid = opfdom.getElementsByTagNameNS('http://purl.org/dc/elements/1.1/', 'identifier')[0]
    except:
        print ('Could not find the dc:identifier from OPF file.')
        sys.exit(1)
    nodevalue = opfuuid.firstChild.nodeValue
    text = mydom.createTextNode(nodevalue)
    node = mydom.createElement('dc:identifier')
    node.appendChild(text)
    root.appendChild(node)
    # get publisher
    try:
        publisher = opfdom.getElementsByTagNameNS('http://purl.org/dc/elements/1.1/', 'publisher')[0]
    except:
        print ('Could not find the dc:publisher from OPF file.')
        sys.exit(1)
    nodevalue = publisher.firstChild.nodeValue
    text = mydom.createTextNode(nodevalue)
    node = mydom.createElement('dc:publisher')
    node.appendChild(text)
    root.appendChild(node)
    # originally issued
    text = mydom.createTextNode('1919–1920')
    node = mydom.createElement('dc:issued')
    node.appendChild(text)
    root.appendChild(node)
    # create summary
    try:
        description = opfdom.getElementsByTagNameNS('http://purl.org/dc/elements/1.1/', 'description')[0]
    except:
        print ('Could not find dc:description from OPF file.')
        sys.exit(1)
    nodevalue = description.firstChild.nodeValue
    text = mydom.createTextNode(nodevalue)
    node = mydom.createElement('summary')
    node.appendChild(text)
    root.appendChild(node)
    # TODO Category
    # Alternate View
    node = mydom.createElement('link')
    node.setAttribute('type', 'text/html')
    node.setAttribute('rel', 'alternate')
    node.setAttribute('title', 'View at Pipfrosch Press')
    node.setAttribute('href', 'https://pipfrosch.com/jom-volume-1-preview-1/')
    root.appendChild(node)
    # image
    node = mydom.createElement('link')
    node.setAttribute('type', 'image/jpeg')
    node.setAttribute('rel', 'http://opds-spec.org/image')
    node.setAttribute('href', '/JoM/JoM-V001.cover.jpg')
    root.appendChild(node)
    node = mydom.createElement('link')
    node.setAttribute('type', 'image/jpeg')
    node.setAttribute('rel', 'http://opds-spec.org/image/thumbnail')
    node.setAttribute('href', '/JoM/JoM-V001.thumbnail.jpg')
    root.appendChild(node)
    # acquisition links
    #
    node = mydom.createElement('link')
    node.setAttribute('type', 'application/atom+xml;type=entry;profile=opds-catalog')
    node.setAttribute('rel', 'self')
    node.setAttribute('href', '/JoM/' + jomstring + '.atom')
    root.appendChild(node)
    node = mydom.createElement('link')
    node.setAttribute('type', 'application/epub+zip')
    node.setAttribute('rel', 'http://opds-spec.org/acquisition')
    node.setAttribute('href', 'https://epub.pipfrosch.com/JoM/' + jomstring + '.kepub.epub')
    root.appendChild(node)
    node = mydom.createElement('link')
    node.setAttribute('type', 'application/atom+xml;profile=opds-catalog;kind=acquisition')
    node.setAttribute('rel', 'http://www.feedbooks.com/opds/same_author')
    node.setAttribute('title', 'More offering from Journal of Mammalogy')
    node.setAttribute('href', '/JoM/' + jomcatalogstring + '.atom')
    root.appendChild(node)
    # dump to file
    string = mydom.toprettyxml(indent='  ',newl='\n',encoding='UTF-8').decode()
    string = '\n'.join([x for x in string.split('\n') if x.strip()!=''])
    fh = open(atom, 'w')
    fh.write(string)
    fh.close()

def main():
    if len(sys.argv) != 3:
        showUsage()
    cwd = os.getcwd()
    opffile = os.path.join(cwd, sys.argv[1])
    if not os.path.exists(opffile):
        showUsage()
    jsonfile = os.path.join(cwd, sys.argv[2])
    if not os.path.exists(jsonfile):
        showUsage()
    createEntry(cwd, jsonfile, opffile)

if __name__ == '__main__':
    main()