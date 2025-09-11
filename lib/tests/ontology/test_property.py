import pytest
import os

from a1facts.ontology.property import Property

def test_property_initialization():
    """Test the initialization of a Property object."""
    prop = Property(name="test_name", prop_type="string", description="A test property.", primary_key=False)
    assert prop.property_name == "test_name"
    assert prop.type == "string"
    assert prop.description == "A test property."
    assert prop.primary_key is False

def test_property_initialization_primary_key():
    """Test the initialization of a Property object as a primary key."""
    prop = Property(name="id", prop_type="int", description="Unique identifier.", primary_key=True)
    assert prop.property_name == "id"
    assert prop.type == "int"
    assert prop.description == "Unique identifier."
    assert prop.primary_key is True

def test_property_str_representation():
    """Test the string representation of a non-primary key property."""
    prop = Property(name="test_name", prop_type="string", description="A test property.")
    expected_str = "test_name (string) - A test property."
    assert str(prop) == expected_str

def test_property_str_representation_primary_key():
    """Test the string representation of a primary key property."""
    prop = Property(name="id", prop_type="int", description="Unique identifier.", primary_key=True)
    expected_str = "id (int) - Unique identifier. - Primary Key"
    assert str(prop) == expected_str
