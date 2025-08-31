from owlready2 import (
    get_ontology,
    Thing,
    ObjectProperty,
    DataProperty,
    FunctionalProperty,
    SymmetricProperty
)
import datetime

# Define the ontology IRI (Internationalized Resource Identifier)
onto = get_ontology("http://fortusight.ai/fund-raising-ontology#")

with onto:
    #///////////////////////////////////////////////////////////////////////////////////////
    #//
    #//   Classes (Entities)
    #//
    #///////////////////////////////////////////////////////////////////////////////////////


    class VC(Thing):
        """A Venture Capital firm that invests in other companies."""
        pass

    class Portfolio_Company(Thing):
        """A company that has received investment from a VC."""
        pass

    class Acquiring_Company(Thing):
        """A company that acquires another company."""
        pass

    class Partner(Thing):
        """An individual who is a partner at a VC firm."""
        pass

    class Investment(Thing):
        """Represents a single investment event from a VC into a Portfolio Company."""
        pass

    class Acquisition(Thing):
        """Represents the event of one company acquiring another."""
        pass


    #///////////////////////////////////////////////////////////////////////////////////////
    #//
    #//   Object Properties (Relationships between Entities)
    #//
    #///////////////////////////////////////////////////////////////////////////////////////

    class invests_in(ObjectProperty):
        """Connects a VC to a Portfolio_Company through an Investment event."""
        domain = [VC]
        range = [Investment]

    class investment_target(ObjectProperty):
        """Connects an Investment event to the Portfolio_Company that received it."""
        domain = [Investment]
        range = [Portfolio_Company]
        # An investment event can only target one company
        inverse_property = FunctionalProperty(Thing)

    class was_acquired_in(ObjectProperty):
        """Connects a Portfolio_Company to the Acquisition event in which it was acquired."""
        domain = [Portfolio_Company]
        range = [Acquisition]

    class acquired_by(ObjectProperty):
        """Connects an Acquisition event to the Acquiring_Company."""
        domain = [Acquisition]
        range = [Acquiring_Company]

    class has_partner(ObjectProperty):
        """Connects a VC to a Partner who works there."""
        domain = [VC]
        range = [Partner]

    class co_invests_with(ObjectProperty, SymmetricProperty):
        """A symmetric relationship between two VCs that have invested in the same funding round."""
        domain = [VC]
        range = [VC]


    #///////////////////////////////////////////////////////////////////////////////////////
    #//
    #//   Datatype Properties (Attributes of Entities)
    #//
    #///////////////////////////////////////////////////////////////////////////////////////

    class name(DataProperty, FunctionalProperty):
        """A string representing the official name of an entity."""
        domain = [Thing]
        range = [str]

    class website(DataProperty, FunctionalProperty):
        """The official website URL of an organization."""
        domain = [Thing]
        range = [str]

    class investment_amount(DataProperty, FunctionalProperty):
        """The monetary value of an investment."""
        domain = [Investment]
        range = [float]

    class investment_date(DataProperty, FunctionalProperty):
        """The date an investment was made."""
        domain = [Investment]
        range = [datetime.date]
        
    class funding_round(DataProperty, FunctionalProperty):
        """The specific funding round of the investment (e.g., Seed, Series A, etc.)."""
        domain = [Investment]
        range = [str]

    class acquisition_price(DataProperty, FunctionalProperty):
        """The price for which a company was acquired."""
        domain = [Acquisition]
        range = [float]

    class acquisition_date(DataProperty, FunctionalProperty):
        """The date an acquisition was completed."""
        domain = [Acquisition]
        range = [datetime.date]

    class description(DataProperty):
        """A text description of an entity or event."""
        domain = [Thing]
        range = [str]

    class source(DataProperty):
        """The source of the information (e.g., a URL to a press release or article)."""
        domain = [Thing]
        range = [str]