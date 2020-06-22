#!/usr/bin/env python
import os
import sys
from openpyxl import load_workbook
from allen_institute_structures import *
from owlready2 import *
from sparql_queries import *

REPORT_PATH = 'source/report.xlsx'
MAPPING_PATH = 'source/one_to_one_mapping.xlsx'
OWL_PATH = 'source/uberon.owl'
MAPPING_SHEET = 'JR_WorkingUberonMapping'
MOUSE_ARA_SHEET = 'Mouse_ARA'
HBA_SHEET = 'HBA'
OUTPUT_PATH = 'source/bridge.json'
OWL_URI = "http://purl.obolibrary.org/obo/uberon/releases/2019-11-22"

def get_report_data():
	print('loading', MAPPING_PATH)
	mapping_book = load_workbook(MAPPING_PATH, read_only=True, data_only=True)

	print('loading', REPORT_PATH)
	book = load_workbook(REPORT_PATH, read_only=True, data_only=True)

	# check for existing sheet name
	if MAPPING_SHEET not in mapping_book.sheetnames:
		raise IndexError(MAPPING_PATH + ' does not contain a ' + MAPPING_SHEET + ' sheet')

	# check for existing sheet name
	if MOUSE_ARA_SHEET not in book.sheetnames:
		raise IndexError(REPORT_PATH + ' does not contain a ' + MOUSE_ARA_SHEET + ' sheet')

	# check for existing sheet name
	if HBA_SHEET not in book.sheetnames:
		raise IndexError(REPORT_PATH + ' does not contain a ' + HBA_SHEET + ' sheet')

	return mapping_book[MAPPING_SHEET], book[MOUSE_ARA_SHEET], book[HBA_SHEET]

def get_uberon_ontology():
	print('querying uberon ontology')
	sparql_query = SparqlQueries(OWL_PATH, OWL_URI)
	return sparql_query.search()

def main():
	print("Running uberon cross-species mapping...")
	#load in the uberon ontology
	uberon_ontology = get_uberon_ontology()

	#load in the spreadsheet mapping data
	mapping_sheet, mouse_sheet, human_sheet = get_report_data()

	allen_institute_structures = AllenInstituteStructures(mapping_sheet, mouse_sheet, human_sheet)
	# allen_institute_structures.print_one_to_one_mappings()

	allen_institute_structures.write_output_json(OUTPUT_PATH)

	# print('number of one to one mappings: ', allen_institute_structures.get_number_of_one_to_one_mappings())
	# print('number of one to one leaf node mappings: ', allen_institute_structures.get_number_of_one_to_one_leaf_node_mappings())

	print('finished...')

if __name__ == "__main__":
	main()
