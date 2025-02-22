import re
from datetime import datetime
from pathlib import Path

"""
This script provides a class, `GedcomParser`, to parse GEDCOM (Genealogical Data Communication) files.
GEDCOM is a standard file format for exchanging genealogical data between different genealogy software.

The script extracts information about individuals and families from a GEDCOM file and transforms
it into a structured format suitable for creating a knowledge graph.  The knowledge graph consists of
entities (people) and relations (family connections like marriage and parent-child).

Key Features:
- Parses GEDCOM files to extract individuals (INDI) and families (FAM) records.
- Extracts relevant information for individuals, such as name, birth date (BIRT), and death date (DEAT).
- Identifies family relationships, including husband (HUSB), wife (WIFE), and children (CHIL).
- Formats the extracted data into a list of entities and relations, making it easy to
  represent the genealogical data in a knowledge graph.
- Handles basic GEDCOM date formats.

Usage:
1.  Create an instance of the `GedcomParser` class.
2.  Call the `parse_file(file_path)` method, passing the path to the GEDCOM file as an argument.
    This method reads the file, parses its contents, and returns two lists:
    - entities: A list of dictionaries, where each dictionary represents a person with their attributes.
    - relations: A list of dictionaries, where each dictionary represents a relationship between two people.

Example:
    entities, relations = process_gedcom_file("path/to/your/gedcom_file.ged")
    # Now you can use the 'entities' and 'relations' lists to build your knowledge graph.

GEDCOM File Structure:
GEDCOM files are line-based and use a specific syntax.  Each line starts with a level number,
followed by a tag that indicates the type of information on that line.  For example:

0 @I1@ INDI  ; Individual record
1 NAME John /Doe/
2 GIVN John
2 SURN Doe
1 BIRT
2 DATE 1 JAN 1980
0 @F1@ FAM   ; Family record
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I3@

The parser is designed to handle this structure and extract the relevant information.

Author: Shiverme Timbers - reddit.com/u/sushibait - sushibait@okbuddy.lol
Version: 1.3
Last Updated: 22 FEB 2025
License: MIT - Do what you want.

"""

class GedcomParser:
    def __init__(self):
        """
        Initializes the GedcomParser with empty dictionaries to store individuals and families,
        and sets the current entity and tag to None.
        """
        self.individuals = {}
        self.families = {}
        self.current_entity = None
        self.current_tag = None

    def parse_file(self, file_path):
        """
        Parses a GEDCOM file and extracts family relationships.

        Args:
            file_path (str): The path to the GEDCOM file.

        Returns:
            tuple: A tuple containing two lists:
                - entities: A list of dictionaries representing individuals.
                - relations: A list of dictionaries representing family relationships.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                self.parse_line(line.strip())
        return self.format_knowledge()

    def parse_line(self, line):
        """
        Parses a single GEDCOM line.

        Args:
            line (str): A string representing a single line from the GEDCOM file.
        """
        parts = line.split(' ', 2)
        level = int(parts<source_id data="0" title="gedcom-to-knowledge-graph.py" />)
        if len(parts) < 2:
            return

        # Handle INDI and FAM records
        if level == 0:
            if 'INDI' in line:
                id = parts[1].replace('@', '')
                self.current_entity = {'id': id, 'type': 'INDI'}
                self.individuals[id] = self.current_entity
            elif 'FAM' in line:
                id = parts[1].replace('@', '')
                self.current_entity = {'id': id, 'type': 'FAM'}
                self.families[id] = self.current_entity
            else:
                self.current_entity = None

        # Handle individual details
        elif self.current_entity and self.current_entity['type'] == 'INDI':
            if level == 1:
                self.current_tag = parts[1]
                if len(parts) > 2:
                    self.current_entity[self.current_tag] = parts[2]
            elif level == 2 and self.current_tag:
                if self.current_tag not in self.current_entity:
                    self.current_entity[self.current_tag] = {}
                self.current_entity[self.current_tag][parts[1]] = parts[2] if len(parts) > 2 else ''

        # Handle family relationships
        elif self.current_entity and self.current_entity['type'] == 'FAM':
            if level == 1:
                tag = parts[1]
                if len(parts) > 2:
                    value = parts[2].replace('@', '')
                    if tag in ['HUSB', 'WIFE']:
                        self.current_entity[tag] = value
                    elif tag == 'CHIL':
                        if 'CHIL' not in self.current_entity:
                            self.current_entity['CHIL'] = []
                        self.current_entity['CHIL'].append(value)

    def format_knowledge(self):
        """
        Formats the parsed data into knowledge graph statements (entities and relations).

        Returns:
            tuple: A tuple containing two lists:
                - entities: A list of dictionaries representing individuals.
                - relations: A list of dictionaries representing family relationships.
        """
        entities = []
        relations = []

        # Create person entities
        for person_id, person in self.individuals.items():
            name = person.get('NAME', f"Unknown_{person_id}")
            birth_date = self._extract_date(person.get('BIRT', {}))
            death_date = self._extract_date(person.get('DEAT', {}))

            observations = [
                f"Name: {name}",
                f"Birth date: {birth_date}" if birth_date else None,
                f"Death date: {death_date}" if death_date else None
            ]

            entities.append({
                "name": f"Person_{person_id}",
                "entityType": "Person",
                "observations": [obs for obs in observations if obs]
            })

        # Create family relationships
        for family in self.families.values():
            if 'HUSB' in family and 'WIFE' in family:
                relations.append({
                    "from": f"Person_{family['HUSB']}",
                    "to": f"Person_{family['WIFE']}",
                    "relationType": "married_to"
                })

            for child in family.get('CHIL', []):
                if 'HUSB' in family:
                    relations.append({
                        "from": f"Person_{family['HUSB']}",
                        "to": f"Person_{child}",
                        "relationType": "parent_of"
                    })
                if 'WIFE' in family:
                    relations.append({
                        "from": f"Person_{family['WIFE']}",
                        "to": f"Person_{child}",
                        "relationType": "parent_of"
                    })

        return entities, relations

    def _extract_date(self, date_dict):
        """
        Extracts date from GEDCOM date dictionary.

        Args:
            date_dict (dict): A dictionary containing date information from the GEDCOM file.

        Returns:
            str: The date string if found, otherwise None.
        """
        if 'DATE' in date_dict:
            return date_dict['DATE']
        return None


def process_gedcom_file(file_path):
    """
    Processes a single GEDCOM file and returns knowledge graph data.

    Args:
        file_path (str): The path to the GEDCOM file.

    Returns:
        tuple: A tuple containing two lists:
            - entities: A list of dictionaries representing individuals.
            - relations: A list of dictionaries representing family relationships.
    """
    parser = GedcomParser()
    return parser.parse_file(file_path)