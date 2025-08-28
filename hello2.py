# Import the rdflib library, which is the core Python library for working with RDF.
import rdflib
# Import specific components from rdflib: Graph for the RDF graph, URIRef for URIs, Literal for data values, and Namespace for defining URI prefixes.
from rdflib import Graph, URIRef, Literal, Namespace
# Import predefined RDF namespaces for convenience (RDF, RDFS, XSD for data types, and OWL for ontology constructs).
from rdflib.namespace import RDF, RDFS, XSD, OWL

# The main function where the script's logic resides.
def main():
    # --- Namespace and Graph Setup ---
    # Create a custom namespace for all the elements (classes, properties, individuals) in our ontology.
    # The '#' at the end is a common convention for namespaces.
    ns = Namespace("http://test.org/company_facts.owl#")

    # Create a new, empty RDF Graph. This object will hold all our RDF triples.
    g = Graph()

    # Bind the custom namespace to the prefix 'comp'. This makes the serialized output (e.g., XML) more readable.
    g.bind("comp", ns)
    # Bind the standard RDF namespace to the 'rdf' prefix.
    g.bind("rdf", RDF)
    # Bind the standard RDFS (RDF Schema) namespace to the 'rdfs' prefix.
    g.bind("rdfs", RDFS)
    # Bind the standard OWL (Web Ontology Language) namespace to the 'owl' prefix.
    g.bind("owl", OWL)

    # --- Schema/Ontology Definition ---
    # Define URIs for our classes by appending terms to our custom namespace.
    Company = ns.Company
    Fact = ns.Fact
    Source = ns.Source
    Rating = ns.Rating
    
    # Add triples to the graph to declare that our URIs represent classes (using rdf:type rdfs:Class).
    g.add((Company, RDF.type, RDFS.Class))
    g.add((Fact, RDF.type, RDFS.Class))
    g.add((Source, RDF.type, RDFS.Class))
    g.add((Rating, RDF.type, RDFS.Class))

    # --- Property Definitions ---
    # Define a URI for the 'has_fact' property.
    has_fact = ns.has_fact
    # Declare 'has_fact' as an RDF property.
    g.add((has_fact, RDF.type, RDF.Property))
    # Define the domain of 'has_fact'. The domain specifies that any resource using this property (the subject of the triple)
    # should be an instance of the 'Company' class. e.g., in (InnovateCorp, has_fact, RevenueFact), InnovateCorp is a Company.
    g.add((has_fact, RDFS.domain, Company))
    # Define the range of 'has_fact'. The range specifies that the value of this property (the object of the triple)
    # should be an instance of the 'Fact' class. e.g., in (InnovateCorp, has_fact, RevenueFact), RevenueFact is a Fact.
    g.add((has_fact, RDFS.range, Fact))

    # Define URIs for the properties related to the 'Fact' class.
    fact_type = ns.fact_type
    fact_value = ns.fact_value
    has_source = ns.has_source
    has_rating = ns.has_rating
    is_related_to = ns.is_related_to

    # Define 'fact_type' as a property with Fact as its domain and a string as its range.
    g.add((fact_type, RDF.type, RDF.Property))
    g.add((fact_type, RDFS.domain, Fact))
    g.add((fact_type, RDFS.range, XSD.string))

    # Define 'fact_value' as a property with Fact as its domain and a float as its range.
    g.add((fact_value, RDF.type, RDF.Property))
    g.add((fact_value, RDFS.domain, Fact))
    g.add((fact_value, RDFS.range, XSD.float))

    # Define 'has_source' as a property linking a Fact to a Source.
    g.add((has_source, RDF.type, RDF.Property))
    g.add((has_source, RDFS.domain, Fact))
    g.add((has_source, RDFS.range, Source))

    # Define 'has_rating' as a property linking a Fact to a Rating.
    g.add((has_rating, RDF.type, RDF.Property))
    g.add((has_rating, RDFS.domain, Fact))
    g.add((has_rating, RDFS.range, Rating))
    
    # Define 'is_related_to' as a symmetric property (if A is related to B, then B is related to A).
    g.add((is_related_to, RDF.type, OWL.SymmetricProperty))
    # Its domain and range are both 'Fact', meaning it links a fact to another fact.
    g.add((is_related_to, RDFS.domain, Fact))
    g.add((is_related_to, RDFS.range, Fact))

    # Define URIs for the properties of the 'Source' class.
    source_name = ns.source_name
    source_url = ns.source_url
    
    # Define 'source_name' as a property with Source as domain and string as range.
    g.add((source_name, RDF.type, RDF.Property))
    g.add((source_name, RDFS.domain, Source))
    g.add((source_name, RDFS.range, XSD.string))
    
    # Define 'source_url' as a property with Source as domain and string as range.
    g.add((source_url, RDF.type, RDF.Property))
    g.add((source_url, RDFS.domain, Source))
    g.add((source_url, RDFS.range, XSD.string))

    # Define the URI for the 'rating_value' property.
    rating_value = ns.rating_value
    # Define 'rating_value' as a property with Rating as domain and string as range.
    g.add((rating_value, RDF.type, RDF.Property))
    g.add((rating_value, RDFS.domain, Rating))
    g.add((rating_value, RDFS.range, XSD.string))


    # --- Instance Creation ---
    # Create a URI for the 'InnovateCorp' company instance.
    innovate_corp = ns.InnovateCorp
    # State that 'innovate_corp' is an instance of the 'Company' class.
    g.add((innovate_corp, RDF.type, Company))
    # Add a human-readable label to the company instance.
    g.add((innovate_corp, RDFS.label, Literal("InnovateCorp")))

    # Create a URI for the 'RevenueFact_2023' fact instance.
    revenue_fact = ns.RevenueFact_2023
    # State that 'revenue_fact' is an instance of the 'Fact' class.
    g.add((revenue_fact, RDF.type, Fact))
    # Add the fact's type as a literal string.
    g.add((revenue_fact, fact_type, Literal("Annual Revenue 2023")))
    # Add the fact's value as a typed literal (decimal for precision).
    g.add((revenue_fact, fact_value, Literal(150000000.50, datatype=XSD.decimal)))

    # Link the company to its fact using the 'has_fact' property.
    g.add((innovate_corp, has_fact, revenue_fact))

    # Create a URI for the 'AnnualReport2023' source instance.
    annual_report = ns.AnnualReport2023
    # State that 'annual_report' is an instance of the 'Source' class.
    g.add((annual_report, RDF.type, Source))
    # Add the source's name as a literal string.
    g.add((annual_report, source_name, Literal("InnovateCorp 2023 Annual Report")))
    # Add the source's URL as a typed literal (anyURI).
    g.add((annual_report, source_url, Literal("http://innovatecorp.com/reports/2023.pdf", datatype=XSD.anyURI)))
    
    # Link the revenue fact to its source.
    g.add((revenue_fact, has_source, annual_report))

    # Create a URI for the 'HighReliability' rating instance.
    high_rating = ns.HighReliability
    # State that 'high_rating' is an instance of the 'Rating' class.
    g.add((high_rating, RDF.type, Rating))
    # Add the rating's value (e.g., "High") as a literal string.
    g.add((high_rating, rating_value, Literal("High")))
    
    # Link the revenue fact to its rating.
    g.add((revenue_fact, has_rating, high_rating))

    # Create another fact instance for 'Net Profit'.
    profit_fact = ns.ProfitFact_2023
    # State that 'profit_fact' is an instance of the 'Fact' class.
    g.add((profit_fact, RDF.type, Fact))
    # Add its type and value.
    g.add((profit_fact, fact_type, Literal("Net Profit 2023")))
    g.add((profit_fact, fact_value, Literal(25000000.75, datatype=XSD.decimal)))
    # This fact can re-use the same source and rating instances.
    g.add((profit_fact, has_source, annual_report))
    g.add((profit_fact, has_rating, high_rating))
    
    # Link this new fact to the company as well.
    g.add((innovate_corp, has_fact, profit_fact))

    # Make the two facts related to each other. Since 'is_related_to' is symmetric, the reverse is also true.
    g.add((revenue_fact, is_related_to, profit_fact))

    # --- Verification and Output ---
    # Call the helper function to print the company's facts from the graph.
    print_company_facts(g, innovate_corp, ns)

    # Save the graph to a file. 'destination' is the filename, 'format' specifies the RDF serialization (e.g., xml, turtle, n3).
    g.serialize(destination="company_facts_rdflib.owl", format="xml")
    # Print a confirmation message.
    print("\nOntology saved to company_facts_rdflib.owl")

    # --- Example Queries ---
    # Print a header for the query section.
    print("\n--- Example Queries (SPARQL) ---")
    print("Finding all facts with 'High' rating:")
    
    # Define a SPARQL query as a multi-line string.
    # SELECT: specifies the variables to return.
    # WHERE: specifies the graph patterns to match.
    query = """
    SELECT ?fact_type
    WHERE {
        ?fact_instance comp:has_rating ?rating_instance .
        ?rating_instance comp:rating_value "High" .
        ?fact_instance comp:fact_type ?fact_type .
    }
    """
    
    # Execute the query on the graph. 'initNs' provides the prefixes used in the query.
    results = g.query(query, initNs={'comp': ns})
    # Loop through the results. Each 'row' is a solution to the query.
    for row in results:
        # Access the result variables by name (e.g., row.fact_type) and print them.
        print(f" - {row.fact_type}")

# A helper function to print facts for a given company from the graph.
def print_company_facts(graph, company_uri, namespace):
    # Retrieve the company's label from the graph. '.value()' gets a single object for a subject-predicate pair.
    company_label = graph.value(subject=company_uri, predicate=RDFS.label)
    print(f"Facts for company: {company_label}")
    
    # Iterate through all 'Fact' instances linked to the company. '.objects()' gets all objects for a subject-predicate pair.
    for fact in graph.objects(subject=company_uri, predicate=namespace.has_fact):
        # Retrieve the type and value for the current fact.
        fact_type = graph.value(subject=fact, predicate=namespace.fact_type)
        fact_value = graph.value(subject=fact, predicate=namespace.fact_value)
        # Extract a short name from the fact's URI for display.
        fact_name = str(fact).split('#')[-1]
        print(f"  - Fact ({fact_name}): {fact_type} - Value: {fact_value}")

        # Iterate through all sources linked to the current fact.
        for source in graph.objects(subject=fact, predicate=namespace.has_source):
            # Retrieve the source's name and URL.
            source_name = graph.value(subject=source, predicate=namespace.source_name)
            source_url = graph.value(subject=source, predicate=namespace.source_url)
            print(f"    - Source: {source_name} ({source_url})")

        # Iterate through all ratings linked to the current fact.
        for rating in graph.objects(subject=fact, predicate=namespace.has_rating):
            # Retrieve the rating's value.
            rating_val = graph.value(subject=rating, predicate=namespace.rating_value)
            print(f"    - Rating: {rating_val}")

        # Find all facts related to the current one.
        related_facts = list(graph.objects(subject=fact, predicate=namespace.is_related_to))
        # If any related facts were found...
        if related_facts:
            print("    - Related Facts:")
            # ...iterate through them.
            for related in related_facts:
                # Get the type of the related fact and print it.
                related_type = graph.value(subject=related, predicate=namespace.fact_type)
                print(f"      - {related_type}")

# Standard Python entry point check.
if __name__ == "__main__":
    # Call the main function to run the script.
    main()
