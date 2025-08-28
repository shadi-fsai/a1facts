from owlready2 import *
import datetime
from company_ontology import onto

# Organization: UnitedHealth Group
unh = onto.Organization("unitedhealth_group")
unh.name = "UnitedHealth Group"
unh.ticker_symbol = "UNH"
unh.organization_type = "Public Company"

# Person: Stephen J. Hemsley
hemsley = onto.Person("stephen_j_hemsley")
hemsley.name = "Stephen J. Hemsley"

# Person: Andrew Witty
witty = onto.Person("andrew_witty")
witty.name = "Andrew Witty"

# Role: CEO for Stephen J. Hemsley (May 2025 - ongoing)
ceo_role_hemsley_2025 = onto.Role("hemsley_ceo_2025")
ceo_role_hemsley_2025.held_at = unh
ceo_role_hemsley_2025.role_title = "CEO"
ceo_role_hemsley_2025.start_date = datetime.date(2025, 5, 13)
hemsley.has_role.append(ceo_role_hemsley_2025)

# Role: CEO for Andrew Witty (until May 2025)
ceo_role_witty = onto.Role("witty_ceo_until_2025")
ceo_role_witty.held_at = unh
ceo_role_witty.role_title = "CEO"
ceo_role_witty.end_date = datetime.date(2025, 5, 13)
witty.has_role.append(ceo_role_witty)

# Corporate Event: CEO Transition (May 2025)
ceo_transition_event = onto.Corporate_Event("unh_ceo_transition_2025")
ceo_transition_event.name = "UnitedHealth Group CEO Transition   Hemsley replaces Witty"
ceo_transition_event.event_type = "Leadership Change"
ceo_transition_event.event_date = datetime.date(2025, 5, 13)
ceo_transition_event.reason = "Andrew Witty stepped down for personal reasons."
ceo_transition_event.source = [
    "https://www.unitedhealthgroup.com/newsroom/2025/2025-05-13-uhg-announces-leadership-transition.html",
    "https://www.npr.org/2025/05/13/nx-s1-5396614/unitedhealth-group-terrible-year-replaces-ceo-andrew-witty",
    "https://www.pbs.org/newshour/health/unitedhealth-group-largest-health-insurer-in-u-s-withdraws-financial-outlook-for-2025"
]
ceo_transition_event.involves_person = [hemsley, witty]

# Relationships
unh.is_led_by = [hemsley]
unh.is_subject_of = [ceo_transition_event]

