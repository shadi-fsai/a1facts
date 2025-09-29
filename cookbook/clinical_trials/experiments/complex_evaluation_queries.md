# Complex Evaluation Queries for Clinical Trials Agent

This file contains 30 complex, multi-step queries designed to test the agent's ability to chain tool calls and synthesize information from different sources within the MCP server.

---

1.  **Query:** "Find recruiting clinical trials for metastatic melanoma, then search PubMed for recent review articles about the lead sponsor of the first trial found."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='metastatic melanoma', status='recruiting')`
        2.  (Agent extracts sponsor from the result, e.g., 'Bristol-Myers Squibb')
        3.  `acquire_tool` -> `PubMedTool.searchLiterature(query='Bristol-Myers Squibb review')`

2.  **Query:** "For the drug 'Verzenio' (abemaciclib), find its FDA-approved indications and then find any ongoing, recruiting clinical trials for those indications."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `FDATool.lookupDrug(drugName='abemaciclib', searchType='label')`
        2.  (Agent extracts indications, e.g., 'breast cancer')
        3.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='breast cancer', status='recruiting')`

3.  **Query:** "Calculate the BMI for a person who is 1.8 meters tall and weighs 85kg. Then, find recruiting clinical trials for conditions related to their resulting BMI category."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `MedicalCalculatorTool.calculateBmi(heightMeters=1.8, weightKg=85)`
        2.  (Agent determines BMI is ~26.2, i.e., 'Overweight')
        3.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='obesity', status='recruiting')`

4.  **Query:** "What is the ICD-10 code for 'Rheumatoid arthritis'? Then, find ongoing clinical trials for this condition."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `MedicalTerminologyTool.search(query='Rheumatoid arthritis')` (predicting tool name)
        2.  (Agent receives ICD-10 code and confirms condition)
        3.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='Rheumatoid arthritis', status='recruiting')`

5.  **Query:** "Find a completed Phase 3 trial for a CAR-T therapy. Then, search the NCBI bookshelf for literature on the mechanism of action of CAR-T cells."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='CAR-T', status='completed')`
        2.  (Agent confirms a trial is found)
        3.  `acquire_tool` -> `NCIBookshelfTool.search(query='CAR-T mechanism of action')` (predicting tool name)

6.  **Query:** "Look up 'Keytruda' on the FDA database to see who makes it. Then, find all PubMed articles from the last 2 years that mention its use in non-small cell lung cancer."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `FDATool.lookupDrug(drugName='Keytruda', searchType='general')`
        2.  (Agent identifies manufacturer)
        3.  `acquire_tool` -> `PubMedTool.searchLiterature(query='Keytruda non-small cell lung cancer', dateRange='2')`

7.  **Query:** "Find active clinical trials sponsored by 'BioNTech' and also search medRxiv for any recent pre-print articles they may have published."
    *   **Predicted Tool Chain (Parallel):**
        1.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(status='active')` -> (Agent filters by sponsor 'BioNTech')
        2.  `acquire_tool` -> `MedRxivTool.search(query='BioNTech')` (predicting tool name)

8.  **Query:** "Find the most recent completed trial for Alzheimer's disease. Take the NCT ID of that trial and find its entry on PubMed."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='Alzheimer disease', status='completed')`
        2.  (Agent extracts NCT ID, e.g., 'NCT01234567')
        3.  `acquire_tool` -> `PubMedTool.searchLiterature(query='NCT01234567')`

9.  **Query:** "List the warnings on the FDA label for 'Lenvima' (lenvatinib). Then, search for ongoing trials for any of the conditions mentioned in the indications."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `FDATool.lookupDrug(drugName='lenvatinib', searchType='label')`
        2.  (Agent extracts a condition from the indications, e.g., 'endometrial carcinoma')
        3.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='endometrial carcinoma', status='recruiting')`

10. **Query:** "Find a clinical trial related to DICOM imaging. Then, use the health topics tool to explain what DICOM is to a layperson."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='DICOM')`
        2.  `acquire_tool` -> `HealthTopicsTool.search(query='DICOM')` (predicting tool name)

---
*20 Additional Complex Queries*
---

11. **Query:** "Find the manufacturer of 'Xalkori' (crizotinib) using the FDA tool, then find all clinical trials they are currently sponsoring."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `FDATool.lookupDrug(drugName='crizotinib', searchType='general')`
        2.  (Agent extracts manufacturer, e.g., 'Pfizer')
        3.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='all', status='recruiting')` -> (Agent filters by sponsor 'Pfizer')

12. **Query:** "Search PubMed for recent articles on 'Osimertinib'. Take the first author of the top result and see if they are listed as an investigator in any recruiting clinical trials."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `PubMedTool.searchLiterature(query='Osimertinib')`
        2.  (Agent extracts author name)
        3.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='all')` -> (Agent performs text search for author name in results; this is a difficult query).

13. **Query:** "What are the known drug interactions for 'Paxlovid'? Then, find any clinical trials studying its use for conditions other than COVID-19, such as Long COVID."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `FDATool.lookupDrug(drugName='Paxlovid', searchType='label')`
        2.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='Long COVID')` -> (Agent filters for 'Paxlovid' or 'nirmatrelvir')

14. **Query:** "Find a completed clinical trial for 'Adcetris' (brentuximab vedotin). Then, look up its full FDA label information, focusing on dosage and administration."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='all', status='completed')` -> (Agent filters for 'Adcetris')
        2.  `acquire_tool` -> `FDATool.lookupDrug(drugName='brentuximab vedotin', searchType='label')`

15. **Query:** "Are there any open access articles on medRxiv about 'T-cell exhaustion'? If so, find any active clinical trials that mention this term."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `MedRxivTool.search(query='T-cell exhaustion', openAccess=true)` (predicting tool name)
        2.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='T-cell exhaustion', status='active')`

16. **Query:** "What is the mechanism of action described on the NCBI Bookshelf for 'monoclonal antibodies'? Then, find phase 3 trials for a specific monoclonal antibody like 'Dupilumab'."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `NCIBookshelfTool.search(query='monoclonal antibody mechanism of action')` (predicting tool name)
        2.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='Dupilumab', status='all')` -> (Agent filters for Phase 3)

17. **Query:** "Find the ICD-10 code for 'Glioblastoma'. Then, search PubMed for review articles on treatment options published in the last 3 years."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `MedicalTerminologyTool.search(query='Glioblastoma')` (predicting tool name)
        2.  `acquire_tool` -> `PubMedTool.searchLiterature(query='Glioblastoma treatment review', dateRange='3')`

18. **Query:** "A person is 5'5" and 150 lbs. After calculating their BMI, find health topics related to their BMI category using the health topics tool."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `MedicalCalculatorTool.calculateBmi()` (Agent converts units)
        2.  (Agent determines BMI category)
        3.  `acquire_tool` -> `HealthTopicsTool.search(query='Overweight health risks')` (predicting tool name)

19. **Query:** "Find a recruiting trial for pediatric acute lymphoblastic leukemia. Then, check the FDA database for any boxed warnings on drugs mentioned in that trial's intervention description."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='pediatric acute lymphoblastic leukemia', status='recruiting')`
        2.  (Agent extracts drug name from trial details)
        3.  `acquire_tool` -> `FDATool.lookupDrug(drugName='extracted_drug', searchType='adverse_events')`

20. **Query:** "Search for DICOM-related tools on the NCBI bookshelf, then find clinical trials that explicitly mention using DICOM for analysis in their study design."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `NCIBookshelfTool.search(query='DICOM')` (predicting tool name)
        2.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='DICOM')`

21. **Query:** "List the adverse reactions for 'Imbruvica' (ibrutinib). Then, search PubMed for articles discussing management of these specific reactions."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `FDATool.lookupDrug(drugName='ibrutinib', searchType='label')`
        2.  (Agent extracts a specific reaction, e.g., 'rash')
        3.  `acquire_tool` -> `PubMedTool.searchLiterature(query='ibrutinib rash management')`

22. **Query:** "Find a Phase 2 trial sponsored by 'AstraZeneca' that was completed in the last year. Then, search medRxiv for any pre-print results with the trial's NCT ID."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(status='completed')` -> (Agent filters by sponsor and date)
        2.  (Agent extracts NCT ID)
        3.  `acquire_tool` -> `MedRxivTool.search(query='NCT_ID')` (predicting tool name)

23. **Query:** "What are the indications for 'Opdivo' (nivolumab)? For the first indication, find the 5 most recent articles on PubMed."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `FDATool.lookupDrug(drugName='nivolumab', searchType='label')`
        2.  (Agent extracts first indication, e.g., 'Melanoma')
        3.  `acquire_tool` -> `PubMedTool.searchLiterature(query='Melanoma', maxResults=5)`

24. **Query:** "Find a trial that was terminated for safety reasons. Then, look up the FDA adverse event reports for the drug involved."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(status='terminated')` -> (Agent filters for 'safety')
        2.  (Agent extracts drug name)
        3.  `acquire_tool` -> `FDATool.lookupDrug(drugName='extracted_drug', searchType='adverse_events')`

25. **Query:** "What is the ICD-10 code for 'Parkinson's disease'? Then, find general information health topics on the condition."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `MedicalTerminologyTool.search(query='Parkinson\'s disease')` (predicting tool name)
        2.  `acquire_tool` -> `HealthTopicsTool.search(query='Parkinson\'s disease')` (predicting tool name)

26. **Query:** "Find a trial using 'CRISPR'. Then search the NCBI bookshelf for an introduction to CRISPR technology."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='CRISPR')`
        2.  `acquire_tool` -> `NCIBookshelfTool.search(query='CRISPR introduction')` (predicting tool name)

27. **Query:** "Look up the drug 'Stelara' (ustekinumab). Find its indications, and then search for recruiting trials for a different condition not on the label, like 'Lupus Nephritis', to find expansion trials."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `FDATool.lookupDrug(drugName='ustekinumab', searchType='label')`
        2.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='Lupus Nephritis', status='recruiting')` -> (Agent filters for 'ustekinumab')

28. **Query:** "Find a trial for a medical device used in cardiology, for example a 'stent'. Then search PubMed for performance reviews of that device type."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `ClinicalTrialsTool.searchTrials(condition='cardiology stent')`
        2.  `acquire_tool` -> `PubMedTool.searchLiterature(query='stent performance review')`

29. **Query:** "Calculate the BMI for a person who is 6'2" and 220 lbs. Then find PubMed articles related to health risks for their BMI category."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `MedicalCalculatorTool.calculateBmi()` (Agent converts units)
        2.  (Agent determines BMI category, e.g., 'Overweight')
        3.  `acquire_tool` -> `PubMedTool.searchLiterature(query='overweight health risks')`

30. **Query:** "Find the manufacturer of 'Skyrizi' (risankizumab). Then check for any pre-print articles on medRxiv from that manufacturer."
    *   **Predicted Tool Chain:**
        1.  `acquire_tool` -> `FDATool.lookupDrug(drugName='risankizumab', searchType='general')`
        2.  (Agent extracts manufacturer, e.g., 'AbbVie')
        3.  `acquire_tool` -> `MedRxivTool.search(query='AbbVie')` (predicting tool name)
