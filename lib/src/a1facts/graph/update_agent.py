from a1facts.ontology.knowledge_ontology import KnowledgeOntology
from a1facts.utils.modelconfig import my_high_precision_model
from agno.agent import Agent
from textwrap import dedent
from datetime import datetime
from a1facts.utils.logger import logger
from colored import cprint
from pydantic import BaseModel, Field
import re
import yaml
from datetime import datetime
import os


class RDFSResult(BaseModel):
    rdfs: str = Field(description="The RDFS format of the knowledge. Only include entities, relationships and their properties that are in the ontology.")
    other_information: str = Field(description="Other information that isn't in the ontology. Ideally this is empty, but if you have other info that is not in the ontology, included it here verbatim.")


class UpdateAgent:
    def __init__(self, ontology: KnowledgeOntology, mytools: list):
        self.ontology = ontology
        self.rdfs_agent = Agent(
            name="RDFS Agent",
            role="Translate the knowledge into a structured format based on the ontology.",
            model=my_high_precision_model,
            instructions=dedent(f"""
                Translate the knowledge into a structured format based on the ontology.
                Ontology:[{self.ontology}]
                Return the results in RDFS format. Include both entities and relationships.
                NEVER use a format different from the ontology.
                NEVER make up information, only use the information provided to you. DO NOT use your own knowledge to make up information.
                Ideally, every RDFS entity should have sources.
                Today is {datetime.now().strftime("%Y-%m-%d")}
            """),
            markdown=True,
            debug_mode=False,
            output_schema=RDFSResult,
        )
        self.update_agent = Agent(
            name="Knowledge Graph Update Agent",
            role="Update the knowledge graph",
            model=my_high_precision_model,
            tools=mytools,

            instructions=dedent(f"""
                The user is providing you RDFS format of the knowledge. 
                Add every entity and relationship to the graph using the tools available to you.
                First add the entities, then add the relationships.
                Make sure to add every single one of them.
                Today is {datetime.now().strftime("%Y-%m-%d")}
            """),
            markdown=True,
            debug_mode=False,
            input_schema=RDFSResult,
            )

    def update(self, knowledge: str):
        #step 0 - translate the knowledge into rdfs format
        #step 1 - deduplicate the knowledge using spacy; add alises to entities and relatioinships
        #step 2 - add the knowledge to the graph using the tools available to you
        logger.system(f"Updating knowledge graph with knowledge: {knowledge}")
        rdfs_result = self.rdfs_agent.run("Translate the following knowledge into a structured format based on the ontology\n\n " + knowledge)
        cprint(rdfs_result.content.rdfs, 'red')
        cprint(rdfs_result.content.other_information, 'yellow')
        exit()
        logger.system(f"RDFS result: {rdfs_result.content.rdfs + "\nToday is " + datetime.now().strftime("%Y-%m-%d")}")
        logger.system(f"RDFS not in ontology: {rdfs_result.content.other_information}")
        return self.update_agent.run(rdfs_result.content.rdfs + "\nToday is " + datetime.now().strftime("%Y-%m-%d"))


def check_type(value: str, expected_type: str) -> bool:
    """Validates if a string value can be cast to the expected type."""
    if expected_type == 'str':
        return True
    if expected_type == 'float':
        try:
            float(value)
            return True
        except ValueError:
            return False
    if expected_type == 'int':
        try:
            int(value)
            return True
        except ValueError:
            return False
    if expected_type == 'bool':
        return value.lower() in ['true', 'false']
    if expected_type == 'date':
        try:
            # Matches YYYY-MM-DD format
            datetime.fromisoformat(value)
            return True
        except (ValueError, TypeError):
            return False
    return False

def _handle_entity_definition(subject, rest_of_line, properties, ontology, success_messages, error_messages, block_index):
    is_valid = True
    entity_class_name = rest_of_line.strip(':')
    entity_class = ontology.find_entity_class(entity_class_name)

    if not entity_class:
        error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: Entity class '{entity_class_name}' not found in ontology for entity '{subject}'.")
        is_valid = False
    else:
        defined_props = {p.property_name: p for p in entity_class.properties}
        for prop, value in properties.items():
            if prop not in defined_props:
                error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: In entity '{subject}', property '{prop}' is not defined for class '{entity_class_name}'.")
                is_valid = False
            elif not check_type(value, defined_props[prop].type):
                error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: In entity '{subject}', property '{prop}' has wrong type. Expected '{defined_props[prop].type}' but value was '{value}'.")
                is_valid = False
    
    if is_valid:
        properties['type'] = entity_class_name
        success_messages.append(f"Block {block_index+1}: (adding entity: {subject} with properties: {properties})")

def _handle_relationship_definition(subject, predicate, rest_of_line, properties, ontology, entity_types, success_messages, error_messages, block_index):
    is_valid = True
    objects = [obj.strip().strip(':') for obj in rest_of_line.split(',')]
    
    relationship_class = next((rc for rc in ontology.relationship_classes if rc.relationship_name == predicate), None)

    if not relationship_class:
        error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: Relationship '{predicate}' not found in ontology.")
        is_valid = False
    else:
        defined_props = {p.property_name: p for p in relationship_class.properties}
        for prop, value in properties.items():
            if prop not in defined_props:
                error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: In relationship '{subject}->{predicate}', property '{prop}' is not defined.")
                is_valid = False
            elif not check_type(value, defined_props[prop].type):
                error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: In relationship '{subject}->{predicate}', property '{prop}' has wrong type. Expected '{defined_props[prop].type}' but value was '{value}'.")
                is_valid = False
        
        # Validate domain and range for each object
        for obj in objects:
            subject_type = entity_types.get(subject)
            object_type = entity_types.get(obj)
            if not subject_type:
                error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: Subject entity '{subject}' was never defined with a type.")
                is_valid = False
            elif subject_type != relationship_class.domain_entity_class:
                error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: For relationship '{predicate}', subject '{subject}' of type '{subject_type}' does not match expected domain '{relationship_class.domain_entity_class}'.")
                is_valid = False
            
            if not object_type:
                error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: Object entity '{obj}' was never defined with a type.")
                is_valid = False
            elif object_type != relationship_class.range_entity_class:
                 error_messages.append(f"Block {block_index+1}: VALIDATION ERROR: For relationship '{predicate}', object '{obj}' of type '{object_type}' does not match expected range '{relationship_class.range_entity_class}'.")
                 is_valid = False
    
    if is_valid:
        for obj in objects:
            if properties:
                success_messages.append(f"Block {block_index+1}: (adding relationship {subject} -> {predicate} -> {obj} with properties: {properties})")
            else:
                success_messages.append(f"Block {block_index+1}: (adding relationship {subject} -> {predicate} -> {obj})")

def parse_rdfs_with_validation(rdfs_content: str, ontology_filename: str):
    """
    Parses and validates an RDFS string against a given ontology.
    
    Args:
        rdfs_content: A string containing the RDFS data.
        ontology_filename: The path to the YAML file defining the ontology.
    """
    # 1. Load and preprocess the ontology from the YAML string
    try:
        ontology = KnowledgeOntology(ontology_filename)
    except (yaml.YAMLError, FileNotFoundError) as e:
        print(f"ERROR: Could not load or parse ontology file: {e}")
        return

    # 2. Pre-processing: Clean RDFS content
    rdfs_content = re.sub(r'#.*', '', rdfs_content)
    rdfs_content = rdfs_content.replace(u'\xa0', ' ')
    blocks = rdfs_content.strip().split('.\n')

    # 3. First Pass: Map all declared entities to their types
    entity_types = {}
    for block_text in blocks:
        # Process each line of the block to find entity declarations
        for line in block_text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # The regex now specifically looks for the ' a ' keyword to identify a type declaration
            match = re.match(r'^:([^\s]+)\s+a\s+:([^\s;]+)', line)
            if match:
                subject = match.group(1)
                entity_class = match.group(2).strip()
                entity_types[subject] = entity_class
                break  # Found the type declaration for this block

    # 4. Second Pass: Parse, validate, and print
    success_messages = []
    error_messages = []
    for i, block_text in enumerate(blocks):
        block_text = block_text.strip()
        if not block_text or block_text.startswith('@prefix'):
            continue
        
        lines = [line.strip() for line in block_text.split('\n') if line.strip()]
        if not lines: continue

        match = re.match(r'(:[^\s]+)\s+(:[^\s]+|a)\s+(.*)', lines[0])
        if not match: continue

        subject = match.group(1).strip(':')
        predicate = match.group(2).strip(':')
        rest_of_line = match.group(3).rstrip(';').strip()
        
        properties = {}
        for line in lines[1:]:
            prop_match = re.match(r'(:[^\s]+)\s+(.*)', line)
            if prop_match:
                key = prop_match.group(1).strip(':')
                value = prop_match.group(2).rstrip(';').strip()
                if '^^' in value: value = value.split('^^')[0]
                value = value.strip('"')
                properties[key] = value

        # --- Validation Logic ---
        if predicate == 'a':
            _handle_entity_definition(subject, rest_of_line, properties, ontology, success_messages, error_messages, i)
        else:
            _handle_relationship_definition(subject, predicate, rest_of_line, properties, ontology, entity_types, success_messages, error_messages, i)

    print("\n--- ✅ Successful Operations ---")
    for msg in success_messages:
        print(msg)

    if error_messages:
        print("\n--- ❌ Validation Errors ---")
        for msg in error_messages:
            print(msg)
    print("\n--- Parsing and Validation Complete ---")


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
        with open(ontology_filename, 'r') as f:
            ontology_string = f.read()

        with open(rdfs_filename, 'r') as f:
            rdfs_string = f.read()

        if not ontology_string.strip() or not rdfs_string.strip():
            print("ERROR: One or both of your files are empty.")
            print("Please populate them with content and re-run.")
            return
        
        # Call the parser with the file contents as strings
        parse_rdfs_with_validation(
            rdfs_content=rdfs_string,
            ontology_filename=ontology_filename
        )

    except FileNotFoundError as e:
        print(f"ERROR: Could not find a required file: {e.filename}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    main()