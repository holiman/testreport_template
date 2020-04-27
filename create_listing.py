#!/usr/bin/env python
import json
import sys

import os
from os.path import isfile, join

import argparse


def dumpjson(obj, fname):
    """ Dumps object to json"""
    #Print file
    with open(fname,"w+") as outfile:
        print("Writing %s" % fname)
        json.dump(obj, outfile)

def dumpjsonl(alist, fname):
    """ Dumps object to json"""
    #Print file
    with open(fname,"w+") as outfile:
        print("Writing %s" % fname)
        for elem in alist:
            json.dump(elem, outfile)
            outfile.write("\n")

# Read a json-lines file, returns a list
def readjsonl(fname):
    """ Dumps object to json"""
    #Print file
    alist = []
    try:
        with open(fname,"r+") as f:
            content = f.readlines()
            for line in content: 
                alist.append(json.loads(line))
    except IOError:
        pass

    return alist

def addAllToListing(artefact_dir, listingfile):
    """
    Regenerates listing-file and adds all files from artefact directory. 
    This method does not reprocess things already listed, so delete the listing
    if you want it regenerated
    """
    
    processed = {}    
    listings = readjsonl(listingfile)
    for oldfile in listings:
        processed[oldfile["fileName"]] = True


    # This will regenerate the listingfile
    files = [f for f in os.listdir(artefact_dir) if (isfile(join(artefact_dir, f)) and f[-4:] == "json")]

    for f in files:
        # If we already have it listed, don't process it again
        if f in processed:
            print("already processed, skipping "+f)
            continue


        file_summary = getSummary(artefact_dir, f)
        if file_summary is not None:
            listings.append(file_summary)

    listings.sort(key=lambda x: x["simLog"])
    # Only list 200 items
    dumpjsonl(listings[-200:], listingfile)

def getSummary(path, resultsfile):
    print("Processing %s" % resultsfile)
    
    path = join(path, resultsfile)

    with open(path,"r") as infile:
        sims = json.load(infile)
        summary = createSummaryFromJson(sims)
        if summary is None:
            print("summary failed on "+resultsfile+ ", skipping")
            return
        summary["size"] = os.path.getsize(path)
        summary["fileName"] = resultsfile
        return summary        

    print("Failed to open %s %s" % (path, resultsfile))
    return None

def createSummaryFromJson( obj ):

    summary ={}

    summary["description"] = obj["description"]
    summary["name"] = obj["name"]
    summary["simLog"] = obj["simLog"]
    summary["ntests"] = len(obj["testCases"].keys())
    cases = obj["testCases"]
    passes = 0
    fails = 0
    clients = set()
    startTime = ""
    for k,case in cases.items():
        
        k = case.keys()
        if startTime == "":
            startTime = case["start"]

        if case["summaryResult"]["pass"]:
            passes = passes+1
        else:
            fails = fails+1

        clientInfos = case["clientInfo"]
        for k, info in clientInfos.items():
            clients.add(info["name"])

    summary["passes"] = passes
    summary["fails"] = fails
    summary["clients"] = list(clients)
    summary["start"] = startTime
    if startTime == "":
        return None

    return summary

parser = argparse.ArgumentParser(description='Create a file listing from test results')
parser.add_argument('-l', action="store", dest="listingfile",required=True, help='Listing-file to regenerate')
parser.add_argument('-a', action="store", dest="artefact_dir",required=True, help='Artefact-dir, containing files')


if __name__ == '__main__':
    
    #For testing: 
    testing = True
    if testing:
        args = parser.parse_args(["-l","listing.jsonl","-a","./results"])
    else:
        args = parser.parse_args()
    addAllToListing(args.artefact_dir,args.listingfile)
    sys.exit(0)