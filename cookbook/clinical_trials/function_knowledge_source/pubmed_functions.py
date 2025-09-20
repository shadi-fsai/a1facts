"""
PubMed API Functions
Provides access to biomedical literature and research publications
"""
import requests
import json
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET

def extract_study_type(title: str, abstract: str = "") -> str:
    """Extract study type from title and abstract."""
    combined_text = (title + " " + abstract).lower()
    
    if any(term in combined_text for term in ['randomized', 'rct', 'controlled trial']):
        return "Randomized Controlled Trial"
    elif any(term in combined_text for term in ['phase i', 'phase 1']):
        return "Phase I Trial"
    elif any(term in combined_text for term in ['phase ii', 'phase 2']):
        return "Phase II Trial"
    elif any(term in combined_text for term in ['phase iii', 'phase 3']):
        return "Phase III Trial"
    elif any(term in combined_text for term in ['cohort', 'prospective']):
        return "Cohort Study"
    elif any(term in combined_text for term in ['case-control', 'retrospective']):
        return "Case-Control Study"
    elif any(term in combined_text for term in ['meta-analysis', 'systematic review']):
        return "Meta-Analysis"
    else:
        return "Observational Study"

def search_pubmed_clinical_trials(drug_name: str, max_results: int = 10) -> Dict:
    """
    Search PubMed for clinical trial publications about a specific drug.
    
    Args:
        drug_name: Name of drug to search for (e.g., "semaglutide")
        max_results: Maximum number of results to return
        
    Returns:
        Dict containing publication data mapped to ontology structure
    """
    # First, search for article IDs
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        'db': 'pubmed',
        'term': f'{drug_name} AND ("clinical trial"[Publication Type] OR "randomized controlled trial"[Publication Type])',
        'retmax': max_results,
        'usehistory': 'y'
    }
    
    try:
        # Get article IDs
        search_response = requests.get(search_url, params=search_params, timeout=10)
        search_response.raise_for_status()
        
        # Parse XML response
        search_root = ET.fromstring(search_response.content)
        ids = [id_elem.text for id_elem in search_root.findall('.//Id')]
        
        if not ids:
            return {
                "publications": [],
                "data_releases": [],
                "source": f"PubMed search for {drug_name} clinical trials (no results)"
            }
        
        # Get detailed information for each article
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            'db': 'pubmed',
            'id': ','.join(ids),
            'retmode': 'xml'
        }
        
        fetch_response = requests.get(fetch_url, params=fetch_params, timeout=10)
        fetch_response.raise_for_status()
        
        # Parse detailed XML response
        fetch_root = ET.fromstring(fetch_response.content)
        
        # Map to ontology structure
        mapped_data = {
            "publications": [],
            "data_releases": [],
            "source": f"PubMed search for {drug_name} clinical trials"
        }
        
        for article in fetch_root.findall('.//PubmedArticle'):
            medline_citation = article.find('.//MedlineCitation')
            if medline_citation is not None:
                pmid = medline_citation.find('.//PMID')
                article_title = medline_citation.find('.//ArticleTitle')
                abstract = medline_citation.find('.//AbstractText')
                pub_date = medline_citation.find('.//PubDate')
                
                pmid_text = pmid.text if pmid is not None else ""
                title_text = article_title.text if article_title is not None else ""
                abstract_text = abstract.text if abstract is not None else ""
                
                if title_text:
                    # Create publication entry
                    publication = {
                        "pmid": pmid_text,
                        "title": title_text,
                        "study_type": extract_study_type(title_text, abstract_text),
                        "source": f"https://pubmed.ncbi.nlm.nih.gov/{pmid_text}/"
                    }
                    mapped_data["publications"].append(publication)
                    
                    # Create data release entry
                    year = ""
                    if pub_date is not None:
                        year_elem = pub_date.find('.//Year')
                        year = year_elem.text if year_elem is not None else ""
                    
                    data_release = {
                        "release_id": f"PMID-{pmid_text}",
                        "release_date": year,
                        "data_type": "Clinical Publication",
                        "source": f"https://pubmed.ncbi.nlm.nih.gov/{pmid_text}/"
                    }
                    mapped_data["data_releases"].append(data_release)
        
        return mapped_data
        
    except requests.RequestException as e:
        return {"error": f"PubMed API request failed: {str(e)}"}
    except ET.ParseError as e:
        return {"error": f"XML parsing error: {str(e)}"}

def search_pubmed_general(query: str, max_results: int = 10) -> Dict:
    """
    General PubMed search for any biomedical topic.
    
    Args:
        query: Search query (e.g., "obesity treatment")
        max_results: Maximum number of results to return
        
    Returns:
        Dict containing publication data
    """
    # First, search for article IDs
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        'db': 'pubmed',
        'term': query,
        'retmax': max_results,
        'usehistory': 'y'
    }
    
    try:
        # Get article IDs
        search_response = requests.get(search_url, params=search_params, timeout=10)
        search_response.raise_for_status()
        
        # Parse XML response
        search_root = ET.fromstring(search_response.content)
        ids = [id_elem.text for id_elem in search_root.findall('.//Id')]
        
        if not ids:
            return {"publications": [], "source": f"PubMed search for '{query}' (no results)"}
        
        # Get detailed information for each article
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            'db': 'pubmed',
            'id': ','.join(ids),
            'retmode': 'xml'
        }
        
        fetch_response = requests.get(fetch_url, params=fetch_params, timeout=10)
        fetch_response.raise_for_status()
        
        # Parse detailed XML response
        fetch_root = ET.fromstring(fetch_response.content)
        
        publications = []
        for article in fetch_root.findall('.//PubmedArticle'):
            medline_citation = article.find('.//MedlineCitation')
            if medline_citation is not None:
                pmid = medline_citation.find('.//PMID')
                article_title = medline_citation.find('.//ArticleTitle')
                abstract = medline_citation.find('.//AbstractText')
                
                pmid_text = pmid.text if pmid is not None else ""
                title_text = article_title.text if article_title is not None else ""
                abstract_text = abstract.text if abstract is not None else ""
                
                if title_text:
                    publication = {
                        "pmid": pmid_text,
                        "title": title_text,
                        "abstract": abstract_text[:500] + "..." if len(abstract_text) > 500 else abstract_text,
                        "study_type": extract_study_type(title_text, abstract_text),
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid_text}/"
                    }
                    publications.append(publication)
        
        return {
            "publications": publications,
            "source": f"PubMed search for '{query}'"
        }
        
    except requests.RequestException as e:
        return {"error": f"PubMed API request failed: {str(e)}"}
    except ET.ParseError as e:
        return {"error": f"XML parsing error: {str(e)}"}

def search_pubmed_by_author(author: str, max_results: int = 10) -> Dict:
    """
    Search PubMed publications by author name.
    
    Args:
        author: Author name (e.g., "Smith J")
        max_results: Maximum number of results to return
        
    Returns:
        Dict containing publication data
    """
    return search_pubmed_general(f'"{author}"[Author]', max_results)

def query_pubmed_research(query: str) -> str:
    """
    Main query function for PubMed knowledge source.
    This function is called by the a1facts knowledge acquirer.
    
    Args:
        query: Natural language query about biomedical literature
        
    Returns:
        JSON string with structured publication data
    """
    query_lower = query.lower()
    
    # Check for specific search types
    if any(term in query_lower for term in ['clinical trial', 'trial', 'study']):
        # Extract potential drug name
        drugs = ['tirzepatide', 'semaglutide', 'maritide', 'vk2735', 'pemvidutide', 'glp-1']
        for drug in drugs:
            if drug in query_lower:
                result = search_pubmed_clinical_trials(drug)
                return json.dumps(result, indent=2)
    
    if any(term in query_lower for term in ['author:', 'by author', 'publications by']):
        # Extract author name (simplified approach)
        words = query.split()
        author_idx = -1
        for i, word in enumerate(words):
            if word.lower() in ['author:', 'by', 'from']:
                author_idx = i + 1
                break
        
        if author_idx > 0 and author_idx < len(words):
            author = ' '.join(words[author_idx:author_idx+2])  # Take next 2 words as author name
            result = search_pubmed_by_author(author)
            return json.dumps(result, indent=2)
    
    # Default to general search
    result = search_pubmed_general(query, max_results=10)
    return json.dumps(result, indent=2)
