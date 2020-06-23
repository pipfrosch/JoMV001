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

def getCurrentTimestamp(xml):
    try:
        mydom = minidom.parse(xml)
    except:
        print (xml + " is not a valid XML file.")
        sys.exit(1)
    try:
        root = mydom.getElementsByTagName('package')[0]
    except:
        print ("Could not find root package node.")
        sys.exit(1)
    try:
        metadata = root.getElementsByTagName('metadata')[0]
    except:
        print ("Could not find metadata node.")
        sys.exit(1)
    metalist = metadata.getElementsByTagName('meta')
    for meta in metalist:
        if meta.hasAttribute("property") and meta.getAttribute("property") == "dcterms:modified":
            return meta.firstChild.nodeValue
    now = pytz.utc.localize(datetime.datetime.utcnow())
    return now.strftime("%Y-%m-%dT%H:%M:%SZ")

def getPubDate(xml):
    try:
        datenode = mydom.getElementsByTagNameNS('http://purl.org/dc/elements/1.1/', 'date')[0]
    except:
        now = pytz.utc.localize(datetime.datetime.utcnow())
        return now.strftime("%Y-%m-%d")
    return datenode.firstChild.nodeValue

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