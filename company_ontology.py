from owlready2 import *
onto = get_ontology("http://fortusight.ai/company-ontology#")

with onto:
    #///////////////////////////////////////////////////////////////////////////////////////
    #//
    #//   Classes (Entities)
    #//
    #///////////////////////////////////////////////////////////////////////////////////////

    class Organization(Thing):
        """A business, governmental, or regulatory entity."""
        pass

    class Regulatory_Body(Organization):
        """A government agency that exercises a regulatory function."""
        pass

    class Product_Service(Thing):
        """An offering commercialized by an Organization."""
        pass

    class Market(Thing):
        """The industry or economic sector where organizations compete."""
        pass

    class Financial_Metric(Thing):
        """A quantitative data point on financial performance, valuation, or efficiency."""
        pass

    class Corporate_Event(Thing):
        """A significant occurrence or announcement involving an Organization."""
        pass

    class Person(Thing):
        """An individual in a leadership or governance role."""
        pass

    class Competitive_Advantage(Thing):
        """A factor providing a long-term advantage over competitors (Moat)."""
        pass

    class Risk_Factor(Thing):
        """A potential threat to an Organization's performance or valuation."""
        pass

    class Capital_Allocation_Policy(Thing):
        """An Organization's stated strategy for deploying capital."""
        pass

    class Financial_Instrument(Thing):
        """A contract giving rise to a financial liability, such as debt."""
        pass

    class Role(Thing):
        """An association class representing a Person holding a position at an Organization."""
        pass

    #///////////////////////////////////////////////////////////////////////////////////////
    #//
    #//   Object Properties (Relationships between Entities)
    #//
    #///////////////////////////////////////////////////////////////////////////////////////

    class operates_in(ObjectProperty):
        """Connects an Organization to a Market it operates within."""
        domain = [Organization]
        range = [Market]

    class competes_with(ObjectProperty):
        """A symmetric relationship between two competing Organizations."""
        domain = [Organization]
        range = [Organization]
        # This makes the property symmetric (if A competes_with B, then B competes_with A)
        symmetric = True

    class produces(ObjectProperty):
        """Links an Organization to a Product or Service it offers."""
        domain = [Organization]
        range = [Product_Service]

    class is_subject_of(ObjectProperty):
        """Links an Organization to an event concerning it."""
        domain = [Organization]
        range = [Corporate_Event]

    class reports(ObjectProperty):
        """Connects an event (like an earnings call) to the financial metrics disclosed."""
        domain = [Corporate_Event]
        range = [Financial_Metric]

    class is_led_by(ObjectProperty):
        """Connects an Organization to a Person in a leadership role."""
        domain = [Organization]
        range = [Person]

    class has_role(ObjectProperty):
        """Connects a Person to their various roles (past and present)."""
        domain = [Person]
        range = [Role]

    class held_at(ObjectProperty, FunctionalProperty):
        """Connects a Role to the Organization where it is held."""
        domain = [Role]
        range = [Organization]

    class possesses(ObjectProperty):
        """Links an Organization to its Competitive Advantage (Moat)."""
        domain = [Organization]
        range = [Competitive_Advantage]

    class is_exposed_to(ObjectProperty):
        """Connects an Organization to a Risk Factor."""
        domain = [Organization]
        range = [Risk_Factor]

    class acquires(ObjectProperty):
        """Relates an acquiring Organization to a target Organization."""
        domain = [Organization]
        range = [Organization]

    class divests(ObjectProperty):
        """Relates an Organization to a Product or Service it has sold off."""
        domain = [Organization]
        range = [Product_Service]

    class has_policy(ObjectProperty):
        """Links an Organization to its capital deployment strategy."""
        domain = [Organization]
        range = [Capital_Allocation_Policy]

    class utilizes(ObjectProperty):
        """Connects an Organization to a financial instrument like debt."""
        domain = [Organization]
        range = [Financial_Instrument]

    class has_adviser(ObjectProperty):
        """Connects an Organization to a Person serving as an adviser."""
        domain = [Organization]
        range = [Person]

    class involves_person(ObjectProperty):
        """Connects a Corporate_Event to a Person involved in it."""
        domain = [Corporate_Event]
        range = [Person]

    #///////////////////////////////////////////////////////////////////////////////////////
    #//
    #//   Datatype Properties (Attributes of Entities)
    #//
    #///////////////////////////////////////////////////////////////////////////////////////

    class name(DataProperty, FunctionalProperty):
        """A string representing the name of an entity."""
        # This property can apply to any class (Thing)
        range = [str]

    class ticker_symbol(DataProperty, FunctionalProperty):
        """The stock market ticker symbol for a public company."""
        domain = [Organization]
        range = [str]

    class organization_type(DataProperty, FunctionalProperty):
        """The type of organization (e.g., Public Company, Regulatory Body)."""
        domain = [Organization]
        range = [str]

    class business_segment(DataProperty):
        """The business segment a product or service belongs to."""
        domain = [Product_Service]
        range = [str]

    class projected_growth_rate_CAGR(DataProperty):
        """The projected Compound Annual Growth Rate for a market."""
        domain = [Market]
        range = [float]

    class metric_name(DataProperty):
        """The name of the financial metric (e.g., Revenue, P/E Ratio)."""
        domain = [Financial_Metric]
        range = [str]

    class metric_value(DataProperty):
        """The numerical value of the financial metric."""
        domain = [Financial_Metric]
        range = [float]

    class fiscal_period(DataProperty):
        """The fiscal period the metric applies to (e.g., Q2 2025)."""
        domain = [Financial_Metric]
        range = [str]

    class event_date(DataProperty):
        """The date of a corporate event."""
        domain = [Corporate_Event]
        range = [datetime.date]

    class event_type(DataProperty, FunctionalProperty):
        """The type of event (e.g., Acquisition, Divestiture, Earnings Report)."""
        domain = [Corporate_Event]
        range = [str]

    class reason(DataProperty):
        """The reason for a corporate event (e.g., 'personal reasons', 'retirement')."""
        domain = [Corporate_Event]
        range = [str]

    # The 'role' and 'effective_since' properties are now deprecated and replaced by the 'Role' class.
    # class role(DataProperty):
    #     """The title or role of a person (e.g., CEO, CFO)."""
    #     domain = [Person]
    #     range = [str]

    # class effective_since(DataProperty):
    #     """The date the role became effective."""
    #     domain = [Person]
    #     range = [datetime.date]

    class role_title(DataProperty, FunctionalProperty):
        """The title of a role (e.g., 'CEO', 'CFO')."""
        domain = [Role]
        range = [str]

    class start_date(DataProperty, FunctionalProperty):
        """The date a role became effective."""
        domain = [Role]
        range = [datetime.date]

    class end_date(DataProperty, FunctionalProperty):
        """The date a role concluded."""
        domain = [Role]
        range = [datetime.date]

    class source(DataProperty):
        """The source of the information (e.g., a URL to a press release)."""
        domain = [Thing] # Can be applied to any individual
        range = [str]

    class advantage_type(DataProperty):
        """The type of competitive advantage (e.g., Network Effects)."""
        domain = [Competitive_Advantage]
        range = [str]

    class risk_type(DataProperty):
        """The category of risk (e.g., Operational, Legal, Macroeconomic)."""
        domain = [Risk_Factor]
        range = [str]

    class dividend_policy(DataProperty):
        """Description of the organization's dividend policy."""
        domain = [Capital_Allocation_Policy]
        range = [str]

    class interest_rate_terms(DataProperty):
        """Terms of the interest rate (e.g., 4.625% Fixed)."""
        domain = [Financial_Instrument]
        range = [str]

    class maturity_date(DataProperty):
        """The maturity date of a financial instrument."""
        domain = [Financial_Instrument]
        range = [datetime.date]

