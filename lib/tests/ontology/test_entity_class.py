import pytest
from ontology.entity_class import EntityClass
from ontology.property import Property

@pytest.fixture
def sample_entity_class():
    """Returns a sample EntityClass object for testing."""
    entity = EntityClass(name="Company", description="A business entity")
    entity.add_property(Property(name="name", prop_type="string", description="The name of the company", primary_key=True))
    entity.add_property(Property(name="ticker", prop_type="string", description="The stock ticker symbol"))
    entity.add_property(Property(name="revenue", prop_type="float", description="The annual revenue"))
    entity.add_property(Property(name="employees", prop_type="integer", description="Number of employees"))
    return entity

@pytest.fixture
def entity_class_no_properties():
    """Returns an EntityClass with no properties."""
    return EntityClass(name="Event", description="A calendar event")

def test_entity_class_no_properties(entity_class_no_properties):
    """Tests the behavior of an EntityClass with no properties."""
    assert entity_class_no_properties.entity_class_name == "Event"
    assert len(entity_class_no_properties.properties) == 0
    assert entity_class_no_properties.primary_key_prop is None

    # Test tool creation with no properties
    assert entity_class_no_properties.get_tool_add_or_update_entity(None) is None
    
    schema = entity_class_no_properties._get_tool_parameters_schema()
    assert schema["properties"] == {}
    assert schema["required"] == []

def test_entity_class_init(sample_entity_class):
    """Tests the initialization of an EntityClass object."""
    assert sample_entity_class.entity_class_name == "Company"
    assert sample_entity_class.description == "A business entity"
    assert len(sample_entity_class.properties) == 4
    assert sample_entity_class.primary_key_prop.property_name == "name"

def test_add_property(sample_entity_class):
    """Tests adding a property to an entity class."""
    new_prop = Property(name="website", prop_type="string", description="The company's website")
    sample_entity_class.add_property(new_prop)
    assert len(sample_entity_class.properties) == 5
    assert sample_entity_class.properties[-1] == new_prop

def test_str_representation(sample_entity_class):
    """Tests the string representation of an EntityClass object."""
    expected_str = f"{sample_entity_class.entity_class_name} ({sample_entity_class.description})\n"
    expected_str += "      Properties:\n"
    for prop in sample_entity_class.properties:
        expected_str += f"      - {prop}\n"
    assert str(sample_entity_class) == expected_str

def test_get_tool_parameters_schema(sample_entity_class):
    """Tests the _get_tool_parameters_schema method."""
    schema = sample_entity_class._get_tool_parameters_schema()
    expected_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "The name of the company"},
            "ticker": {"type": "string", "description": "The stock ticker symbol"},
            "revenue": {"type": "number", "description": "The annual revenue"},
            "employees": {"type": "integer", "description": "Number of employees"}
        },
        "required": ["name", "ticker", "revenue", "employees"]
    }
    assert schema == expected_schema

def test_get_add_or_update_tool(sample_entity_class):
    """Tests the get_add_or_update_tool method."""
    def mock_add_or_update(entity_class_name, primary_key_name, properties):
        return f"Updated {entity_class_name} with {primary_key_name}={properties[primary_key_name]}"

    tool = sample_entity_class.get_tool_add_or_update_entity(mock_add_or_update)
    assert tool.__name__ == "add_or_update_Company_information"
    assert "Primary key: name" in tool.__doc__
    
    # Test calling the tool
    result = tool(kwargs={'name': 'TestCorp', 'ticker': 'TC'})
    assert result == "Updated Company with name=TestCorp"
    result_no_kwargs = tool(name='TestCorp2', ticker='TC2')
    assert result_no_kwargs == "Updated Company with name=TestCorp2"


def test_get_all_entity_tool(sample_entity_class):
    """Tests the get_get_all_entity_tool method."""
    def mock_get_all(entity_class_name):
        return [f"{entity_class_name}_1", f"{entity_class_name}_2"]

    tool = sample_entity_class.get_tool_get_all_entity(mock_get_all)
    assert tool.__name__ == "get_all_Company_entities"
    assert tool.__doc__ == "Get all Company entities."
    
    # Test calling the tool
    result = tool()
    assert result == ["Company_1", "Company_2"]

def test_get_entity_properties_tool(sample_entity_class):
    """Tests the get_get_entity_properties_tool method."""
    def mock_get_properties(entity_class_name, pk_name, pk_value):
        if pk_value is None:
            return "pk_value was None"
        return {pk_name: pk_value, "ticker": "TC"}

    tool = sample_entity_class.get_tool_get_entity_properties(mock_get_properties)
    assert tool.__name__ == "get_Company_properties"
    
    expected_doc = f"Get a {sample_entity_class.entity_class_name} properties. \n" + (f"Returns properties: {sample_entity_class.properties}" if sample_entity_class.properties else "") + "\n"
    assert tool.__doc__ == expected_doc

    # The tool's defined parameter name in its schema (`__parameters__`)
    param_name_in_schema = f"{sample_entity_class.entity_class_name}_{sample_entity_class.primary_key_prop.property_name}"

    assert param_name_in_schema in tool.__parameters__["properties"]

    # Test calling the tool as an agent would, using the parameter from the schema.
    result_as_agent = tool(**{param_name_in_schema: "TestCorp"})
    assert result_as_agent == {"name": "TestCorp", "ticker": "TC"}
