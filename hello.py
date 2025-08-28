# To run this script, you need to install owlready2:
# pip install Owlready2

from owlready2 import *

# 1. Create a new ontology
# The IRI (Internationalized Resource Identifier) is a unique name for the ontology.
onto = get_ontology("http://test.org/company_facts.owl")

# 2. Define the ontology structure within the 'with onto:' block
with onto:
    # (1) Define Classes (Concepts)
    # The main concepts in our model are Entity, Fact, Source, and Rating.
    class Entity(Thing):
        """Represents a real-world entity, like a company."""
        pass

    class Fact(Thing):
        """Represents a piece of information about an Entity."""
        pass

    class Source(Thing):
        """Represents the origin of a Fact, e.g., a report or article."""
        pass

    class Rating(Thing):
        """Represents a confidence level or quality rating for a Fact."""
        pass

    class Timescale(Thing):
        """Represents a time period with a start and end date."""
        pass

    class EntityType(Thing):
        """Represents the type of an entity, e.g., 'Corporation', 'Startup'."""
        pass

    # (2) Define Properties (Relationships)
    # Properties connect our classes together.

    # -- Object Properties (linking individuals to individuals) --

    class has_fact(ObjectProperty):
        """Connects an Entity to its Facts."""
        domain = [Entity]
        range = [Fact]

    class is_fact_of(ObjectProperty, FunctionalProperty):
        """Connects a Fact back to its Entity."""
        domain = [Fact]
        range = [Entity]
        # 'inverse_property' creates a two-way link:
        # if fact1.is_fact_of = entity1, then entity1.has_fact automatically includes fact1.
        inverse_property = has_fact

    class has_entity_type(ObjectProperty):
        """Connects an Entity to its EntityTypes."""
        domain = [Entity]
        range = [EntityType]

    class is_related_to(ObjectProperty, TransitiveProperty, SymmetricProperty):
        """Defines a relationship between two EntityTypes. It is transitive and symmetric."""
        domain = [EntityType]
        range = [EntityType]

    class has_source(ObjectProperty):
        """Links a Fact to its Sources. A fact can have multiple sources."""
        domain = [Fact]
        range = [Source]

    class has_rating(ObjectProperty, FunctionalProperty):
        """Links a Fact to its Rating. A fact has only one rating."""
        domain = [Fact]
        range = [Rating]

    # -- Data Properties (linking individuals to data values like strings, numbers) --

    class has_type(DataProperty, FunctionalProperty):
        """The type of the fact, e.g., 'Revenue' or 'Employee Count'."""
        domain = [Fact]
        range = [str]

    class has_value(DataProperty, FunctionalProperty):
        """The value of the fact, e.g., '150M USD' or '3000'."""
        domain = [Fact]
        range = [str] # Using string for flexibility, could also be int, float, etc.

    class has_timescale(ObjectProperty, FunctionalProperty):
        """The time period the fact is relevant for."""
        domain = [Fact]
        range = [Timescale]

    class has_start_date(DataProperty, FunctionalProperty):
        """The start date of a timescale. Can be '-infinity'."""
        domain = [Timescale]
        range = [str]

    class has_end_date(DataProperty, FunctionalProperty):
        """The end date of a timescale. Can be '+infinity'."""
        domain = [Timescale]
        range = [str]


# 3. Create Individuals (Instances)
# Now we create concrete examples based on our class and property definitions.

# Create an entity
company_acme = Entity("ACME_Corporation")

# Create some entity types
type_corp = EntityType("Corporation")
type_public = EntityType("Public_Company")
type_tech = EntityType("Technology_Company")

# Define relationships between types
# e.g., a Public Company is a type of Corporation
type_public.is_related_to.append(type_corp)
# e.g., a Tech Company can also be a Corporation
type_tech.is_related_to.append(type_corp)

# Assign types to the entity
company_acme.has_entity_type.append(type_public)
company_acme.has_entity_type.append(type_tech)

# Create some sources
source_report = Source("Annual_Report_2023")
source_news = Source("Financial_News_Article_Jan_2024")

# Create some ratings
rating_high_confidence = Rating("High_Confidence")
rating_medium_confidence = Rating("Medium_Confidence")

# Create a Fact about ACME Corporation's revenue
fact_revenue = Fact("ACME_Revenue_2023")
fact_revenue.is_fact_of = company_acme
fact_revenue.has_type = "Annual Revenue"
fact_revenue.has_value = "300M USD"
# Create and assign a timescale for the revenue fact
ts_revenue = Timescale("Timescale_Revenue_2023")
ts_revenue.has_start_date = "2023-01-01"
ts_revenue.has_end_date = "2023-12-31"
fact_revenue.has_timescale = ts_revenue
fact_revenue.has_source.append(source_report)
fact_revenue.has_source.append(source_news)
fact_revenue.has_rating = rating_high_confidence

# Create another Fact about the number of employees
fact_employees = Fact("ACME_Employees_2023")
fact_employees.is_fact_of = company_acme
fact_employees.has_type = "Number of Employees"
fact_employees.has_value = "5150"
# Create and assign a timescale for the employees fact (point in time)
ts_employees = Timescale("Timescale_Employees_2023")
ts_employees.has_start_date = "2023-12-31"
ts_employees.has_end_date = "2023-12-31"
fact_employees.has_timescale = ts_employees
fact_employees.has_source.append(source_report)
fact_employees.has_rating = rating_medium_confidence

# Create a Fact about the company's status to show infinity
fact_active = Fact("ACME_Is_Active")
fact_active.is_fact_of = company_acme
fact_active.has_type = "Is Active"
fact_active.has_value = "True"
# Create and assign a timescale for the active status fact
ts_active = Timescale("Timescale_Active")
ts_active.has_start_date = "1995-04-10" # Assuming founding date
ts_active.has_end_date = "+infinity"
fact_active.has_timescale = ts_active
fact_active.has_rating = rating_high_confidence

# 4. Save the ontology to a file
output_file = "company_facts.owl"
onto.save(file=output_file, format="rdfxml")
print(f"Ontology saved to '{output_file}'")

# 5. Verify and Display the structure
print("\n--- Ontology Content Verification ---")

# Display Entity Info and its Types
entity_type_names = [et.name for et in company_acme.has_entity_type]
print(f"Entity: {company_acme.name} (Types: {', '.join(entity_type_names)})")

# Display relationships for the entity's types
for et in company_acme.has_entity_type:
    related_types = [rt.name for rt in et.is_related_to]
    if related_types:
        print(f"  - EntityType '{et.name}' is related to: {', '.join(related_types)}")


print(f"\nFacts for Entity: {company_acme.name}")

# Accessing facts through the inverse property 'has_fact' on the entity
for fact in company_acme.has_fact:
    print(f"\n  - Fact: {fact.name}")
    print(f"    - Type: {fact.has_type}")
    print(f"    - Value: {fact.has_value}")
    if fact.has_timescale:
        ts = fact.has_timescale
        print(f"    - Timescale: From {ts.has_start_date} to {ts.has_end_date}")
    
    if fact.has_rating:
        print(f"    - Rating: {fact.has_rating.name}")
    
    # Get the names of all sources for this fact
    source_names = [s.name for s in fact.has_source]
    if source_names:
        print(f"    - Sources: {', '.join(source_names)}")

