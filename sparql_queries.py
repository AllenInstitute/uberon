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

	def full_search(self):
		#Search query is given here

		query = "PREFIX base: <" + str(self.owrl_uri) + "> " \
			"SELECT ?s ?p ?o " \
			"WHERE { " \
			"?s ?p ?o . " \
			"}"

		print('query', query)

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

			# print('p', p)

			# if(p =='label' or s == 'label' or o == 'label'):
			if(p =='label'):
				t = {'s' : s, 'p' : p, "o" : o}
				print('*************')
				print('item', item)
				print('hot dod', t)

			response.append({'s' : s, 'p' : p, "o" : o})

		# print(response) #just to show the output
		
		output_file = 'source/test_out.json'

		print('Writing', output_file)

		with open(output_file, 'w') as outfile:
			json.dump(response, outfile, indent=2)

		return response

	def search_label(self, object_value):
		#Search query is given here

		# query = "base <" + str(self.owrl_uri) + "> " \
		# 	"SELECT ?p " \
		# 	"WHERE { " \
		# 	"?p label " + str(object_value) + " " \
		# 	"}"

		# query = "prefix base: <" + str(self.owrl_uri) + "> " \
		# 	"SELECT ?p " \
		# 	"WHERE { " \
		# 	"?p base:label '" + str(object_value) + "' ." \
		# 	"}"

		# query = "prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> " \
		# 	" base <" + str(self.owrl_uri) + "> " \
		# 	"SELECT ?p ?n " \
		# 	"WHERE { " \
		# 	"?p rdfs:label '" + str(object_value) + "' ." \
		# 	"}"

		query = "prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> " \
			" base <" + str(self.owrl_uri) + "> " \
			"SELECT ?s ?p ?o " \
			"WHERE { " \
			"?s rdfs:label '" + str(object_value) + "' . " \
			"?s ?p ?o ." \
			"}"


		# print('query', query)

		# #query is being run
		resultsList = self.graph.query(query)

		# print('len(resultsList)', len(resultsList))

		#creating json object
		response = []
		for item in resultsList:
			# print('item', item)
			s = str(item['s'].toPython())
			s = re.sub(r'.*#',"",s)

			p = str(item['p'].toPython())
			p = re.sub(r'.*#', "", p)

			o = str(item['o'].toPython())
			o = re.sub(r'.*#', "", o)
			# response.append({'p' : p})
			response.append({'subject' : s, 'predicate' : p, "object" : o})

		query = "prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> " \
			" base <" + str(self.owrl_uri) + "> " \
			"SELECT ?s ?p ?o " \
			"WHERE { " \
			"?o rdfs:label '" + str(object_value) + "' . " \
			"?s ?p ?o ." \
			"}"


		# print('query', query)

		# #query is being run
		resultsList = self.graph.query(query)

		# print('len(resultsList)', len(resultsList))

		#creating json object
		for item in resultsList:
			# print('item', item)
			s = str(item['s'].toPython())
			s = re.sub(r'.*#',"",s)

			p = str(item['p'].toPython())
			p = re.sub(r'.*#', "", p)

			o = str(item['o'].toPython())
			o = re.sub(r'.*#', "", o)
			# response.append({'p' : p})
			response.append({'subject' : s, 'predicate' : p, "object" : o})

		# print('response', response) #just to show the output
		
		# output_file = 'source/test2_out.json'

		# print('Writing', output_file)

		# with open(output_file, 'w') as outfile:
		# 	json.dump(response, outfile, indent=2)

		return response