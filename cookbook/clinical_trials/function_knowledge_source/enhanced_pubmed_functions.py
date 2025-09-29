"""
Enhanced PubMed Functions using BioPython
Replaces existing pubmed_functions.py with professional-grade implementation

KEY IMPROVEMENTS:
- Professional XML parsing with Bio.Entrez
- MeSH term integration for precision
- Rate limiting to prevent API blocks
- Related article discovery
- Enhanced data extraction and classification
- 15+ functions vs 5 basic functions (3x capability)
"""

from Bio import Entrez
import time
import json
import re
import datetime
from typing import Dict as DictType, List as ListType, Optional as OptionalType

# Set email for NCBI API (required by NCBI)
Entrez.email = "research@a1facts.com"

def enhanced_search_pubmed_clinical_trials(query: str, max_results: int = 20) -> DictType:
    """
    Advanced PubMed search using BioPython with MeSH terms and related articles.
    
    MAJOR IMPROVEMENTS over current function:
    - Professional XML parsing with Bio.Entrez
    - MeSH term integration for precision
    - Rate limiting to prevent API blocks
    - Related article discovery
    - Structured data extraction
    """
    try:
        # Advanced search with MeSH terms for clinical trials
        search_handle = Entrez.esearch(
            db="pubmed",
            term=f'{query} AND ("clinical trial"[Publication Type] OR "randomized controlled trial"[Publication Type] OR "controlled clinical trial"[Publication Type])',
            retmax=max_results,
            usehistory="y"
        )
        search_results = Entrez.read(search_handle)
        search_handle.close()
        
        if not search_results["IdList"]:
            return {"publications": [], "source": "PubMed via BioPython", "query": query}
        
        # Batch fetch detailed information
        fetch_handle = Entrez.efetch(
            db="pubmed",
            id=search_results["IdList"],
            rettype="medline",
            retmode="xml"
        )
        
        records = Entrez.read(fetch_handle)
        fetch_handle.close()
        
        # Enhanced data mapping
        publications = []
        for record in records["PubmedArticle"]:
            article = record["MedlineCitation"]["Article"]
            
            pub_data = {
                "pmid": record["MedlineCitation"]["PMID"],
                "title": article.get("ArticleTitle", ""),
                "abstract": _extract_abstract(article.get("Abstract", {})),
                "journal": article.get("Journal", {}).get("Title", ""),
                "publication_date": _extract_publication_date(article.get("Journal", {}).get("JournalIssue", {})),
                "authors": _extract_authors(article.get("AuthorList", [])),
                "mesh_terms": _extract_mesh_terms(record["MedlineCitation"].get("MeshHeadingList", [])),
                "study_type": _classify_study_type(article.get("ArticleTitle", ""), article.get("Abstract", {})),
                "keywords": _extract_keywords(record["MedlineCitation"].get("KeywordList", [])),
                "doi": _extract_doi(article.get("ELocationID", [])),
                "source": f"https://pubmed.ncbi.nlm.nih.gov/{record['MedlineCitation']['PMID']}/"
            }
            publications.append(pub_data)
        
        # Rate limiting to be respectful to NCBI (3 requests per second max)
        time.sleep(0.34)
        
        return {
            "publications": publications,
            "total_found": int(search_results["Count"]),
            "source": "PubMed via BioPython Enhanced API",
            "query": query,
            "api_version": "BioPython with MeSH integration"
        }
        
    except Exception as e:
        return {"error": str(e), "source": "PubMed via BioPython", "query": query}

def get_related_articles(pmid: str, max_related: int = 10) -> DictType:
    """
    Find related articles using BioPython's elink - NEW CAPABILITY!
    This function doesn't exist in your current setup.
    """
    try:
        link_handle = Entrez.elink(
            dbfrom="pubmed",
            db="pubmed", 
            id=pmid,
            linkname="pubmed_pubmed_citedin"
        )
        link_results = Entrez.read(link_handle)
        link_handle.close()
        
        related_ids = []
        if link_results[0]["LinkSetDb"]:
            for link_db in link_results[0]["LinkSetDb"]:
                if link_db["LinkName"] == "pubmed_pubmed_citedin":
                    related_ids = [link["Id"] for link in link_db["Link"][:max_related]]
        
        if not related_ids:
            return {"related_articles": [], "source": "PubMed elink via BioPython"}
        
        # Fetch details for related articles
        fetch_handle = Entrez.efetch(
            db="pubmed",
            id=related_ids,
            rettype="medline", 
            retmode="xml"
        )
        records = Entrez.read(fetch_handle)
        fetch_handle.close()
        
        related_articles = []
        for record in records["PubmedArticle"]:
            article = record["MedlineCitation"]["Article"]
            related_articles.append({
                "pmid": record["MedlineCitation"]["PMID"],
                "title": article.get("ArticleTitle", ""),
                "journal": article.get("Journal", {}).get("Title", ""),
                "authors": _extract_authors(article.get("AuthorList", []))[:3],  # First 3 authors
                "publication_date": _extract_publication_date(article.get("Journal", {}).get("JournalIssue", {})),
                "relevance": "cited_by_original",
                "source": f"https://pubmed.ncbi.nlm.nih.gov/{record['MedlineCitation']['PMID']}/"
            })
        
        time.sleep(0.34)
        return {
            "related_articles": related_articles,
            "source": "PubMed elink via BioPython",
            "original_pmid": pmid
        }
    except Exception as e:
        return {"error": str(e), "source": "PubMed elink", "pmid": pmid}

def search_mesh_terms(term: str) -> DictType:
    """
    Search MeSH database for controlled vocabulary terms - NEW CAPABILITY!
    Essential for precision medical searching.
    """
    try:
        search_handle = Entrez.esearch(db="mesh", term=term, retmax=20)
        search_results = Entrez.read(search_handle)
        search_handle.close()
        
        if not search_results["IdList"]:
            return {"mesh_terms": [], "source": "MeSH via BioPython", "query": term}
        
        # Fetch MeSH term details
        fetch_handle = Entrez.efetch(db="mesh", id=search_results["IdList"], retmode="xml")
        mesh_records = Entrez.read(fetch_handle)
        fetch_handle.close()
        
        mesh_terms = []
        for record in mesh_records:
            if "DescriptorRecord" in record:
                descriptor = record["DescriptorRecord"]
                mesh_terms.append({
                    "mesh_id": descriptor.get("DescriptorUI", ""),
                    "term": descriptor.get("DescriptorName", {}).get("String", ""),
                    "definition": descriptor.get("Annotation", ""),
                    "tree_numbers": [tn.get("String", "") for tn in descriptor.get("TreeNumberList", {}).get("TreeNumber", [])]
                })
        
        time.sleep(0.34)
        return {
            "mesh_terms": mesh_terms,
            "source": "MeSH Database via BioPython",
            "query": term
        }
        
    except Exception as e:
        return {"error": str(e), "source": "MeSH Database", "query": term}

def get_database_info() -> DictType:
    """
    Get PubMed database information - NEW CAPABILITY!
    Useful for understanding search capabilities and database status.
    """
    try:
        info_handle = Entrez.einfo(db="pubmed")
        info_record = Entrez.read(info_handle)
        info_handle.close()
        
        return {
            "database_name": info_record["DbInfo"]["DbName"],
            "description": info_record["DbInfo"]["Description"], 
            "record_count": info_record["DbInfo"]["Count"],
            "last_update": info_record["DbInfo"]["LastUpdate"],
            "available_fields": [field["Name"] for field in info_record["DbInfo"]["FieldList"][:20]],  # First 20 fields
            "search_field_count": len(info_record["DbInfo"]["FieldList"]),
            "source": "PubMed einfo via BioPython"
        }
    except Exception as e:
        return {"error": str(e), "source": "PubMed einfo"}

def search_by_author(author_name: str, max_results: int = 20) -> DictType:
    """
    Search publications by specific author - ENHANCED CAPABILITY!
    Much more robust than basic string matching.
    """
    try:
        # Use proper author field search
        search_handle = Entrez.esearch(
            db="pubmed",
            term=f'{author_name}[Author]',
            retmax=max_results,
            sort="relevance"
        )
        search_results = Entrez.read(search_handle)
        search_handle.close()
        
        if not search_results["IdList"]:
            return {"publications": [], "source": "PubMed Author Search", "author": author_name}
        
        # Fetch publication details
        fetch_handle = Entrez.efetch(
            db="pubmed",
            id=search_results["IdList"],
            rettype="medline",
            retmode="xml"
        )
        records = Entrez.read(fetch_handle)
        fetch_handle.close()
        
        publications = []
        for record in records["PubmedArticle"]:
            article = record["MedlineCitation"]["Article"]
            publications.append({
                "pmid": record["MedlineCitation"]["PMID"],
                "title": article.get("ArticleTitle", ""),
                "journal": article.get("Journal", {}).get("Title", ""),
                "publication_date": _extract_publication_date(article.get("Journal", {}).get("JournalIssue", {})),
                "authors": _extract_authors(article.get("AuthorList", [])),
                "study_type": _classify_study_type(article.get("ArticleTitle", ""), article.get("Abstract", {})),
                "source": f"https://pubmed.ncbi.nlm.nih.gov/{record['MedlineCitation']['PMID']}/"
            })
        
        time.sleep(0.34)
        return {
            "publications": publications,
            "total_found": int(search_results["Count"]),
            "author_searched": author_name,
            "source": "PubMed Author Search via BioPython"
        }
        
    except Exception as e:
        return {"error": str(e), "source": "PubMed Author Search", "author": author_name}

def search_by_journal(journal_name: str, keywords: str = "", max_results: int = 20) -> DictType:
    """
    Search publications in specific journal - ENHANCED CAPABILITY!
    More precise journal matching and optional keyword filtering.
    """
    try:
        # Build search query
        if keywords:
            search_term = f'("{journal_name}"[Journal]) AND ({keywords})'
        else:
            search_term = f'"{journal_name}"[Journal]'
        
        search_handle = Entrez.esearch(
            db="pubmed",
            term=search_term,
            retmax=max_results,
            sort="pub date"
        )
        search_results = Entrez.read(search_handle)
        search_handle.close()
        
        if not search_results["IdList"]:
            return {
                "publications": [], 
                "source": "PubMed Journal Search", 
                "journal": journal_name,
                "keywords": keywords
            }
        
        # Fetch publication details
        fetch_handle = Entrez.efetch(
            db="pubmed",
            id=search_results["IdList"],
            rettype="medline",
            retmode="xml"
        )
        records = Entrez.read(fetch_handle)
        fetch_handle.close()
        
        publications = []
        for record in records["PubmedArticle"]:
            article = record["MedlineCitation"]["Article"]
            publications.append({
                "pmid": record["MedlineCitation"]["PMID"],
                "title": article.get("ArticleTitle", ""),
                "journal": article.get("Journal", {}).get("Title", ""),
                "publication_date": _extract_publication_date(article.get("Journal", {}).get("JournalIssue", {})),
                "authors": _extract_authors(article.get("AuthorList", []))[:5],  # First 5 authors
                "abstract": _extract_abstract(article.get("Abstract", {}))[:500] + "..." if len(_extract_abstract(article.get("Abstract", {}))) > 500 else _extract_abstract(article.get("Abstract", {})),
                "source": f"https://pubmed.ncbi.nlm.nih.gov/{record['MedlineCitation']['PMID']}/"
            })
        
        time.sleep(0.34)
        return {
            "publications": publications,
            "total_found": int(search_results["Count"]),
            "journal_searched": journal_name,
            "keywords": keywords,
            "source": "PubMed Journal Search via BioPython"
        }
        
    except Exception as e:
        return {"error": str(e), "source": "PubMed Journal Search", "journal": journal_name}

def search_drug_mechanism_of_action(drug_name: str, max_results: int = 15) -> DictType:
    """
    Search for mechanism of action studies for specific drugs - NEW CAPABILITY!
    Focused on MOA research critical for competitive intelligence.
    """
    try:
        # Focused search for mechanism of action
        search_term = f'{drug_name} AND ("mechanism of action"[Title/Abstract] OR "pharmacodynamics"[Title/Abstract] OR "molecular mechanism"[Title/Abstract] OR "mode of action"[Title/Abstract])'
        
        search_handle = Entrez.esearch(
            db="pubmed",
            term=search_term,
            retmax=max_results,
            sort="relevance"
        )
        search_results = Entrez.read(search_handle)
        search_handle.close()
        
        if not search_results["IdList"]:
            return {"publications": [], "source": "PubMed MOA Search", "drug": drug_name}
        
        # Fetch publication details
        fetch_handle = Entrez.efetch(
            db="pubmed",
            id=search_results["IdList"],
            rettype="medline",
            retmode="xml"
        )
        records = Entrez.read(fetch_handle)
        fetch_handle.close()
        
        publications = []
        for record in records["PubmedArticle"]:
            article = record["MedlineCitation"]["Article"]
            abstract = _extract_abstract(article.get("Abstract", {}))
            
            publications.append({
                "pmid": record["MedlineCitation"]["PMID"],
                "title": article.get("ArticleTitle", ""),
                "journal": article.get("Journal", {}).get("Title", ""),
                "publication_date": _extract_publication_date(article.get("Journal", {}).get("JournalIssue", {})),
                "authors": _extract_authors(article.get("AuthorList", []))[:3],
                "abstract": abstract,
                "mesh_terms": _extract_mesh_terms(record["MedlineCitation"].get("MeshHeadingList", [])),
                "mechanism_keywords": _extract_mechanism_keywords(article.get("ArticleTitle", ""), abstract),
                "study_type": _classify_study_type(article.get("ArticleTitle", ""), article.get("Abstract", {})),
                "source": f"https://pubmed.ncbi.nlm.nih.gov/{record['MedlineCitation']['PMID']}/"
            })
        
        time.sleep(0.34)
        return {
            "publications": publications,
            "total_found": int(search_results["Count"]),
            "drug_searched": drug_name,
            "search_focus": "mechanism_of_action",
            "source": "PubMed MOA Search via BioPython"
        }
        
    except Exception as e:
        return {"error": str(e), "source": "PubMed MOA Search", "drug": drug_name}

def search_drug_safety_profile(drug_name: str, max_results: int = 20) -> DictType:
    """
    Search for drug safety and adverse event publications - NEW CAPABILITY!
    Critical for competitive safety intelligence.
    """
    try:
        # Safety-focused search
        search_term = f'{drug_name} AND ("adverse events"[Title/Abstract] OR "side effects"[Title/Abstract] OR "toxicity"[Title/Abstract] OR "safety profile"[Title/Abstract] OR "tolerability"[Title/Abstract])'
        
        search_handle = Entrez.esearch(
            db="pubmed",
            term=search_term,
            retmax=max_results,
            sort="pub date"
        )
        search_results = Entrez.read(search_handle)
        search_handle.close()
        
        if not search_results["IdList"]:
            return {"publications": [], "source": "PubMed Safety Search", "drug": drug_name}
        
        # Fetch publication details
        fetch_handle = Entrez.efetch(
            db="pubmed",
            id=search_results["IdList"],
            rettype="medline",
            retmode="xml"
        )
        records = Entrez.read(fetch_handle)
        fetch_handle.close()
        
        publications = []
        for record in records["PubmedArticle"]:
            article = record["MedlineCitation"]["Article"]
            abstract = _extract_abstract(article.get("Abstract", {}))
            
            publications.append({
                "pmid": record["MedlineCitation"]["PMID"],
                "title": article.get("ArticleTitle", ""),
                "journal": article.get("Journal", {}).get("Title", ""),
                "publication_date": _extract_publication_date(article.get("Journal", {}).get("JournalIssue", {})),
                "authors": _extract_authors(article.get("AuthorList", []))[:3],
                "abstract": abstract,
                "safety_keywords": _extract_safety_keywords(article.get("ArticleTitle", ""), abstract),
                "study_type": _classify_study_type(article.get("ArticleTitle", ""), article.get("Abstract", {})),
                "mesh_terms": _extract_mesh_terms(record["MedlineCitation"].get("MeshHeadingList", [])),
                "source": f"https://pubmed.ncbi.nlm.nih.gov/{record['MedlineCitation']['PMID']}/"
            })
        
        time.sleep(0.34)
        return {
            "publications": publications,
            "total_found": int(search_results["Count"]),
            "drug_searched": drug_name,
            "search_focus": "safety_profile",
            "source": "PubMed Safety Search via BioPython"
        }
        
    except Exception as e:
        return {"error": str(e), "source": "PubMed Safety Search", "drug": drug_name}

def get_clinical_trial_publications(nct_id: str) -> DictType:
    """
    Find publications related to specific clinical trial NCT ID - NEW CAPABILITY!
    Links clinical trials to their published results.
    """
    try:
        # Search for publications mentioning the NCT ID
        search_handle = Entrez.esearch(
            db="pubmed",
            term=f'{nct_id}[Text Word]',
            retmax=50
        )
        search_results = Entrez.read(search_handle)
        search_handle.close()
        
        if not search_results["IdList"]:
            return {"publications": [], "source": "PubMed Clinical Trial Search", "nct_id": nct_id}
        
        # Fetch publication details
        fetch_handle = Entrez.efetch(
            db="pubmed",
            id=search_results["IdList"],
            rettype="medline",
            retmode="xml"
        )
        records = Entrez.read(fetch_handle)
        fetch_handle.close()
        
        publications = []
        for record in records["PubmedArticle"]:
            article = record["MedlineCitation"]["Article"]
            abstract = _extract_abstract(article.get("Abstract", {}))
            
            # Check if NCT ID is actually mentioned in title/abstract
            title_abstract = (article.get("ArticleTitle", "") + " " + abstract).upper()
            if nct_id.upper() in title_abstract:
                publications.append({
                    "pmid": record["MedlineCitation"]["PMID"],
                    "title": article.get("ArticleTitle", ""),
                    "journal": article.get("Journal", {}).get("Title", ""),
                    "publication_date": _extract_publication_date(article.get("Journal", {}).get("JournalIssue", {})),
                    "authors": _extract_authors(article.get("AuthorList", [])),
                    "abstract": abstract,
                    "study_type": _classify_study_type(article.get("ArticleTitle", ""), article.get("Abstract", {})),
                    "nct_mentioned": nct_id,
                    "source": f"https://pubmed.ncbi.nlm.nih.gov/{record['MedlineCitation']['PMID']}/"
                })
        
        time.sleep(0.34)
        return {
            "publications": publications,
            "total_found": len(publications),
            "nct_id_searched": nct_id,
            "source": "PubMed Clinical Trial Publication Search via BioPython"
        }
        
    except Exception as e:
        return {"error": str(e), "source": "PubMed Clinical Trial Search", "nct_id": nct_id}

# Helper functions for enhanced data processing

def _extract_abstract(abstract_data):
    """Extract abstract text from complex XML structure."""
    if not abstract_data:
        return ""
    
    if "AbstractText" in abstract_data:
        abstract_text = abstract_data["AbstractText"]
        if isinstance(abstract_text, list):
            # Handle structured abstracts
            return " ".join([str(text) for text in abstract_text if text])
        else:
            return str(abstract_text)
    return ""

def _extract_authors(author_list):
    """Extract and format author information."""
    authors = []
    for author in author_list:
        if "LastName" in author and "ForeName" in author:
            authors.append(f"{author['ForeName']} {author['LastName']}")
        elif "CollectiveName" in author:
            authors.append(author["CollectiveName"])
    return authors

def _extract_mesh_terms(mesh_list):
    """Extract MeSH terms for categorization."""
    mesh_terms = []
    for mesh in mesh_list:
        if "DescriptorName" in mesh:
            mesh_terms.append(mesh["DescriptorName"]["#text"])
    return mesh_terms

def _extract_keywords(keyword_list):
    """Extract author keywords."""
    keywords = []
    for keyword_group in keyword_list:
        if "Keyword" in keyword_group:
            keyword_items = keyword_group["Keyword"]
            if isinstance(keyword_items, list):
                keywords.extend([kw["#text"] if isinstance(kw, dict) else str(kw) for kw in keyword_items])
            else:
                keywords.append(keyword_items["#text"] if isinstance(keyword_items, dict) else str(keyword_items))
    return keywords

def _extract_doi(elocation_list):
    """Extract DOI from electronic location identifiers."""
    for elocation in elocation_list:
        if elocation.get("EIdType") == "doi":
            return elocation.get("#text", "")
    return ""

def _extract_publication_date(journal_issue):
    """Extract publication date from journal issue."""
    if "PubDate" in journal_issue:
        pub_date = journal_issue["PubDate"]
        year = pub_date.get("Year", "")
        month = pub_date.get("Month", "")
        day = pub_date.get("Day", "")
        
        # Handle month names
        month_map = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
            "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", 
            "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
        }
        if month in month_map:
            month = month_map[month]
        
        parts = [p for p in [year, month, day] if p]
        return "-".join(parts) if parts else ""
    return ""

def _classify_study_type(title, abstract_data):
    """Enhanced study type classification."""
    abstract = _extract_abstract(abstract_data)
    text = (title + " " + abstract).lower()
    
    # Phase classification
    if any(term in text for term in ['phase i', 'phase 1', 'dose escalation', 'maximum tolerated dose', 'first-in-human']):
        return "Phase I Clinical Trial"
    elif any(term in text for term in ['phase ii', 'phase 2', 'efficacy', 'dose finding', 'proof of concept']):
        return "Phase II Clinical Trial"  
    elif any(term in text for term in ['phase iii', 'phase 3', 'confirmatory', 'registration', 'pivotal']):
        return "Phase III Clinical Trial"
    elif any(term in text for term in ['phase iv', 'phase 4', 'post-market', 'real-world']):
        return "Phase IV Clinical Trial"
    
    # Study design classification
    elif any(term in text for term in ['randomized controlled', 'rct', 'placebo controlled', 'double-blind']):
        return "Randomized Controlled Trial"
    elif any(term in text for term in ['meta-analysis', 'systematic review', 'pooled analysis']):
        return "Meta-Analysis/Systematic Review"
    elif any(term in text for term in ['observational', 'cohort', 'case-control']):
        return "Observational Study"
    elif any(term in text for term in ['review', 'overview', 'summary']):
        return "Review Article"
    else:
        return "Clinical Study"

def _extract_mechanism_keywords(title, abstract):
    """Extract mechanism of action related keywords."""
    text = (title + " " + abstract).lower()
    moa_keywords = []
    
    moa_terms = [
        "mechanism of action", "pharmacodynamics", "molecular mechanism", "mode of action",
        "target engagement", "receptor binding", "enzyme inhibition", "pathway modulation",
        "agonist", "antagonist", "inhibitor", "activator", "modulator"
    ]
    
    for term in moa_terms:
        if term in text:
            moa_keywords.append(term)
    
    return moa_keywords

def _extract_safety_keywords(title, abstract):
    """Extract safety-related keywords."""
    text = (title + " " + abstract).lower()
    safety_keywords = []
    
    safety_terms = [
        "adverse events", "side effects", "toxicity", "safety profile", "tolerability",
        "dose-limiting toxicity", "serious adverse events", "treatment emergent",
        "contraindication", "drug interaction", "withdrawal", "discontinuation"
    ]
    
    for term in safety_terms:
        if term in text:
            safety_keywords.append(term)
    
    return safety_keywords
