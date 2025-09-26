import pytest
from a1facts.ontology.relationship_class import RelationshipClass
from a1facts.ontology.entity_class import EntityClass
from a1facts.ontology.property import Property

@pytest.fixture
def company_entity():
    """Returns a sample Company EntityClass object."""
    entity = EntityClass(name="Company", description="A business entity")
    entity.add_property(Property(name="name", prop_type="string", description="The name of the company", primary_key=True))
    return entity

@pytest.fixture
def sector_entity():
    """Returns a sample Sector EntityClass object."""
    entity = EntityClass(name="Sector", description="An industry sector")
    entity.add_property(Property(name="name", prop_type="string", description="The name of the sector", primary_key=True))
    return entity

@pytest.fixture
def operates_in_relationship(company_entity, sector_entity):
    """Returns a sample RelationshipClass object."""
    rel = RelationshipClass(name="operates_in", domain=company_entity, range=sector_entity, description="A company operates in a sector")
    return rel

def test_relationship_class_init(operates_in_relationship, company_entity, sector_entity):
    """Tests the initialization of a RelationshipClass object."""
    assert operates_in_relationship.relationship_name == "operates_in"
    assert operates_in_relationship.domain_entity_class == company_entity.entity_class_name
    assert operates_in_relationship.range_entity_class == sector_entity.entity_class_name
    assert operates_in_relationship.domain_primary_key_prop == "name"
    assert operates_in_relationship.range_primary_key_prop == "name"
    assert len(operates_in_relationship.properties) == 0
    assert not operates_in_relationship.symmetric

def test_str_representation(operates_in_relationship):
    """Tests the string representation of a RelationshipClass object."""
    expected_str = "operates_in (A company operates in a sector) - Domain: Company - Range: Sector\n"
    assert str(operates_in_relationship) == expected_str

def test_is_symmetric():
    """Tests the is_symmetric method."""
    company = EntityClass("Company", "desc")
    company.add_property(Property("name", "string", "desc", True))
    symmetric_rel = RelationshipClass("works_with", company, company, "desc", symmetric=True)
    assert symmetric_rel.is_symmetric()


def test_get_tool_add_or_update_relationship(operates_in_relationship):
    """Tests the get_tool_add_or_update_relationship method."""
    def mock_add_or_update(*args, **kwargs):
        return f"Called with {args}"

    tool = operates_in_relationship.get_tool_add_or_update_relationship(mock_add_or_update)
    assert tool.__name__ == "add_link_Company_operates_in_Sector"
    
    result = tool(from_Company_name="TestCorp", to_Sector_name="Tech")
    assert "TestCorp" in result and "Tech" in result and "operates_in" in result

def test_get_tool_get_relationship_entities(operates_in_relationship):
    """Tests the get_get_relationship_entities_tool method."""
    def mock_get_entities(*args):
        return [f"Entity from {args[0]}"]

    tool = operates_in_relationship.get_tool_get_relationship_entities(mock_get_entities)
    assert tool.__name__ == "get_Sectors_Company_operates_in"
    
    result = tool(from_Company_name="TestCorp")
    assert "Entity from Company" in result[0]
