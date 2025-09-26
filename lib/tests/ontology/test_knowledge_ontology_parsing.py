import pytest
import os
from a1facts.ontology.knowledge_ontology import KnowledgeOntology

@pytest.fixture
def ontology():
    """Fixture to create a KnowledgeOntology instance for testing."""
    ontology_file = os.path.join(os.path.dirname(__file__), 'company.yaml')
    return KnowledgeOntology(ontology_file)

def test_parse_simple_entity(ontology):
    """Test parsing a simple entity with no properties."""
    rdfs_content = ":TestEntity a :Company ."
    entities, relationships = ontology.parse_rdfs_with_validation(rdfs_content)
    assert len(entities) == 1
    assert len(relationships) == 0
    entity = entities[0]
    assert entity.name == "TestEntity"
    assert entity.properties["type"] == "Company"

def test_parse_entity_with_properties(ontology):
    """Test parsing an entity with properties."""
    rdfs_content = """
    :FMC_Corporation a :Company ;
        :name "FMC Corporation" ;
        :company_type "Public Company" .
    """
    entities, relationships = ontology.parse_rdfs_with_validation(rdfs_content)
    assert len(entities) == 1
    entity = entities[0]
    assert entity.name == "FMC_Corporation"
    assert entity.properties["name"] == "FMC Corporation"
    assert entity.properties["company_type"] == "Public Company"

def test_parse_simple_relationship(ontology):
    """Test parsing a simple relationship with no properties."""
    rdfs_content = """
    :FMC_Corporation a :Company .
    :Event_FMC_Acq_DuPont a :Corporate_Event .
    :FMC_Corporation :is_subject_of :Event_FMC_Acq_DuPont .
    """
    entities, relationships = ontology.parse_rdfs_with_validation(rdfs_content)
    assert len(entities) == 2
    assert len(relationships) == 1
    relationship = relationships[0]
    assert relationship.domain.name == "FMC_Corporation"
    assert relationship.relationship == "is_subject_of"
    assert relationship.range.name == "Event_FMC_Acq_DuPont"

def test_parse_relationship_with_stubbed_range(ontology):
    """Test parsing a relationship where the range is not explicitly defined."""
    rdfs_content = """
    :FMC_Corporation a :Company .
    :FMC_Corporation :operates_in :Crop_Protection_Market .
    """
    entities, relationships = ontology.parse_rdfs_with_validation(rdfs_content)
    assert len(entities) == 2
    assert len(relationships) == 1
    range_entity = next(e for e in entities if e.name == "Crop_Protection_Market")
    assert range_entity is not None
    assert range_entity.properties["type"] == "Market"

def test_parse_full_example_file(ontology):
    """Test parsing the full example.rdfs file."""
    rdfs_file = os.path.join(os.path.dirname(__file__), '..', '..', 'example.rdfs')
    with open(rdfs_file, 'r') as f:
        rdfs_content = f.read()
    
    entities, relationships = ontology.parse_rdfs_with_validation(rdfs_content)
    assert len(entities) > 0
    assert len(relationships) > 0
