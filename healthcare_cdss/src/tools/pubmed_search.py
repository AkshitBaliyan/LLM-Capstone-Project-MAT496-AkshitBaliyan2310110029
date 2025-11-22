"""
PubMed Medical Literature Search

This module provides tools for searching PubMed and other medical literature
databases to support evidence-based clinical decision making.
"""

from typing import Annotated, List, Optional
from datetime import datetime
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from pydantic import BaseModel, Field

from ..state.healthcare_state import ClinicalState


# Initialize LLM for summarization
summarization_model = init_chat_model(
    "openai:gpt-4o-mini",  # Cheaper model for summarization
    temperature=0.0
)


class PubMedArticle(BaseModel):
    """Structure for PubMed article"""
    pmid: str = Field(description="PubMed ID")
    title: str = Field(description="Article title")
    abstract: str = Field(description="Article abstract")
    journal: str = Field(description="Journal name")
    year: str = Field(description="Publication year")
    authors: List[str] = Field(default_factory=list, description="Author list")
    
class ArticleSummary(BaseModel):
    """Structured summary of medical article"""
    key_findings: str = Field(description="Main clinical findings")
    relevance: str = Field(description="Relevance to current case")
    evidence_level: str = Field(description="Quality of evidence (A/B/C/D)")
    clinical_implications: str = Field(description="Implications for practice")


def search_pubmed(query: str, max_results: int = 5) -> List[PubMedArticle]:
    """
    Search PubMed for medical literature
    
    Note: This is a simplified implementation for Phase 2.
    In production, this would use the actual PubMed E-utilities API
    via Biopython's Entrez module.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
    
    Returns:
        List of PubMed articles
    """
    # For Phase 2, we'll simulate PubMed results
    # In Phase 5, this will be replaced with actual API calls
    
    print(f"📚 Searching PubMed for: '{query}'")
    print("   (Using simulated results for Phase 2)")
    
    # Simulated results - In real implementation, use:
    # from Bio import Entrez
    # Entrez.email = "your_email@example.com"
    # handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    # record = Entrez.read(handle)
    # pmids = record["IdList"]
    # ... fetch details
    
    simulated_articles = [
        PubMedArticle(
            pmid="12345678",
            title=f"Clinical Review: {query}",
            abstract=f"This systematic review examines {query}. Multiple studies demonstrate the effectiveness of evidence-based approaches. Key findings include improved patient outcomes and reduced complications when following clinical guidelines.",
            journal="Journal of Clinical Medicine",
            year="2024",
            authors=["Smith J", "Johnson A", "Williams B"]
        ),
        PubMedArticle(
            pmid="87654321",
            title=f"Management Guidelines for {query}",
            abstract=f"Evidence-based guidelines for managing {query}. Recommendations are based on high-quality randomized controlled trials and meta-analyses. Grade A evidence supports first-line treatment approaches.",
            journal="American Journal of Medicine",
            year="2023",
            authors=["Davis M", "Brown R"]
        )
    ]
    
    return simulated_articles[:max_results]


def summarize_medical_article(article: PubMedArticle, clinical_context: str) -> ArticleSummary:
    """
    Summarize medical article for clinical relevance
    
    Args:
        article: PubMed article to summarize
        clinical_context: Current clinical context/question
    
    Returns:
        Structured summary of article
    """
    prompt = f"""Summarize this medical article for clinical decision making.

CLINICAL CONTEXT: {clinical_context}

ARTICLE:
Title: {article.title}
Journal: {article.journal} ({article.year})
Authors: {', '.join(article.authors[:3])}

Abstract: {article.abstract}

Provide:
1. Key clinical findings relevant to the context
2. Specific relevance to the current case
3. Evidence level (A=high quality RCT, B=lower quality RCT, C=observational, D=expert opinion)
4. What this means for clinical practice

Be concise and clinically focused."""

    structured_model = summarization_model.with_structured_output(ArticleSummary)
    
    try:
        summary = structured_model.invoke(prompt)
        return summary
    except Exception as e:
        # Fallback if structured output fails
        print(f"Warning: Summarization failed: {e}")
        return ArticleSummary(
            key_findings=article.abstract[:200],
            relevance="See abstract for details",
            evidence_level="C",
            clinical_implications="Review full article for clinical guidance"
        )


@tool(parse_docstring=True)
def search_medical_literature(
    clinical_question: str,
    state: Annotated[ClinicalState, InjectedState],
    tool_call_id: str = "literature_search",
    max_results: Annotated[int, "Maximum number of articles to retrieve"] = 3
) -> Command:
    """Search medical literature (PubMed) for evidence-based information.
    
    This tool searches PubMed and clinical guidelines to find relevant
    medical evidence for the current clinical question. It:
    - Searches PubMed database
    - Retrieves relevant articles
    - Summarizes findings for clinical relevance
    - Stores full articles in file system
    - Returns concise summaries to agent
    
    This follows the context offloading pattern from the research agent,
    storing detailed information in files while returning summaries.
    
    Args:
        clinical_question: Question or topic to research
        state: Injected clinical state
        tool_call_id: Injected tool call ID
        max_results: Number of articles to retrieve (default: 3)
    
    Returns:
        Command updating state with literature findings
    """
    print(f"\n{'='*60}")
    print(f"📚 MEDICAL LITERATURE SEARCH")
    print(f"{'='*60}")
    print(f"Query: {clinical_question}\n")
    
    # Search PubMed
    articles = search_pubmed(clinical_question, max_results=max_results)
    
    if not articles:
        return Command(update={
            "messages": state.get("messages", []) + [
                ToolMessage(
                    content=f"No articles found for: {clinical_question}",
                    tool_call_id=tool_call_id
                )
            ]
        })
    
    # Process and summarize articles
    files = state.get("files", {})
    evidence_sources = state.get("evidence_sources", [])
    summaries_text = []
    
    for i, article in enumerate(articles, 1):
        # Summarize article
        summary = summarize_medical_article(article, clinical_question)
        
        # Create filename
        filename = f"pubmed_{article.pmid}.md"
        
        # Store full article in file system
        file_content = f"""# {article.title}

**PMID:** {article.pmid}  
**Journal:** {article.journal}  
**Year:** {article.year}  
**Authors:** {', '.join(article.authors)}

## Abstract

{article.abstract}

## Clinical Summary

**Key Findings:**  
{summary.key_findings}

**Relevance to Case:**  
{summary.relevance}

**Evidence Level:** {summary.evidence_level}

**Clinical Implications:**  
{summary.clinical_implications}

---
*Retrieved: {datetime.now().strftime("%Y-%m-%d %H:%M")}*
"""
        
        files[filename] = file_content
        
        # Add to evidence sources
        citation = f"{article.authors[0] if article.authors else 'Unknown'} et al. {article.journal}. {article.year}. PMID: {article.pmid}"
        evidence_sources.append(citation)
        
        # Create summary for agent
        summaries_text.append(
            f"{i}. [{filename}] {article.title[:80]}...\n"
            f"   Evidence Level: {summary.evidence_level}\n"
            f"   Key Finding: {summary.key_findings[:100]}..."
        )
        
        print(f"✓ Article {i}: {article.title[:60]}...")
        print(f"  PMID: {article.pmid} | Evidence: {summary.evidence_level}")
    
    print(f"\n{'='*60}\n")
    
    # Create summary message
    summary_message = f"""📚 Literature Search Complete

Found {len(articles)} relevant articles for: "{clinical_question}"

{chr(10).join(summaries_text)}

Files stored: {', '.join([f'pubmed_{a.pmid}.md' for a in articles])}

💡 Use read_file() to access full article details and abstracts.
Evidence levels: A (high quality RCT) > B (lower quality RCT) > C (observational) > D (expert opinion)
"""
    
    # Update state
    return Command(update={
        "files": files,
        "evidence_sources": evidence_sources,
        "messages": state.get("messages", []) + [
            ToolMessage(content=summary_message, tool_call_id=tool_call_id)
        ]
    })


def format_citation(article: PubMedArticle) -> str:
    """
    Format article as citation
    
    Args:
        article: PubMed article
    
    Returns:
        Formatted citation string
    """
    first_author = article.authors[0] if article.authors else "Unknown"
    
    return f"{first_author} et al. {article.title}. {article.journal}. {article.year}. PMID: {article.pmid}"


def get_article_url(pmid: str) -> str:
    """
    Get PubMed URL for article
    
    Args:
        pmid: PubMed ID
    
    Returns:
        URL to article on PubMed
    """
    return f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
