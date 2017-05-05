#!/usr/bin/env python
import json
import sys
from os import listdir
from os.path import isfile, join

import argparse

parser = argparse.ArgumentParser(description='Create a file listing from test results')
parser.add_argument('-f', action="store", dest="artefact",help='specific artefact-file to add (omit to regenerate all)')
parser.add_argument('-l', action="store", dest="listingfile",required=True, help='Listing-file to regenerate')
parser.add_argument('-a', action="store", dest="artefact_dir",required=True, help='Artefact-dir, containing files')

def dumpjson(obj, fname):
	""" Dumps object to json"""
	#Print file
	with open(fname,"w+") as outfile:
		print("Writing %s" % fname)
		json.dump(obj, outfile)

def addAllToListing(artefact_dir, listingfile, filename = None):
	"""Regenerates listing-file and adds all files from artefact directory, 
	unless 'filename' has been specified (in which case only that is added, and 
	listing is not regenerated from scratch
	"""
	
	listings = {"files" : []}
	
	if filename is not None:
		#Don't regenerate, read existing 
		with open(listingfile,"r") as infile:
			listings = json.load(infile)

	# This will regenerate the listingfile
	files = [f for f in listdir(artefact_dir) if isfile(join(artefact_dir, f))]
	
	for f in files :
		if filename is not None and filename != join(artefact_dir, f):
			continue

		file_summary = getSummary(join(artefact_dir, f))
		if file_summary is not None:
			listings["files"].append(file_summary)

	dumpjson(listings, listingfile)

def getSummary(resultsfile):
	print("Opening %s" % resultsfile)

	with open(resultsfile,"r") as infile:
		sims = json.load(infile)
		sim_summary = createSummaryFromJson(sims)

		file_entry = { "filename" : resultsfile,
						"simulations" : sim_summary,
						"clients" : getClients(sims)}

		print "Returning %s" % file_entry
		return file_entry

	print("Failed to open %s" % resultsfile)
	return None

def getClients(resultobj):
	clients = {}
	if "clients" in resultobj.keys():
		clients = resultobj['clients']
	else:
		for client, data in sims.items():	
			clients[client] = {"branch": "", "commit" : "", "repo" : ""}
	return clients

def createSummaryFromJson( resultobj ):

	sims = resultobj['simulations']
	for client, data in sims.items():

		if "ethereum/consensus" not in data.keys():
			return
		subresults = data["ethereum/consensus"]["subresults"]
		s_len = len(subresults)

		success =0
		fail =0
		for s_result in subresults:
			if s_result['success']:
				success = success+1
			else:
				fail = fail +1

		data["ethereum/consensus"]["subresults"] = s_len
		data["ethereum/consensus"]["n_successes"] = success
		data["ethereum/consensus"]["n_fails"] = fail
	

	return sims


if __name__ == '__main__':
	
	#For testing: 
	#args = parser.parse_args(["-l","listing2.json","-a","test_artefacts"])
	#args = parser.parse_args(["-a","test_artefacts","-f","test_artefacts/20170308_151608-go-ethereum:master.json","-l","listing.json"])
	
	args = parser.parse_args()
	addAllToListing(args.artefact_dir,args.listingfile,args.artefact)
	sys.exit(0)