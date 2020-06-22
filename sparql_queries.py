#!/usr/bin/env python
import os
import sys
from owlready2 import *
import json

class SparqlQueries:
	def __init__(self, owl_path, owrl_uri):
		world = World()
		world.get_ontology(owl_path).load()
		# sync_reasoner(world)
		self.graph = world.as_rdflib_graph()
		self.owrl_uri = owrl_uri

	def search(self):
		#Search query is given here

		query = "base <" + str(self.owrl_uri) + "> " \
			"SELECT ?s ?p ?o " \
			"WHERE { " \
			"?s ?p ?o . " \
			"}"

		#query is being run
		resultsList = self.graph.query(query)

		#creating json object
		response = []
		for item in resultsList:
			s = str(item['s'].toPython())
			s = re.sub(r'.*#',"",s)

			p = str(item['p'].toPython())
			p = re.sub(r'.*#', "", p)

			o = str(item['o'].toPython())
			o = re.sub(r'.*#', "", o)
			response.append({'s' : s, 'p' : p, "o" : o})

		# print(response) #just to show the output
		
		output_file = 'source/test_out.json'

		print('Writing', output_file)

		with open(output_file, 'w') as outfile:
			json.dump(response, outfile, indent=2)

		return response