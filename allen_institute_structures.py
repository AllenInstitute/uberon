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


SUPERCLASS_NAME_LINKED_INDEX = 5
ATLAS_NAME_INDEX = 10
MAPPING_STRUCTURE_INDEX = 11

MOUSE_ATLAS_NAME = 'Mouse_ARA'
HBA_ATLAS_NAME = 'HBA'

class AllenInstituteStructures(object):

	def __init__(self, mapping_sheet, mouse_sheet, human_sheet):
		self.mapping_sheet = mapping_sheet
		self.mouse_sheet = mouse_sheet
		self.human_sheet = human_sheet

		self.mouse_structure_graph = self.create_structure_graph(self.mouse_sheet, 'Mouse')
		self.human_structure_graph = self.create_structure_graph(self.human_sheet, 'Human')

		self.one_to_one_mappings, self.leaf_node_mappings, self.mouse_atlas_structures, self.hba_atlas_structures = self.get_one_to_one_mappings(self.mouse_structure_graph, self.human_structure_graph, self.mapping_sheet)


	def print_one_to_one_mappings(self):
		print('one to one mappings:')
		for name in self.one_to_one_mappings:
			print(name)

	def get_number_of_one_to_one_mappings(self):
		return len(self.one_to_one_mappings)

	def get_number_of_one_to_one_leaf_node_mappings(self):
		return len(self.leaf_node_mappings)


	def validate_presence(self, value_name, value, row_number, name):
		# print('value_name', value_name, 'value', value, 'row_number', row_number)

		if not value:
			raise Exception('Expected ' + str(value_name) + ' on row ' + str(row_number) + ' for sheet ' + str(name) + ' to contain a value but it did not')


	def validate_int_type(self, value_name, value, row_number, name):
		if type(value) != int:
			raise Exception('Expected ' + str(value_name) + ' on row ' + str(row_number) + ' for sheet ' + str(name) + ' to be of type int but it was ' + str(type(value)))

	def validate_string_type(self, value_name, value, row_number, name):
		if type(value) != str:
			raise Exception('Expected ' + str(value_name) + ' on row ' + str(row_number) + ' for sheet ' + str(name) + ' to be of type string but it was ' + str(type(value)))


	def get_structure_offset(self, row):
		offset = 0
		value = row[STRUCTURES_INDEX + offset].value

		while not value:
			offset+=1
			value = row[STRUCTURES_INDEX + offset].value

		return value, offset


	def get_parent_structure(self, parent_offset, previous_parent_offset, previous_structure, previous_parent_structure):
		#default
		offset_diff = parent_offset - previous_parent_offset
		parent_structure = None

		if offset_diff > 0:
			parent_structure = previous_structure
		else:
			parent_structure = previous_parent_structure

			#if previous_structure is None then we are at the root node
			while offset_diff != 0:
				parent_structure = parent_structure.parent
				offset_diff+=1


		return parent_structure


	def create_structure_graph(self, sheet, graph_name):
		
		row_number = 1
		previous_structure = None
		previous_parent_structure = None
		previous_parent_offset = 0

		root = None

		for row in sheet.iter_rows():
			if ROWS_TO_SKIP < row_number:
				id_value = row[ID_INDEX].value
				acronym = row[ACRONYM_INDEX].value
				hemisphere = row[HEMISPHERE_INDEX].value
				red = row[RED_INDEX].value
				green = row[GREEN_INDEX].value
				blue = row[BLUE_INDEX].value
				st_level = row[ST_LEVEL_INDEX].value
				st_order = row[ST_ORDER_INDEX].value
				structures = row[STRUCTURES_INDEX].value

				name, parent_offset = self.get_structure_offset(row)

				self.validate_presence('id', id_value, row_number, graph_name)
				self.validate_presence('acronym', acronym, row_number, graph_name)
				self.validate_presence('structure', name, row_number, graph_name)

				acronym = str(acronym)

				self.validate_int_type('id', id_value, row_number, graph_name)
				self.validate_string_type('acronym', acronym, row_number, graph_name)
				self.validate_string_type('structure', name, row_number, graph_name)

				# print("********************")
				# print(row_number, name, parent_offset)

				# time.sleep(1)
				

				parent_structure = self.get_parent_structure(parent_offset, previous_parent_offset, previous_structure, previous_parent_structure)

				# if parent_structure:
				# 	print(row_number, name, ' - ', parent_structure.name)
				# else:
				# 	print(row_number, name, ' - ', 'none')

				# time.sleep(1)

				allen_institute_structure = AllenInstituteStructure(id_value, acronym, name, hemisphere, red, green, blue, st_level, st_order, parent_structure, row_number)

				if root is None:
					root = allen_institute_structure
				

				previous_parent_offset = parent_offset
				previous_structure = allen_institute_structure
				previous_parent_structure = parent_structure

			row_number+=1

		return StructureGraph(root, graph_name)

	def get_one_to_one_mappings(self, mouse_structure_graph, human_structure_graph, mapping_sheet):
		MOUSE_ATLAS_NAME = 'Mouse_ARA'
		HBA_ATLAS_NAME = 'HBA'

		mappings = []
		leaf_node_mappings = []

		mouse_atlas_structures = {}
		hba_atlas_structures = {}
		superclass_name_linked_names = {}
		row_number = 1
		for row in mapping_sheet.iter_rows():
			atlas_name = row[ATLAS_NAME_INDEX].value
			structure_id = row[MAPPING_STRUCTURE_INDEX].value
			superclass_name_linked = row[SUPERCLASS_NAME_LINKED_INDEX].value

			if type(structure_id) == int:
				if atlas_name == MOUSE_ATLAS_NAME:
					structure = mouse_structure_graph.get_structure_by_id(structure_id, atlas_name, row_number)
					structure.add_mapping_info(row_number, superclass_name_linked, atlas_name)

					mouse_atlas_structures[superclass_name_linked] = structure
					superclass_name_linked_names[superclass_name_linked] = True

				elif atlas_name == HBA_ATLAS_NAME:
					structure = human_structure_graph.get_structure_by_id(structure_id, atlas_name, row_number)
					hba_atlas_structures[superclass_name_linked] = structure
					superclass_name_linked_names[superclass_name_linked] = True
					structure.add_mapping_info(row_number, superclass_name_linked, atlas_name)

			row_number+=1

			# print(atlas_name, structure_id)
			# time.sleep(1)

		for superclass_name_linked_name in list(superclass_name_linked_names.keys()):
			# print('unique_name', unique_name)
			if superclass_name_linked_name in mouse_atlas_structures and superclass_name_linked_name in hba_atlas_structures:
				mappings.append(superclass_name_linked_name)

				if mouse_atlas_structures[superclass_name_linked_name].is_leaf_node() and hba_atlas_structures[superclass_name_linked_name].is_leaf_node():
					leaf_node_mappings.append(superclass_name_linked_name)

		return mappings, leaf_node_mappings, mouse_atlas_structures, hba_atlas_structures

	def get_structure_info(self, structure):
		structure_info = {}
		structure_info['structure_id'] = structure.id
		structure_info['acronym'] = structure.acronym
		structure_info['name'] = structure.name
		structure_info['atlas_name'] = structure.atlas_name
		structure_info['mapping_xlsx_row_number'] = structure.mapping_row_number
		structure_info['is_leaf_node'] = structure.is_leaf_node()

		return structure_info

	def write_output_json(self, output_file):
		data = {}
		data['number_of_one_to_one_mappings'] = self.get_number_of_one_to_one_mappings()
		data['number_of_one_to_one_leaf_node_mappings'] = self.get_number_of_one_to_one_leaf_node_mappings()

		structures = []

		for superclass_name_linked_name in self.one_to_one_mappings:
			structure_data = {}
			mouse_atlas_structure = self.mouse_atlas_structures[superclass_name_linked_name]
			hba_atlas_structure = self.hba_atlas_structures[superclass_name_linked_name]
			structure_data['superclass_name_linked_name'] = superclass_name_linked_name
			structure_data['are_both_leaf_nodes'] = (mouse_atlas_structure.is_leaf_node() and hba_atlas_structure.is_leaf_node())

			structure_data['mouse_data_data'] = self.get_structure_info(mouse_atlas_structure)
			structure_data['human_data_data'] = self.get_structure_info(hba_atlas_structure)

			structures.append(structure_data)
		
		data['structures'] = structures

		print('Writing', output_file)

		with open(output_file, 'w') as outfile:
			json.dump(data, outfile, indent=2)