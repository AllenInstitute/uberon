import os
import sys

class AllenInstituteStructure(object):
	def __init__(self, id, acronym, name, hemisphere, red, green, blue, st_level, st_order, parent, row_number = None):
		self.id = int(id)
		self.acronym = str(acronym).strip()
		self.name = str(name).strip()
		self.hemisphere = hemisphere
		self.red = red
		self.green = green
		self.blue = blue
		self.st_level = st_level
		self.st_order = st_order
		self.children = []
		self.parent = parent
		self.row_number = row_number

		if parent is not None:
			parent.add_child_structure(self)

	def add_child_structure(self, structure):
		self.children.append(structure)

	def is_leaf_node(self):
		return len(self.children) == 0

	def is_root(self):
		return (self.parent == None)