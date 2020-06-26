import os
import sys
from openpyxl import load_workbook
from structure_graph import *
from allen_institute_structure import *
import time
import json

ID_INDEX = 1
ACRONYM_INDEX = 2
HEMISPHERE_INDEX = 3
RED_INDEX = 4
GREEN_INDEX = 5
BLUE_INDEX = 6
ST_LEVEL_INDEX = 7
ST_ORDER_INDEX = 8
STRUCTURES_INDEX = 9
ROWS_TO_SKIP = 1
FIRST_STRUCTURE = 0


JR_ANALYSIS_INDEX = 1
SUPERCLASS_NAME_LINKED_INDEX = 5
ATLAS_NAME_INDEX = 10
MAPPING_STRUCTURE_INDEX = 11

MOUSE_ATLAS_NAME = 'Mouse_ARA'
HUMAN_ATLAS_NAME = 'Human_BrainSpan'

class AllenInstituteStructures(object):

	def __init__(self, mapping_sheet, mouse_ontology, human_ontology):
		self.mapping_sheet = mapping_sheet
		self.mouse_ontology = mouse_ontology
		self.human_ontology = human_ontology

		#build the graph
		self.mouse_structure_graph = self.create_structure_graph(self.mouse_ontology, 'Mouse')
		self.human_structure_graph = self.create_structure_graph(self.human_ontology, 'Human')

		#map the structures
		self.one_to_one_mappings, self.leaf_node_mappings, self.mouse_atlas_structures, self.hba_atlas_structures = self.get_one_to_one_mappings(self.mouse_structure_graph, self.human_structure_graph, self.mapping_sheet)


	def print_one_to_one_mappings(self):
		print('one to one mappings:')
		for name in self.one_to_one_mappings:
			print(name)

	def get_number_of_one_to_one_mappings(self):
		return len(self.one_to_one_mappings)

	def get_number_of_one_to_one_leaf_node_mappings(self):
		return len(self.leaf_node_mappings)


	def get_structure_offset(self, row):
		offset = 0
		value = row[STRUCTURES_INDEX + offset].value

		while not value:
			offset+=1
			value = row[STRUCTURES_INDEX + offset].value

		return value, offset

	def create_structure_graph(self, ontology, graph_name):
		print('create_structure_graph', graph_name)
		msg = ontology['msg']
		root_structure = msg[FIRST_STRUCTURE]

		parents = {}

		queue = []
		queue.append(root_structure)


		root = None

		#bfs
		while len(queue) != 0:
			current_structure = queue.pop(FIRST_STRUCTURE)

			id_value = current_structure['id']
			atlas_id = current_structure['atlas_id']
			ontology_id = current_structure['ontology_id']
			acronym = current_structure['acronym']
			name = current_structure['name']
			color_hex_triplet = current_structure['color_hex_triplet']
			graph_order = current_structure['graph_order']
			st_level = current_structure['st_level']
			hemisphere_id = current_structure['hemisphere_id']
			parent_structure_id = current_structure['parent_structure_id']
			children = current_structure['children']

			parent = None

			#look up parent
			if parent_structure_id is not None:
				parent = parents[parent_structure_id]

			#create the structure
			structure = AllenInstituteStructure(id_value, atlas_id, ontology_id, acronym, name, color_hex_triplet, graph_order, st_level, hemisphere_id, parent_structure_id, parent)

			#set the root node if needed
			if root == None:
				root = structure

			parents[id_value] = structure


			for child in children:
				queue.append(child)

		return StructureGraph(root, graph_name)

	def get_one_to_one_mappings(self, mouse_structure_graph, human_structure_graph, mapping_sheet):

		mappings = []
		leaf_node_mappings = []

		mouse_atlas_structures = {}
		human_atlas_structures = {}
		superclass_name_linked_names = {}
		row_number = 1
		for row in mapping_sheet.iter_rows():
			atlas_name = row[ATLAS_NAME_INDEX].value
			structure_id = row[MAPPING_STRUCTURE_INDEX].value
			superclass_name_linked = row[SUPERCLASS_NAME_LINKED_INDEX].value
			analysis = row[JR_ANALYSIS_INDEX].value

			if type(structure_id) == int:
				if atlas_name == MOUSE_ATLAS_NAME:
					structure = mouse_structure_graph.get_structure_by_id(structure_id, atlas_name, row_number)
					structure.add_mapping_info(row_number, superclass_name_linked, atlas_name, analysis)

					mouse_atlas_structures[superclass_name_linked] = structure
					superclass_name_linked_names[superclass_name_linked] = True

				elif atlas_name == HUMAN_ATLAS_NAME:
					structure = human_structure_graph.get_structure_by_id(structure_id, atlas_name, row_number)
					human_atlas_structures[superclass_name_linked] = structure
					superclass_name_linked_names[superclass_name_linked] = True
					structure.add_mapping_info(row_number, superclass_name_linked, atlas_name, analysis)

			row_number+=1

			# print(atlas_name, structure_id)
			# time.sleep(1)

		for superclass_name_linked_name in list(superclass_name_linked_names.keys()):
			# print('unique_name', unique_name)
			# if superclass_name_linked_name in mouse_atlas_structures and superclass_name_linked_name in human_atlas_structures and mouse_atlas_structures[superclass_name_linked_name].is_ok() and human_atlas_structures[superclass_name_linked_name].is_ok():
			if superclass_name_linked_name in mouse_atlas_structures and superclass_name_linked_name in human_atlas_structures:
				mappings.append(superclass_name_linked_name)

				if mouse_atlas_structures[superclass_name_linked_name].is_leaf_node() and human_atlas_structures[superclass_name_linked_name].is_leaf_node():
					leaf_node_mappings.append(superclass_name_linked_name)

		return mappings, leaf_node_mappings, mouse_atlas_structures, human_atlas_structures

	def get_structure_info(self, structure):
		structure_info = {}
		structure_info['structure_id'] = structure.id
		structure_info['acronym'] = structure.acronym
		structure_info['name'] = structure.name
		structure_info['jr_analysis'] = structure.analysis
		structure_info['atlas_name'] = structure.atlas_name
		structure_info['mapping_xlsx_row_number'] = structure.mapping_row_number
		structure_info['is_leaf_node'] = structure.is_leaf_node()

		return structure_info

	def write_output_json(self, output_file, sparql_query):
		data = {}
		data['number_of_one_to_one_mappings'] = self.get_number_of_one_to_one_mappings()
		# data['number_of_one_to_one_leaf_node_mappings'] = self.get_number_of_one_to_one_leaf_node_mappings()

		structures = []

		for superclass_name_linked_name in self.one_to_one_mappings:
			structure_data = {}
			mouse_atlas_structure = self.mouse_atlas_structures[superclass_name_linked_name]
			hba_atlas_structure = self.hba_atlas_structures[superclass_name_linked_name]
			structure_data['superclass_name_linked'] = superclass_name_linked_name
			structure_data['are_both_leaf_nodes'] = (mouse_atlas_structure.is_leaf_node() and hba_atlas_structure.is_leaf_node())

			structure_data['mouse_data'] = self.get_structure_info(mouse_atlas_structure)
			structure_data['human_data'] = self.get_structure_info(hba_atlas_structure)

			uberon_data = {}
			records = sparql_query.search_label(superclass_name_linked_name)

			id_value = None
			label = None

			for record in records:
				if record['predicate'] == 'id':
					id_value = record['object']

				elif record['predicate'] == 'label':
					label = record['object']


			uberon_data['id'] = id_value
			uberon_data['label'] = label 
			uberon_data['records'] = records

			structure_data['uberon_data'] = uberon_data

			structures.append(structure_data)
		
		data['structures'] = structures

		print('Writing', output_file)

		with open(output_file, 'w') as outfile:
			json.dump(data, outfile, indent=2)