import os
import sys
from openpyxl import load_workbook
from structure_graph import *
from allen_institute_structure import *
import time
import json
import networkx
import networkx as nx
import matplotlib.pyplot as plt
# from networkx.drawing.nx_agraph import graphviz_layout
from pygraphviz import *

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
		self.one_to_one_mappings, self.leaf_node_mappings, self.mouse_atlas_structures, self.human_atlas_structures = self.get_one_to_one_mappings(self.mouse_structure_graph, self.human_structure_graph, self.mapping_sheet)


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

	def get_mapped_structures(self, sparql_query):
		mapped_structures = []


		for superclass_name_linked_name in self.one_to_one_mappings:
			structure_data = {}
			mouse_atlas_structure = self.mouse_atlas_structures[superclass_name_linked_name]
			hba_atlas_structure = self.human_atlas_structures[superclass_name_linked_name]
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

			mapped_structures.append(structure_data)

		return mapped_structures

	def get_missing_structures(self):

		#get all of the unmapped structures
		mouse_root = self.mouse_structure_graph.root
		human_root = self.human_structure_graph.root

		missing_mouse_structures = self.find_missing_structures(mouse_root)
		missing_human_structures = self.find_missing_structures(human_root)


		missing_structures = {}
		missing_mouse = {}
		missing_mouse['number_of_missing'] = len(missing_mouse_structures)
		missing_mouse['missing'] = missing_mouse_structures

		missing_human = {}
		missing_human['number_of_missing'] = len(missing_human_structures)
		missing_human['missing'] = missing_human_structures
		
		missing_structures['missing_mouse'] = missing_mouse
		missing_structures['missing_human'] = missing_human

		return missing_structures

	def write_output_json(self, output_file, sparql_query):
		data = {}
		data['number_of_one_to_one_mappings'] = self.get_number_of_one_to_one_mappings()
		data['number_of_one_to_one_leaf_node_mappings'] = self.get_number_of_one_to_one_leaf_node_mappings()

		#get the missing and mapped structures
		missing_structures = self.get_missing_structures()
		mapped_structures = self.get_mapped_structures(sparql_query)

		data['missing_structures'] = missing_structures
		data['mapped_structures'] = mapped_structures

		print('Writing', output_file)

		with open(output_file, 'w') as outfile:
			json.dump(data, outfile, indent=2)

	def find_missing_structures(self, root_structure):
		missing_structures = []

		self.one_to_one_mappings

		queue = []
		queue.append(root_structure)


		#bfs
		while len(queue) != 0:
			structure = queue.pop(FIRST_STRUCTURE)
			if structure.is_missing_superclass_name_linked():
				structure_data = {}
				structure_data['id'] = structure.id
				structure_data['name'] = structure.name
				structure_data['acronym'] = structure.acronym

				missing_structures.append(structure_data)

			for child in structure.children:
				queue.append(child)

		return missing_structures

	def get_mouse_id(self, structure):
		return 'mouse_' + str(structure.id) + '_' + str(structure.acronym)

	def get_human_id(self, structure):
		return 'human_' + str(structure.id) + '_' + str(structure.acronym)

	def add_nodes(self, graph, root_structure, graph_type):
		queue = []
		queue.append(root_structure)

		#bfs
		while len(queue) != 0:
			structure = queue.pop(FIRST_STRUCTURE)
			# color = 'red'
			color = '#' + str(structure.color_hex_triplet)
			fillcolor = 'red'

			if graph_type == 'mouse':
				graph.add_node(self.get_mouse_id(structure), color=color, style='filled', fillcolor=fillcolor)
			elif graph_type == 'human':
				graph.add_node(self.get_human_id(structure), color=color, style='filled', fillcolor=fillcolor)
			else:
				raise Exception('graph_type ' + str(graph_type) + ' is not valid')

			# graph.add_node(structure.id, color='red')

			for child in structure.children:
				queue.append(child)

	def add_edges(self, graph, root_structure, graph_type):
		queue = []
		queue.append(root_structure)

		#bfs
		while len(queue) != 0:
			structure = queue.pop(FIRST_STRUCTURE)
			if(structure.parent is not None):
				if graph_type == 'mouse':
					graph.add_edge(self.get_mouse_id(structure.parent), self.get_mouse_id(structure))
				elif graph_type == 'human':
					graph.add_edge(self.get_human_id(structure.parent), self.get_human_id(structure))
				else:
					raise Exception('graph_type ' + str(graph_type) + ' is not valid')

			for child in structure.children:
				queue.append(child)

	#add in all of the nodes and tree edges
	def create_graph(self, graph, root_structure, graph_type):
		self.add_nodes(graph, root_structure, graph_type)
		self.add_edges(graph, root_structure, graph_type)

	def add_cross_species_links(self, graph, mouse_graph, human_graph):
		fillcolor = 'green'

		#loop through all structures with 1 to 1 mappings
		for superclass_name_linked_name in self.one_to_one_mappings:
			mouse_atlas_structure = self.mouse_atlas_structures[superclass_name_linked_name]
			hba_atlas_structure = self.human_atlas_structures[superclass_name_linked_name]

			# label = superclass_name_linked_name
			label = superclass_name_linked_name + ' (' + str(mouse_atlas_structure.analysis) + ',' + str(hba_atlas_structure.analysis) + ')'

			#set edge beteen them
			graph.add_edge(self.get_mouse_id(mouse_atlas_structure), self.get_human_id(hba_atlas_structure), label=label, color='green')

			#color those nodes green
			mouse_node = graph.get_node(self.get_mouse_id(mouse_atlas_structure))
			mouse_node.attr['fillcolor'] = fillcolor

			human_node = graph.get_node(self.get_human_id(hba_atlas_structure))
			human_node.attr['fillcolor'] = fillcolor


			other_mouse_node = mouse_graph.get_node(self.get_mouse_id(mouse_atlas_structure))
			other_mouse_node.attr['fillcolor'] = fillcolor

			other_human_node = human_graph.get_node(self.get_human_id(hba_atlas_structure))
			other_human_node.attr['fillcolor'] = fillcolor


	def write_output_graph(self, output_file, mouse_output_file, human_output_file):
		# g = nx.Graph()
		# g = nx.DiGraph()
		graph = AGraph()
		mouse_graph = AGraph()
		human_graph = AGraph()

		#get the roots
		mouse_root = self.mouse_structure_graph.root
		human_root = self.human_structure_graph.root

		#add the mouse structures
		self.create_graph(graph, mouse_root, 'mouse')
		self.create_graph(mouse_graph, mouse_root, 'mouse')

		#add the human structures
		self.create_graph(graph, human_root, 'human')
		self.create_graph(human_graph, human_root, 'human')

		#add the links across species
		self.add_cross_species_links(graph, mouse_graph, human_graph)
	
		#set the layouts
		graph.layout('dot', args='-Nfontsize=10 -Nwidth=".2" -Nheight=".2" -Nmargin=0 -Gfontsize=8')
		mouse_graph.layout('dot', args='-Nfontsize=10 -Nwidth=".2" -Nheight=".2" -Nmargin=0 -Gfontsize=8')
		human_graph.layout('dot', args='-Nfontsize=10 -Nwidth=".2" -Nheight=".2" -Nmargin=0 -Gfontsize=8')

		#write the files
		print('Writing', output_file)
		graph.draw(output_file)

		print('Writing', mouse_output_file)
		mouse_graph.draw(mouse_output_file)

		print('Writing', human_output_file)
		human_graph.draw(human_output_file)