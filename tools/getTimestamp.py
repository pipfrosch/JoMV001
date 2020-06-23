#!/usr/bin/env python3
import sys
import os
import pathlib
import datetime
import pytz
from xml.dom import minidom

def showUsage():
    print ("Usage: " + sys.argv[0] + " path/to/contents.opf")
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

def main():
    if len(sys.argv) != 2:
        showUsage()
    opf = pathlib.Path(sys.argv[1])
    if not opf.exists():
        showUsage()
    rn = getCurrentTimestamp(sys.argv[1])
    print (rn)

if __name__ == "__main__":
    main()