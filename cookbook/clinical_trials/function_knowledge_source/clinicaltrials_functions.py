"""
ClinicalTrials.gov API Functions
Provides access to the official clinical trials database
"""
import requests
import json
from typing import Dict, List, Optional

def _extract_phase(phases_list):
    """Extract phase information from design module."""
    if not phases_list:
        return "Not Applicable"
    if isinstance(phases_list, list) and phases_list:
        return phases_list[0]
    return str(phases_list)

def _classify_sponsor_type(sponsor_name):
    """Classify sponsor type based on name."""
    sponsor_lower = sponsor_name.lower()
    if any(term in sponsor_lower for term in ['university', 'hospital', 'medical center', 'institute']):
        return "Academic"
    elif any(term in sponsor_lower for term in ['nih', 'government', 'health department']):
        return "Government"
    else:
        return "Pharmaceutical"

def search_trials_by_condition(condition: str, max_results: int = 20) -> Dict:
    """
    Search clinical trials by medical condition and map to ontology structure.
    
    Args:
        condition: Medical condition (e.g., "diabetes", "obesity")
        max_results: Maximum number of results to return
        
    Returns:
        Dict containing structured trial data mapped to trials.yaml ontology
    """
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        'query.cond': condition,
        'pageSize': max_results,
        'format': 'json'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_data = response.json()
        
        # Map to ontology structure
        mapped_data = {
            "clinical_trials": [],
            "drugs": [],
            "sponsors": [],
            "endpoints": [],
            "source": f"https://clinicaltrials.gov/api/v2/studies?query.cond={condition}"
        }
        
        for study in raw_data.get('studies', []):
            protocol = study.get('protocolSection', {})
            identification = protocol.get('identificationModule', {})
            design = protocol.get('designModule', {})
            status = protocol.get('statusModule', {})
            sponsor_info = protocol.get('sponsorCollaboratorsModule', {})
            arms = protocol.get('armsInterventionsModule', {})
            outcomes = protocol.get('outcomesModule', {})
            
            # Extract trial data
            trial_id = identification.get('nctId', '')
            if trial_id:
                # ClinicalTrial entity
                clinical_trial = {
                    "trial_id": trial_id,
                    "phase": _extract_phase(design.get('phases', [])),
                    "source": f"https://clinicaltrials.gov/study/{trial_id}"
                }
                mapped_data["clinical_trials"].append(clinical_trial)
                
                # Sponsor entity
                lead_sponsor = sponsor_info.get('leadSponsor', {})
                if lead_sponsor.get('name'):
                    sponsor = {
                        "name": lead_sponsor.get('name'),
                        "sponsor_type": _classify_sponsor_type(lead_sponsor.get('name', '')),
                        "source": f"https://clinicaltrials.gov/study/{trial_id}"
                    }
                    mapped_data["sponsors"].append(sponsor)
                
                # Drug entities from interventions
                interventions = arms.get('interventions', [])
                for intervention in interventions:
                    if intervention.get('type') == 'Drug':
                        drug = {
                            "name": intervention.get('name', ''),
                            "source": f"https://clinicaltrials.gov/study/{trial_id}"
                        }
                        if drug["name"]:
                            mapped_data["drugs"].append(drug)
                
                # Endpoint entities
                primary_outcomes = outcomes.get('primaryOutcomes', [])
                for i, outcome in enumerate(primary_outcomes):
                    endpoint = {
                        "endpoint_id": f"{trial_id}-P{i+1}",
                        "endpoint_type": "Primary",
                        "status": "Ongoing",  # Default, would need trial results to determine
                        "description": outcome.get('measure', ''),
                        "source": f"https://clinicaltrials.gov/study/{trial_id}"
                    }
                    mapped_data["endpoints"].append(endpoint)
        
        return mapped_data
        
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

def search_trials_by_drug(drug_name: str, max_results: int = 20) -> Dict:
    """
    Search clinical trials by drug/intervention name.
    
    Args:
        drug_name: Name of drug or intervention (e.g., "tirzepatide", "semaglutide")
        max_results: Maximum number of results to return
        
    Returns:
        Dict containing trial data from ClinicalTrials.gov
    """
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        'query.intr': drug_name,
        'pageSize': max_results,
        'format': 'json'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

def search_trials_by_sponsor(sponsor: str, max_results: int = 20) -> Dict:
    """
    Search clinical trials by sponsor organization.
    
    Args:
        sponsor: Sponsor name (e.g., "Eli Lilly", "Novo Nordisk")
        max_results: Maximum number of results to return
        
    Returns:
        Dict containing trial data from ClinicalTrials.gov
    """
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        'query.lead': sponsor,
        'pageSize': max_results,
        'format': 'json'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

def get_trial_details(nct_id: str) -> Dict:
    """
    Get detailed information for a specific clinical trial.
    
    Args:
        nct_id: NCT number (e.g., "NCT05198934")
        
    Returns:
        Dict containing detailed trial information
    """
    url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

def search_recent_trials(days_back: int = 30, max_results: int = 20) -> Dict:
    """
    Search for recently updated clinical trials.
    
    Args:
        days_back: Number of days to look back
        max_results: Maximum number of results to return
        
    Returns:
        Dict containing recently updated trials
    """
    from datetime import datetime, timedelta
    
    cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        'query.lastUpdatePost': cutoff_date,
        'pageSize': max_results,
        'format': 'json'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

def query_clinicaltrials_gov(query: str) -> str:
    """
    Main query function for ClinicalTrials.gov knowledge source.
    This function is called by the a1facts knowledge acquirer.
    
    Args:
        query: Natural language query about clinical trials
        
    Returns:
        JSON string with structured clinical trial data
    """
    import re
    
    query_lower = query.lower()
    
    # Determine search strategy based on query content
    if 'nct' in query_lower:
        # Extract NCT ID and get specific trial details
        nct_match = re.search(r'nct\d+', query_lower)
        if nct_match:
            nct_id = nct_match.group(0).upper()
            result = get_trial_details(nct_id)
            return json.dumps(result, indent=2)
    
    # Check for specific search types
    if any(term in query_lower for term in ['sponsor', 'company', 'pharma']):
        # Extract potential sponsor name
        sponsors = ['eli lilly', 'novo nordisk', 'amgen', 'viking', 'altimmune']
        for sponsor in sponsors:
            if sponsor in query_lower:
                result = search_trials_by_sponsor(sponsor)
                return json.dumps(result, indent=2)
    
    if any(term in query_lower for term in ['drug', 'medication', 'treatment']):
        # Extract potential drug name
        drugs = ['tirzepatide', 'semaglutide', 'maritide', 'vk2735', 'pemvidutide', 'glp-1']
        for drug in drugs:
            if drug in query_lower:
                result = search_trials_by_drug(drug)
                return json.dumps(result, indent=2)
    
    # Default to condition-based search
    result = search_trials_by_condition(query, max_results=20)
    return json.dumps(result, indent=2)
