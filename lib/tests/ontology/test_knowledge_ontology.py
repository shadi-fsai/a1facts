import pytest
import os

from ontology.knowledge_ontology import KnowledgeOntology

@pytest.fixture
def ontology():
    """Fixture to create a KnowledgeOntology instance for testing."""
    # Use a real ontology file from the cookbook for a realistic test
    ontology_file = os.path.join(os.path.dirname(__file__),  'company.yaml')
    return KnowledgeOntology(ontology_file)

def test_ontology_loading(ontology):
    """Test if the ontology is loaded correctly."""
    assert ontology.name == "Company Knowledge Graph"
    assert "Financial and Market Intelligence" in ontology.description
    assert len(ontology.entity_classes) > 0
    assert len(ontology.relationship_classes) > 0

def test_entity_class_parsing(ontology):
    """Test if entity classes are parsed correctly."""
    company_class = ontology.find_entity_class("Company")
    assert company_class is not None
    assert company_class.entity_class_name == "Company"
    assert "A business entity" in company_class.description
    
    # Check for a specific property
    name_property = next((p for p in company_class.properties if p.property_name == "name"), None)
    assert name_property is not None
    assert name_property.type == "str"
    assert name_property.primary_key is True

def test_relationship_class_parsing(ontology):
    """Test if relationship classes are parsed correctly."""
    competes_with_rel = next((r for r in ontology.relationship_classes if r.relationship_name == "competes_with"), None)
    assert competes_with_rel is not None
    assert competes_with_rel.domain_entity_class == "Company"
    assert competes_with_rel.range_entity_class == "Company"
    assert competes_with_rel.symmetric is True

def test_tool_creation(ontology):
    """Test the creation of tools."""
    # Dummy functions for tool creation
    def dummy_func(*args, **kwargs):
        pass

    # Test entity tool creation
    add_update_tools = ontology.get_tools_add_or_update_entity(dummy_func)
    assert len(add_update_tools) == len(ontology.entity_classes)

    get_prop_tools = ontology.get_tools_get_entity_properties(dummy_func)
    assert len(get_prop_tools) == len(ontology.entity_classes)

    get_all_tools = ontology.get_tools_get_all_entity(dummy_func)
    assert len(get_all_tools) == len(ontology.entity_classes)

    # Test relationship tool creation
    add_rel_tools = ontology.get_tools_add_or_update_relationship(dummy_func)
    assert len(add_rel_tools) == len(ontology.relationship_classes)

    get_rel_prop_tools = ontology.get_tools_get_relationship_properties(dummy_func)
    assert len(get_rel_prop_tools) == len(ontology.relationship_classes)
    
    get_rel_entities_tools = ontology.get_tools_get_relationship_entities(dummy_func)
    assert len(get_rel_entities_tools) == len(ontology.relationship_classes)
