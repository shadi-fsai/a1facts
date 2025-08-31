import yaml
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

def read_ontology(file_path):
    with open(file_path, 'r') as f:
        ontology = yaml.load(f, Loader=yaml.FullLoader)
    
    print("="*40)
    print("ENTITY CLASSES (NODES)")
    print("="*40)
    for name, details in ontology.get('entity_classes', {}).items():
        print(f"Entity: {name}")
        print(f"  Description: {details.get('description', 'N/A')}")
        print("  Properties:")
        for prop in details.get('properties', []):
            prop_name = prop.get('name', 'N/A')
            prop_type = prop.get('type', 'N/A')
            prop_desc = prop.get('description', 'N/A')
            print(f"    - {prop_name} ({prop_type}): {prop_desc}")
        print("-" * 20)

    print("\n" + "="*40)
    print("RELATIONSHIPS (EDGES)")
    print("="*40)
    for name, details in ontology.get('relationships', {}).items():
        print(f"Relationship: {name}")
        domain = details.get('domain', 'N/A')
        range_ = details.get('range', 'N/A')
        description = details.get('description', 'N/A')
        print(f"  {domain} -> {name} -> {range_}")
        print(f"  Description: {description}")
        if 'symmetric' in details and details['symmetric']:
            print("  (This relationship is symmetric)")
        print("-" * 20)


if __name__ == "__main__":
    read_ontology('test/company.yaml')
