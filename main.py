#!/usr/bin/env python
import os
import sys
from openpyxl import load_workbook
from allen_institute_structures import * 

REPORT_PATH = 'source/report.xlsx'
MAPPING_SHEET = 'JR_WorkingUberonMapping'
MOUSE_ARA_SHEET = 'Mouse_ARA'
HBA_SHEET = 'HBA'

def get_report_data():
	print('loading report.xlsx')
	book = load_workbook(REPORT_PATH, read_only=True, data_only=True)

			# check for existing sheet name
	if MAPPING_SHEET not in book.sheetnames:
		raise IndexError(REPORT_PATH + ' does not contain a ' + MAPPING_SHEET + ' sheet')

				# check for existing sheet name
	if MOUSE_ARA_SHEET not in book.sheetnames:
		raise IndexError(REPORT_PATH + ' does not contain a ' + MOUSE_ARA_SHEET + ' sheet')

				# check for existing sheet name
	if HBA_SHEET not in book.sheetnames:
		raise IndexError(REPORT_PATH + ' does not contain a ' + HBA_SHEET + ' sheet')

	return book[MAPPING_SHEET], book[MOUSE_ARA_SHEET], book[HBA_SHEET]
	

def main():
	#TODO load in uberon.owl data

	print("Running uberon cross-species mapping...")

	mapping_sheet, mouse_sheet, human_sheet = get_report_data()

	allen_institute_structures = AllenInstituteStructures(mapping_sheet, mouse_sheet, human_sheet)
	# allen_institute_structures.print_one_to_one_mappings()

	print('number of one to one mappings: ', allen_institute_structures.get_number_of_one_to_one_mappings())
	print('number of one to one leaf node mappings: ', allen_institute_structures.get_number_of_one_to_one_leaf_node_mappings())

	print('finished...')

if __name__ == "__main__":
	main()
