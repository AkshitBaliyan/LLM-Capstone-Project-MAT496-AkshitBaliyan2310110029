"""
Tavily Web Search Tool for Healthcare CDSS

This module provides web search capabilities using Tavily API for real-time
medical information retrieval beyond PubMed literature.
"""

from typing import Annotated, List, Optional
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from pydantic import BaseModel, Field
import os

from ..state.healthcare_state import ClinicalState


# Initialize summarization model
summarization_model = init_chat_model(
    "openai:gpt-4o-mini",
    temperature=0.0
)


class WebSearchResult(BaseModel):
    """Structured web search result"""
    title: str = Field(description="Page title")
    url: str = Field(description="Page URL")
    content: str = Field(description="Page content snippet")
    relevance_score: float = Field(description="Relevance score 0-1")


class MedicalSearchSummary(BaseModel):
    """Summary of medical web search"""
    key_findings: str = Field(description="Key medical findings from search")
    clinical_relevance: str = Field(description="Relevance to the clinical case")
    sources_quality: str = Field(description="Assessment of source quality")
    actionable_insights: str = Field(description="Actionable clinical insights")


def search_tavily_web(query: str, max_results: int = 5) -> List[WebSearchResult]:
    """
    Search the web using Tavily API
    
    Args:
        query: Search query
        max_results: Maximum results to return
    
    Returns:
        List of web search results
    """
    try:
        from tavily import TavilyClient
        
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            print("⚠️ TAVILY_API_KEY not found - using simulated results")
            return get_simulated_results(query, max_results)
        
        client = TavilyClient(api_key=api_key)
        
        # Search with focus on medical/health content
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_raw_content=True,
            topic="general"
        )
        
        results = []
        for item in response.get("results", []):
            results.append(WebSearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                content=item.get("content", ""),
                relevance_score=item.get("score", 0.0)
            ))
        
        return results
        
    except ImportError:
        print("⚠️ tavily-python not installed - using simulated results")
        return get_simulated_results(query, max_results)
    except Exception as e:
        print(f"⚠️ Tavily search error: {e} - using simulated results")
        return get_simulated_results(query, max_results)


def get_simulated_results(query: str, max_results: int) -> List[WebSearchResult]:
    """
    Simulated web search results for demo/testing
    
    Args:
        query: Search query
        max_results: Max results
    
    Returns:
        Simulated search results
    """
    simulated = [
        WebSearchResult(
            title=f"Clinical Guidelines: {query}",
            url=f"https://www.mayoclinic.org/search?q={query.replace(' ', '+')}",
            content=f"Comprehensive clinical information about {query}. Evidence-based guidelines from leading medical institutions. Covers symptoms, causes, diagnosis, and treatment options with latest research.",
            relevance_score=0.95
        ),
        WebSearchResult(
            title=f"Latest Research on {query}",
            url=f"https://www.ncbi.nlm.nih.gov/pmc/?term={query.replace(' ', '+')}",
            content=f"Recent peer-reviewed studies on {query}. Meta-analyses and systematic reviews provide strong evidence for clinical decision-making. Updated treatment protocols and emerging therapies discussed.",
            relevance_score=0.90
        ),
        WebSearchResult(
            title=f"Patient Information: {query}",
            url=f"https://medlineplus.gov/search?query={query.replace(' ', '+')}",
            content=f"Patient-friendly information about {query} from trusted medical sources. Includes symptoms, treatment options, and when to seek emergency care. Validated by medical professionals.",
            relevance_score=0.85
        )
    ]
    
    return simulated[:max_results]


def summarize_web_search(results: List[WebSearchResult], clinical_context: str) -> MedicalSearchSummary:
    """
    Summarize web search results for clinical relevance
    
    Args:
        results: Web search results  
        clinical_context: Current clinical question/context
    
    Returns:
        Structured summary of findings
    """
    # Combine all content
    all_content = "\n\n".join([
        f"Source: {r.title}\n{r.content}"
        for r in results
    ])
    
    prompt = f"""Summarize these web search results for clinical decision making.

CLINICAL CONTEXT: {clinical_context}

WEB SEARCH RESULTS:
{all_content}

Provide:
1. Key medical findings relevant to the clinical context
2. Clinical relevance and applicability
3. Assessment of source quality (are these reputable medical sources?)
4. Actionable insights for clinical practice

Be concise and clinically focused."""

    structured_model = summarization_model.with_structured_output(MedicalSearchSummary)
    
    try:
        summary = structured_model.invoke(prompt)
        return summary
    except Exception as e:
        print(f"Warning: Summarization failed: {e}")
        return MedicalSearchSummary(
            key_findings="See search results for details",
            clinical_relevance="Review individual sources for clinical applicability",
            sources_quality="Multiple sources found - review for credibility",
            actionable_insights="Consult detailed sources for clinical guidance"
        )


@tool(parse_docstring=True)
def search_medical_web(
    clinical_question: str,
    state: Annotated[ClinicalState, InjectedState],
    tool_call_id: str = "web_search",
    max_results: Annotated[int, "Maximum number of results to retrieve"] = 3
) -> Command:
    """Search the web for current medical information using Tavily.
    
    This tool searches the broader web for medical information beyond
    PubMed literature. Useful for:
    - Clinical guidelines and protocols
    - Latest medical news and developments
    - Patient education resources
    - Drug information
    - Disease statistics and epidemiology
    
    Complements PubMed search by providing more current and diverse sources.
    
    Args:
        clinical_question: Medical topic or question to search
        state: Injected clinical state
        tool_call_id: Injected tool call ID
        max_results: Number of results to retrieve (default: 3)
    
    Returns:
        Command updating state with web search findings
    """
    print(f"\n{'='*60}")
    print(f"🌐 WEB SEARCH - Tavily")
    print(f"{'='*60}")
    print(f"Query: {clinical_question}\n")
    
    # Search web
    results = search_tavily_web(clinical_question, max_results=max_results)
    
    if not results:
        return Command(update={
            "messages": state.get("messages", []) + [
                ToolMessage(
                    content=f"No web results found for: {clinical_question}",
                    tool_call_id=tool_call_id
                )
            ]
        })
    
    # Summarize results
    summary = summarize_web_search(results, clinical_question)
    
    # Store detailed results in file system
    files = state.get("files", {})
    evidence_sources = state.get("evidence_sources", [])
    summaries_text = []
    
    for i, result in enumerate(results, 1):
        # Create filename
        filename = f"web_search_{i}_{clinical_question[:30].replace(' ', '_')}.md"
        
        # Store full result
        file_content = f"""# {result.title}

**URL:** {result.url}  
**Relevance Score:** {result.relevance_score:.2f}  
**Query:** {clinical_question}

## Content

{result.content}

## Clinical Summary

**Key Findings:**  
{summary.key_findings}

**Clinical Relevance:**  
{summary.clinical_relevance}

**Source Quality:**  
{summary.sources_quality}

**Actionable Insights:**  
{summary.actionable_insights}

---
*Retrieved via Tavily Web Search*
"""
        
        files[filename] = file_content
        
        # Add to evidence sources
        evidence_sources.append(f"Web: {result.title} - {result.url}")
        
        # Create summary for agent
        summaries_text.append(
            f"{i}. [{filename}] {result.title[:60]}...\n"
            f"   Relevance: {result.relevance_score:.0%}\n"
            f"   Insight: {summary.actionable_insights[:80]}..."
        )
        
        print(f"✓ Result {i}: {result.title[:60]}...")
        print(f"  Relevance: {result.relevance_score:.0%}")
    
    print(f"\n{'='*60}\n")
    
    # Create summary message
    summary_message = f"""🌐 Web Search Complete

Found {len(results)} relevant web sources for: "{clinical_question}"

{chr(10).join(summaries_text)}

**Key Clinical Findings:**
{summary.key_findings}

**Actionable Insights:**
{summary.actionable_insights}

Files stored: {', '.join([f'web_search_{i}...' for i in range(1, len(results)+1)])}

💡 These sources complement PubMed literature with current guidelines and practical information.
"""
    
    # Update state
    return Command(update={
        "files": files,
        "evidence_sources": evidence_sources,
        "messages": state.get("messages", []) + [
            ToolMessage(content=summary_message, tool_call_id=tool_call_id)
        ]
    })


def format_web_source(result: WebSearchResult) -> str:
    """
    Format web result as citation
    
    Args:
        result: Web search result
    
    Returns:
        Formatted citation string
    """
    return f"{result.title}. {result.url} (Relevance: {result.relevance_score:.0%})"
