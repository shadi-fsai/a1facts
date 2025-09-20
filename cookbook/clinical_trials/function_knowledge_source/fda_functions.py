"""
FDA API Functions
Provides access to FDA databases including FAERS (adverse events) and drug approvals
"""
import requests
import json
from typing import Dict, List, Optional

def categorize_adverse_event(reaction: str) -> str:
    """Categorize adverse event by severity."""
    serious_reactions = [
        'death', 'died', 'fatal', 'hospitalization', 'disability', 'congenital',
        'life threatening', 'serious'
    ]
    
    reaction_lower = reaction.lower()
    if any(term in reaction_lower for term in serious_reactions):
        return "Serious"
    else:
        return "Non-serious"

def search_fda_adverse_events(drug_name: str, max_results: int = 10) -> Dict:
    """
    Search FDA FAERS database for adverse events related to a drug.
    
    Args:
        drug_name: Name of drug to search for (e.g., "semaglutide")
        max_results: Maximum number of results to return
        
    Returns:
        Dict containing adverse event data mapped to ontology structure
    """
    url = "https://api.fda.gov/drug/event.json"
    params = {
        'search': f'patient.drug.medicinalproduct:"{drug_name}"',
        'limit': max_results
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_data = response.json()
        
        # Map to ontology structure
        mapped_data = {
            "adverse_events": [],
            "source": f"https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:\"{drug_name}\""
        }
        
        for result in raw_data.get('results', []):
            # Extract reactions
            reactions = result.get('patient', {}).get('reaction', [])
            
            for reaction in reactions:
                reaction_term = reaction.get('reactionmeddrapt', '')
                if reaction_term:
                    adverse_event = {
                        "adverse_event_id": result.get('safetyreportid', ''),
                        "event_type": reaction_term,
                        "severity": categorize_adverse_event(reaction_term),
                        "source": f"FDA FAERS Report {result.get('safetyreportid', '')}"
                    }
                    mapped_data["adverse_events"].append(adverse_event)
        
        return mapped_data
        
    except requests.RequestException as e:
        return {"error": f"FDA API request failed: {str(e)}"}

def search_fda_drug_approvals(drug_name: str, max_results: int = 10) -> Dict:
    """
    Search FDA drug approval database for information about a drug.
    
    Args:
        drug_name: Name of drug to search for
        max_results: Maximum number of results to return
        
    Returns:
        Dict containing drug approval data
    """
    url = "https://api.fda.gov/drug/drugsfda.json"
    params = {
        'search': f'openfda.brand_name:"{drug_name}" OR openfda.generic_name:"{drug_name}"',
        'limit': max_results
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"FDA API request failed: {str(e)}"}

def search_fda_recalls(drug_name: str, max_results: int = 10) -> Dict:
    """
    Search FDA drug recall database.
    
    Args:
        drug_name: Name of drug to search for
        max_results: Maximum number of results to return
        
    Returns:
        Dict containing drug recall data
    """
    url = "https://api.fda.gov/drug/enforcement.json"
    params = {
        'search': f'product_description:"{drug_name}"',
        'limit': max_results
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"FDA API request failed: {str(e)}"}

def search_fda_labeling(drug_name: str, max_results: int = 10) -> Dict:
    """
    Search FDA drug labeling database for prescribing information.
    
    Args:
        drug_name: Name of drug to search for
        max_results: Maximum number of results to return
        
    Returns:
        Dict containing drug labeling data
    """
    url = "https://api.fda.gov/drug/label.json"
    params = {
        'search': f'openfda.brand_name:"{drug_name}" OR openfda.generic_name:"{drug_name}"',
        'limit': max_results
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"FDA API request failed: {str(e)}"}

def query_fda_databases(query: str) -> str:
    """
    Main query function for FDA knowledge source.
    This function is called by the a1facts knowledge acquirer.
    
    Args:
        query: Natural language query about FDA data
        
    Returns:
        JSON string with structured FDA data
    """
    query_lower = query.lower()
    
    # Determine search strategy based on query content
    if any(term in query_lower for term in ['adverse', 'side effect', 'reaction', 'safety']):
        # Extract potential drug name
        drugs = ['tirzepatide', 'semaglutide', 'maritide', 'vk2735', 'pemvidutide', 'glp-1', 'mounjaro', 'ozempic', 'wegovy']
        for drug in drugs:
            if drug in query_lower:
                result = search_fda_adverse_events(drug)
                return json.dumps(result, indent=2)
        
        # Default adverse event search
        result = search_fda_adverse_events(query, max_results=10)
        return json.dumps(result, indent=2)
    
    elif any(term in query_lower for term in ['approval', 'approved', 'authorization']):
        # Extract potential drug name
        drugs = ['tirzepatide', 'semaglutide', 'maritide', 'vk2735', 'pemvidutide']
        for drug in drugs:
            if drug in query_lower:
                result = search_fda_drug_approvals(drug)
                return json.dumps(result, indent=2)
    
    elif any(term in query_lower for term in ['recall', 'withdrawn']):
        # Extract potential drug name
        drugs = ['tirzepatide', 'semaglutide', 'maritide', 'vk2735', 'pemvidutide']
        for drug in drugs:
            if drug in query_lower:
                result = search_fda_recalls(drug)
                return json.dumps(result, indent=2)
    
    elif any(term in query_lower for term in ['label', 'prescribing', 'indication']):
        # Extract potential drug name
        drugs = ['tirzepatide', 'semaglutide', 'maritide', 'vk2735', 'pemvidutide']
        for drug in drugs:
            if drug in query_lower:
                result = search_fda_labeling(drug)
                return json.dumps(result, indent=2)
    
    # Default to adverse events search
    result = search_fda_adverse_events(query, max_results=10)
    return json.dumps(result, indent=2)
