import pytest
from a1facts.ontology.knowledge_ontology import KnowledgeOntology

@pytest.fixture
def ontology(tmp_path):
    """Fixture to create a KnowledgeOntology instance for testing."""
    ontology_data = {
        'world': {
            'name': 'Test World',
            'description': 'An ontology for testing RDFS parsing.'
        },
        'entity_classes': {
            'Person': {
                'description': 'A human being.',
                'properties': [
                    {'name': 'name', 'type': 'string', 'primary_key': True},
                    {'name': 'age', 'type': 'integer'}
                ]
            },
            'Company': {
                'description': 'A business entity.',
                'properties': [
                    {'name': 'name', 'type': 'string', 'primary_key': True},
                    {'name': 'industry', 'type': 'string'}
                ]
            }
        },
        'relationships': {
            'WORKS_AT': {
                'description': 'A Person works at a Company.',
                'domain': 'Person',
                'range': 'Company'
            }
        }
    }
    file_path = tmp_path / "test_ontology.yaml"
    import yaml
    with open(file_path, 'w') as f:
        yaml.dump(ontology_data, f)
    return KnowledgeOntology(str(file_path))

@pytest.mark.parametrize("rdfs_content, expected_name, expected_age", [
    # Standard case
    (':Alice a :Person ; :name "Alice" ; :age 30 .', "Alice", "30"),
    # Blank node
    ('_:b1 a :Person ; :name "Bob" ; :age 42 .', "Bob", "42"),
    # Extra whitespace
    ('   :Carol a :Person ; \n :name "Carol"  ; \n\n :age 25 .   ', "Carol", "25"),
    # No final semicolon
    (':David a :Person ; :name "David" ; :age 50', "David", "50"),
    # Comments
    ('# This is a test\n:Eve a :Person ; # entity definition\n :name "Eve" ; :age 33 .', "Eve", "33"),
])
def test_various_entity_formats(ontology, rdfs_content, expected_name, expected_age):
    """Tests parsing various RDFS entity formats."""
    entities, _ = ontology.parse_rdfs_with_validation(rdfs_content)
    assert len(entities) == 1
    
    entity = entities[0]
    # For blank nodes, the entity name is an internal ID, so we check the 'name' property.
    if rdfs_content.strip().startswith('_:'):
         assert entity.properties["name"] == expected_name
    else:
        assert entity.name == expected_name

    assert entity.properties["age"] == expected_age

def test_multiple_entities(ontology):
    """Tests parsing multiple entities in one go."""
    rdfs_content = """
    :Alice a :Person ; :name "Alice" ; :age 30.
    :ACME a :Company ; :name "ACME" ; :industry "Manufacturing".
    """
    entities, _ = ontology.parse_rdfs_with_validation(rdfs_content)
    assert len(entities) == 2

    alice = next(e for e in entities if e.name == "Alice")
    acme = next(e for e in entities if e.name == "ACME")

    assert alice.properties["age"] == "30"
    assert acme.properties["name"] == "ACME"
    assert acme.properties["industry"] == "Manufacturing"


@pytest.mark.parametrize("rdfs_content, domain, rel, range_name", [
    # Standard relationship
    (':Alice a :Person ; :name "Alice" . :ACME a :Company ; :name "ACME" . :Alice :WORKS_AT :ACME .', "Alice", "WORKS_AT", "ACME"),
    # Relationship with blank nodes
    ('_:a a :Person ; :name "Anon" . _:c a :Company ; :name "Confidential" . _:a :WORKS_AT _:c .', "a", "WORKS_AT", "c"),
])
def test_relationship_parsing(ontology, rdfs_content, domain, rel, range_name):
    """Tests parsing various RDFS relationship formats."""
    entities, relationships = ontology.parse_rdfs_with_validation(rdfs_content)
    assert len(entities) == 2
    assert len(relationships) == 1

    relationship = relationships[0]
    assert relationship.domain_entity.name == domain
    assert relationship.relationship == rel
    assert relationship.range_entity.name == range_name
