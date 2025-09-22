import re
import os
import yaml
from a1facts.ontology.knowledge_ontology import KnowledgeOntology
from a1facts.ontology.rdfs_entity import RDFSEntity
from a1facts.ontology.rdfs_relationship import RDFSRelationship

def main():
    """
    Main function to run the RDFS parser.
    Handles file creation, reading, and passing content to the parser.
    """
    ontology_filename = "ontology.yaml"
    rdfs_filename = "example.rdfs"

    # --- File existence check and creation ---
    made_changes = False
    if not os.path.exists(ontology_filename):
        with open(ontology_filename, 'w') as f:
            f.write("# Please define your ontology here\n")
        made_changes = True

    if not os.path.exists(rdfs_filename):
        with open(rdfs_filename, 'w') as f:
            f.write("# Please provide your RDFS data here\n")
        made_changes = True

    if made_changes:
        print("Created dummy files: 'ontology.yaml' and/or 'example.rdfs'.")
        print("Please populate them with your content and re-run.")
        return

    # --- Read files and execute parser ---
    try:
        # 1. Load the ontology
        ontology = KnowledgeOntology(ontology_filename)

        with open(rdfs_filename, 'r') as f:
            rdfs_string = f.read()

        if not rdfs_string.strip():
            print("ERROR: Your RDFS file is empty.")
            print("Please populate it with content and re-run.")
            return
        
        # Call the parser with the file contents as strings
        entities, relationships = ontology.parse_rdfs_with_validation(rdfs_string)
        
        print("\n--- Parsed RDFSEntity Objects ---")
        for entity in entities:
            entity.print()
            
        print("\n--- Parsed RDFSRelationship Objects ---")
        for relationship in relationships:
            relationship.print()

    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"ERROR: Could not load or parse a required file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    main()
