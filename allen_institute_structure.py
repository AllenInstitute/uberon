import os
import sys

class AllenInstituteStructure(object):
	def __init__(self, id_value, atlas_id, ontology_id, acronym, name, color_hex_triplet, graph_order, st_level, hemisphere_id, parent_structure_id, parent):
		self.id = id_value
		self.atlas_id = atlas_id
		self.ontology_id = ontology_id
		self.acronym = acronym
		self.name = name
		self.color_hex_triplet = color_hex_triplet
		self.graph_order = graph_order
		self.st_level = st_level
		self.hemisphere_id = hemisphere_id
		self.parent_structure_id = parent_structure_id
		self.children = []
		self.parent = parent

		self.mapping_row_number = None
		self.superclass_name_linked = None
		self.atlas_name = None
		self.analysis = None

		if parent is not None:
			parent.add_child_structure(self)

	def add_mapping_info(self, mapping_row_number, superclass_name_linked, atlas_name, analysis):
		self.mapping_row_number = mapping_row_number
		self.superclass_name_linked = superclass_name_linked
		self.atlas_name = atlas_name
		self.analysis = analysis

	def add_child_structure(self, structure):
		self.children.append(structure)

	def is_leaf_node(self):
		return len(self.children) == 0

	def is_root(self):
		return (self.parent == None)

	def is_ok(self):
		return self.analysis == 'OK'