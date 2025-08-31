from owlready2 import *
from a1c import a1c
from company_ontology import onto
from knowledge_source import *

fmp_api_key = "xrXNUmkxWIszjiFRpVvYaIoJ9rcIizcO"
fmp = knowledge_source("fmp", 
                       "A",3, 
                       "https://financialmodelingprep.com/stable/profile", 
                       "https://site.financialmodelingprep.com/developer/docs/stable", 
                       fmp_api_key)

fortu1 = a1c("fortu1", onto, [fmp])
fortu1.printOntology()
print(fortu1)

