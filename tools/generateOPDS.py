#!/usr/bin/env python3
import sys
import os
import pathlib
import time
import datetime
import json
import pytz
from xml.dom import minidom
from dateutil import parser

os.environ['TZ'] = 'Europe/London'
time.tzset()

# check output with https://opds-validator.appspot.com/

def showUsage():
    print ('Usage: ' + sys.argv[0] + ' path/to/contents.opf path/to/epub.json')
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
    print(opffile)
    sys.exit(1)
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
    print("output: " + atom)
    sys.exit(1)
#    txt = os.path.basename(atom)
#    jomstring = txt.split(".")[0]
#    jomcatalogstring = "JoM"
#    if '-noitalics' in jomstring:
#        jomcatalogstring += '-noitalics'
    mydom = minidom.parseString('<entry/>')
    root = mydom.getElementsByTagName('entry')[0]
    # root.setAttribute('xml:lang', xmllang)
    root.setAttribute('xmlns', 'http://www.w3.org/2005/Atom')
    #root.setAttribute('xmlns:thr', 'http://purl.org/syndication/thread/1.0')
    root.setAttribute('xmlns:dc', 'http://purl.org/dc/terms/')
    #root.setAttribute('xmlns:opds', 'http://opds-spec.org/2010/catalog')
    #root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    #root.setAttribute('xmlns:schema', 'http://schema.org/')
    # get the OPF dom
    
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
    # get the UUID
    #try:
    #    opfuuid = opfdom.getElementsByTagNameNS('http://purl.org/dc/elements/1.1/', 'identifier')[0]
    #except:
    #    print ("Could not find the dc:identifier from OPF file.")
    #    sys.exit(1)
    #nodevalue = 'urn:uuid:' + opfuuid.firstChild.nodeValue
    stringlist = list('urn:uuid:bc955e92-abb4-4f8f-8929-839b7235a5ae')
    if "-noitalics" in jomstring:
        stringlist[28] = "9"
    string = ''.join(stringlist)
    text = mydom.createTextNode(string)
    node = mydom.createElement('id')
    node.appendChild(text)
    root.appendChild(node)
    # author
    text = mydom.createTextNode('American Society of Mammalogists')
    node = mydom.createElement('name')
    node.appendChild(text)
    author = mydom.createElement('author')
    author.appendChild(node)
    text = mydom.createTextNode('https://www.mammalogy.org/')
    node = mydom.createElement('uri')
    node.appendChild(text)
    author.appendChild(node)
    root.appendChild(author)
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
    for meta in metalist:
        if meta.hasAttribute('property') and meta.getAttribute('property') == 'dc:modified':
            nodevalue = meta.firstChild.nodeValue
            timestring = standardizeDateTime(nodevalue)
            text = mydom.createTextNode(timestring)
            node = mydom.createElement('updated')
            node.appendChild(text)
            root.appendChild(node)
            break
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
    #opffile = pathlib.Path(sys.argv[1])
    opffile = os.path.join(cwd, sys.argv[1])
    if not os.path.exists(opffile):
        showUsage()
    jsonfile = pathlib.Path(sys.argv[2])
    if not jsonfile.exists():
        showUsage()
    createEntry(cwd, jsonfile, opffile)

if __name__ == '__main__':
    main()