import os
import sys
from allen_institute_structure import *

FIRST_ITEM = 0

class StructureGraph(object):
	

	def __init__(self, root, name):
		self.root = root
		self.name = name

		self.names_to_structures = self.hash_structure_names()
		self.ids_to_structures = self.hash_structure_ids()

	def hash_structure_names(self):
		queue = []
		queue.append(self.root)
		names_to_structures = {}

		#bfs
		while(len(queue) != 0):
			structure = queue.pop(FIRST_ITEM)

			#TODO - this should pass when the right 
			# if structure.name in names_to_structures:
				# raise Exception('Expected structure.name to be unique but found multiple ' + str(structure.name) + ' structures')

			names_to_structures[structure.name] = structure

			for child in structure.children:
				queue.append(child)

		return names_to_structures

	def hash_structure_ids(self):
		queue = []
		queue.append(self.root)
		ids_to_structures = {}

		#bfs
		while(len(queue) != 0):
			structure = queue.pop(FIRST_ITEM)

			structure_name = structure.id

			if structure.id in ids_to_structures:
				raise Exception('Expected structure.name to be unique but found multiple ' + str(structure.id) + ' structures')

			ids_to_structures[structure.id] = structure

			for child in structure.children:
				queue.append(child)

		return ids_to_structures

	def get_structure_by_id(self, id_value, atlas_name=None, row_number=None):
		if id_value not in self.ids_to_structures:

			if atlas_name is not None and row_number is not None:
				raise Exception('Expected id with ' + str(id_value) + ' to exist in the ' + str(self.name) + ' structure graph for the '+ str(atlas_name) + ' atlas but it does not, line: ' + str(row_number))
			else:
				raise Exception('Expected id with ' + str(id_value) + ' to exist in the ' + str(self.name) + ' structure graph but it does not')

		return self.ids_to_structures[id_value]
