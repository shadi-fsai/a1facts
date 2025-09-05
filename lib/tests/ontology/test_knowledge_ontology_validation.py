import pytest
import os
import yaml
from ontology.knowledge_ontology import KnowledgeOntology

@pytest.fixture
def create_temp_yaml(tmp_path):
    """A fixture to create temporary YAML files for testing."""
    def _create_yaml(content, name="invalid_ontology.yaml"):
        path = tmp_path / name
        path.write_text(yaml.dump(content))
        return str(path)
    return _create_yaml

def test_relationship_with_missing_domain_fails(create_temp_yaml):
    """
    Tests that loading an ontology fails when a relationship is missing a domain.
    """
    content = {
        'entity_classes': {
            'Company': {'description': 'A company', 'properties': []},
            'Sector': {'description': 'A sector', 'properties': []}
        },
        'relationships': {
            'operates_in': {
                # 'domain': 'Company',  <-- Missing
                'range': 'Sector',
                'description': 'Operates in a sector'
            }
        }
    }
    file_path = create_temp_yaml(content)
    # This should fail because `domain` will be None when passed to RelationshipClass
    with pytest.raises(AttributeError, match="'NoneType' object has no attribute 'entity_class_name'"):
        KnowledgeOntology(file_path)

def test_relationship_with_non_existent_domain_fails(create_temp_yaml):
    """
    Tests that loading fails when a relationship's domain entity does not exist.
    """
    content = {
        'entity_classes': {
            'Sector': {'description': 'A sector', 'properties': []}
        },
        'relationships': {
            'operates_in': {
                'domain': 'NonExistentCompany',
                'range': 'Sector',
                'description': 'Operates in a sector'
            }
        }
    }
    file_path = create_temp_yaml(content)
    # This should also fail with the same AttributeError
    with pytest.raises(AttributeError, match="'NoneType' object has no attribute 'entity_class_name'"):
        KnowledgeOntology(file_path)

def test_entity_property_missing_name(create_temp_yaml):
    """
    Tests if the system handles an entity property missing its 'name'.
    The current implementation will create a property named 'N/A'.
    This test confirms the current (unsafe) behavior.
    """
    content = {
        'entity_classes': {
            'Company': {
                'description': 'A company',
                'properties': [
                    {'type': 'string', 'description': 'A property without a name'}
                ]
            }
        }
    }
    file_path = create_temp_yaml(content)
    ontology = KnowledgeOntology(file_path)
    company_class = ontology.find_entity_class('Company')
    assert company_class is not None
    assert len(company_class.properties) == 1
    # This is the undesirable behavior: a property is created with the name 'N/A'
    assert company_class.properties[0].property_name == 'N/A'

def test_relationship_property_missing_name(create_temp_yaml):
    """
    Tests if the system handles a relationship property missing its 'name'.
    This test uses 'property_name' as per the code, but if that's missing,
    it should also create a property named 'N/A'.
    """
    content = {
        'entity_classes': {
            'Company': {
                'description': 'A company', 
                'properties': [{'name': 'name', 'type': 'string', 'description': 'pk', 'primary_key': True}]
            },
            'Sector': {
                'description': 'A sector', 
                'properties': [{'name': 'name', 'type': 'string', 'description': 'pk', 'primary_key': True}]
            }
        },
        'relationships': {
            'operates_in': {
                'domain': 'Company',
                'range': 'Sector',
                'description': 'Operates in a sector',
                'properties': [
                    # The key should be 'property_name', but it's missing.
                    {'type': 'string', 'description': 'A property without a name'}
                ]
            }
        }
    }
    file_path = create_temp_yaml(content)
    ontology = KnowledgeOntology(file_path)
    rel_class = ontology.relationship_classes[0]
    assert len(rel_class.properties) == 1
    # This is also undesirable: property is created with name 'N/A'
    assert rel_class.properties[0].property_name == 'N/A'
