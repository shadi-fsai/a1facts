from company_ontology import onto
import datetime

unh = onto.Organization("unitedhealth_group")
unh.name = "UnitedHealth Group"
unh.ticker_symbol = "UNH"
unh.organization_type = "Public Company"

# Person: Stephen J. Hemsley
hemsley = onto.Person("stephen_j_hemsley")
hemsley.name = ["Stephen J. Hemsley"]

# Person: Andrew Witty
witty = onto.Person("andrew_witty")
witty.name = ["Andrew Witty"]

# Role: CEO for Stephen J. Hemsley (May 2025 - [Ongoing])
ceo_role_hemsley_2 = onto.Role("HemsleyCEO2Role")
ceo_role_hemsley_2.held_at = unh
ceo_role_hemsley_2.role_title = "CEO"
ceo_role_hemsley_2.start_date = datetime.date(2006, 11, 1)
ceo_role_hemsley_2.end_date = datetime.date(2017, 8, 31)
hemsley.has_role.append(ceo_role_hemsley_2)


# Role: CEO for Stephen J. Hemsley (2006 - 2017)
ceo_role_hemsley_1 = onto.Role("HemsleyCEO1Role")
ceo_role_hemsley_1.held_at = unh
ceo_role_hemsley_1.role_title = "CEO"
ceo_role_hemsley_1.start_date = datetime.date(2006, 11, 1)
hemsley.has_role.append(ceo_role_hemsley_1)

# Role: Chairman (current)
chairman_role = onto.Role("hemsley_chairman")
chairman_role.role_title = "Chairman"
chairman_role.held_at = unh
hemsley.has_role.append(chairman_role)

# Role: CEO for Andrew Witty (until May 2025)
ceo_role_witty = onto.Role("witty_ceo_until_2025")
ceo_role_witty.role_title = "CEO"
ceo_role_witty.end_date = datetime.date(2025, 5, 13)
ceo_role_witty.held_at = unh
witty.has_role.append(ceo_role_witty)

# Corporate Event: CEO Transition (May 2025)
ceo_transition_event = onto.Corporate_Event("unh_ceo_transition_2025")
ceo_transition_event.name = ["UnitedHealth Group CEO Transition – Hemsley replaces Witty"]
ceo_transition_event.event_type = ["Leadership Change"]
ceo_transition_event.event_date = [datetime.date(2025, 5, 13)]
ceo_transition_event.reason = ["Andrew Witty stepped down for personal reasons."]
ceo_transition_event.source.extend([
    "https://www.unitedhealthgroup.com/newsroom/2025/2025-05-13-uhg-announces-leadership-transition.html",
    "https://www.foxbusiness.com/markets/unitedhealth-group-names-new-ceo",
    "https://www.beckerspayer.com/payer/we-have-gotten-things-wrong-unitedhealths-new-ceo-addresses-investors/",
    "https://www.unitedhealthgroup.com/content/dam/UHG/PDF/investors/2025/unh-reestablishes-full-year-outlook-and-reports-second-quarter-2025-results.pdf"
])
ceo_transition_event.involves_person.extend([hemsley, witty])

# Relationships
unh.is_led_by.append(hemsley)
unh.is_subject_of.append(ceo_transition_event)

