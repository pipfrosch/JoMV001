#!/usr/bin/env python3
import sys
import os
import pathlib
import datetime
import pytz
from xml.dom import minidom

def showUsage():
    print ("Usage: " + sys.argv[0] + " path/to/contents.opf path/to/entry.atom")
    sys.exit(1)

def createEntry(atom, xml):
    mydom = minidom.parseString('<entry/>')
    root = mydom.getElementsByTagName('entry')[0]
    # root.setAttribute('xml:lang', xmllang)
    root.setAttribute('xmlns', 'http://www.w3.org/2005/Atom')
    root.setAttribute('xmlns:thr', 'http://purl.org/syndication/thread/1.0')
    root.setAttribute('xmlns:dcterms', 'http://purl.org/dc/terms/')
    root.setAttribute('xmlns:opds', 'http://opds-spec.org/2010/catalog')
    root.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.setAttribute('xmlns:schema', 'http://schema.org/')
    # get the OPF dom
    try:
        opfdom = minidom.parse(xml)
    except:
        print (xml + " is not a valid XML file.")
        sys.exit(1)
    try:
        opfroot = opfdom.getElementsByTagName('package')[0]
    except:
        print ("Could not find root package node.")
        sys.exit(1)
    try:
        metadata = opfroot.getElementsByTagName('metadata')[0]
    except:
        print ("Could not find metadata node.")
        sys.exit(1)
    # get the title
    try:
        opftitle = opfdom.getElementsByTagNameNS('http://purl.org/dc/elements/1.1/', 'title')[0]
    except:
        print ("Could not extract title from OPF file.")
        sys.exit(1)
    nodevalue = opftitle.firstChild.nodeValue
    text = mydom.createTextNode(nodevalue)
    node = mydom.createElement('title')
    node.appendChild(text)
    root.appendChild(node)
    # get the UUID
    try:
        opfuuid = opfdom.getElementsByTagNameNS('http://purl.org/dc/elements/1.1/', 'identifier')[0]
    except:
        print ("Could not find the dc:identifier from OPF file.")
        sys.exit(1)
    nodevalue = 'urn:uuid:' + opfuuid.firstChild.nodeValue
    text = mydom.createTextNode(nodevalue)
    node = mydom.createElement('id')
    node.appendChild(text)
    root.appendChild(node)
    # author
    text = mydom.createTextNode('American Society of Mammalogists')
    node = mydom.createElement('name')
    node.appendChild(text)
    author = mydom.createElement('author')
    author.appendChild(node)
    root.appendChild(author)
    # published date
    try:
        datenode = opfdom.getElementsByTagNameNS('http://purl.org/dc/elements/1.1/', 'date')[0]
    except:
        print ("Could not find the dc:date from OPF file.")
        sys.exit(1)
    nodevalue = datenode.firstChild.nodeValue
    text = mydom.createTextNode(nodevalue)
    node = mydom.createElement('published')
    node.appendChild(text)
    root.appendChild(node)
    # modified date
    metalist = metadata.getElementsByTagName('meta')
    for meta in metalist:
        if meta.hasAttribute("property") and meta.getAttribute("property") == "dcterms:modified":
            nodevalue = meta.firstChild.nodeValue
            text = mydom.createTextNode(nodevalue)
            node = mydom.createElement('updated')
            node.appendChild(text)
            root.appendChild(node)
            break
    # get language
    try:
        language = opfdom.getElementsByTagNameNS('http://purl.org/dc/elements/1.1/', 'language')[0]
    except:
        print ("Could not find the dc:language from OPF file.")
        sys.exit(1)
    nodevalue = language.firstChild.nodeValue
    text = mydom.createTextNode(nodevalue)
    node = mydom.createElement('dcterms:language')
    node.appendChild(text)
    root.appendChild(node)
    # get publisher
    try:
        publisher = opfdom.getElementsByTagNameNS('http://purl.org/dc/elements/1.1/', 'publisher')[0]
    except:
        print ("Could not find the dc:publisher from OPF file.")
        sys.exit(1)
    nodevalue = publisher.firstChild.nodeValue
    text = mydom.createTextNode(nodevalue)
    node = mydom.createElement('dcterms:publisher')
    node.appendChild(text)
    root.appendChild(node)
    # originally issued
    text = mydom.createTextNode("1919–1920")
    node = mydom.createElement('dcterms:issued')
    node.appendChild(text)
    root.appendChild(node)
    # create summary
    try:
        description = opfdom.getElementsByTagNameNS('http://purl.org/dc/elements/1.1/', 'description')[0]
    except:
        print ("Could not find dc:description from OPF file.")
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
    node.setAttribute('href', 'https://pipfrosch.com/TODOWHENFINISHED')
    root.appendChild(node)
    # image
    node = mydom.createElement('link')
    node.setAttribute('type', 'image/jpeg')
    node.setAttribute('rel', 'http://opds-spec.org/image')
    node.setAttribute('href', 'https://opds.pipfrosch.com/JoM/JoM-V001.cover.jpg')
    root.appendChild(node)
    node = mydom.createElement('link')
    node.setAttribute('type', 'image/jpeg')
    node.setAttribute('rel', 'http://opds-spec.org/image/thumbnail')
    node.setAttribute('href', 'https://opds.pipfrosch.com/JoM/JoM-V001.thumbnail.jpg')
    root.appendChild(node)
    # dump to file
    string = mydom.toprettyxml(indent="  ",newl="\n",encoding="UTF-8").decode()
    string = '\n'.join([x for x in string.split("\n") if x.strip()!=''])
    fh = open(atom, "w")
    fh.write(string)
    fh.close()
    #if not xmllang == booklang:
    #    print ('Warning: The xml:lang ' + xmllang + ' differs from the book lang ' + booklang)
    #    print ('This might be okay but could be accidental.')

def main():
    if len(sys.argv) != 3:
        showUsage()
    opf = pathlib.Path(sys.argv[1])
    if not opf.exists():
        showUsage()
    createEntry(sys.argv[2], sys.argv[1])

if __name__ == "__main__":
    main()