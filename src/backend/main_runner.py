"""
UpskillxAI Main Execution Graph
===============================

This module defines the core orchestration pipeline for the UpskillxAI backend
using LangGraph. It models the data flow as a Directed Acyclic Graph (DAG),
where state is passed between distinct processing nodes (document loaders, AI 
analyzers, job scrapers, and resource finders).

The graph enables parallel execution of independent enrichment tasks (like web 
scraping and resource fetching) after the core analysis phase is complete.
"""

import asyncio
from typing import TypedDict, Annotated, List, Dict, Any, Union
import operator
import importlib.util
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END

from src.backend.loaders.all_around_loader import process_document, perform_final_union
from src.backend.loaders.jina_loader_jd import get_job_description
from src.utilities.brain import analyse_node
from src.utilities.net_surf import add_queries_to_state, get_skill_resources

from pydantic import Field
from src.utilities.resource_finder import get_learning_resources


class GraphState(TypedDict):
    """
    Represents the complete state of a single execution of the UpskillxAI pipeline.
    
    This TypedDict defines the schema of the state dictionary passed between nodes 
    in the LangGraph. It acts as the central data store, holding inputs, intermediate 
    results, and final outputs. Fields annotated with `operator.add` act as reducers
    (e.g., appending to a list rather than overwriting).
    """
    resume_input: Annotated[str, Field(description="Input for the resume, can be a path, URL, or raw text string.")]
    jd_input: Annotated[str, Field(description="Input for the job description, can be a path, URL, or raw text string.")]
    target_role: Annotated[str, Field(description="The user's target role used to guide job scraping keywords.")]
    location: Annotated[str, Field(description="The preferred geographic location for job searching.")]
    
    resume_text: Annotated[str, Field(description="The fully extracted and normalized plain text of the resume.")]
    job_description: Annotated[str, Field(description="The fully extracted and normalized plain text of the job description.")]
    
    candidate_skills: Annotated[List[str], Field(description="List of technical skills extracted from the candidate's resume.")]
    required_skills: Annotated[List[str], Field(description="List of required skills extracted from the job description.")]
    skill_gaps: Annotated[List[str], Field(description="Skills required by the job description but missing from the resume.")]
    ats_score: Annotated[int, Field(description="Calculated ATS matching score between 0 and 100.")]
    learning_path: Annotated[List[Dict[str, Any]], Field(description="Generated learning path recommendations based on skill gaps.")]
    
    search_queries: Annotated[List[str], Field(description="Generated search engine queries to find learning resources for the skill gaps.")]
    skill_resources: Annotated[str, Field(description="Aggregated learning resources found via web search.")]
    static_resources: Annotated[List[Dict[str, str]], Field(description="Static learning resources retrieved from Udemy, YouTube, and Coursera.")]
    
    job_listings: Annotated[List[Dict[str, Any]], Field(description="List of job postings scraped from external boards like Naukri.")]
    
    career_summary: Annotated[str, Field(description="A final summarization of the candidate's profile, gaps, and job prospects.")]
    
    error: Annotated[str, Field(description="Error message if any step in the pipeline fails.")]
    status_messages: Annotated[List[str], operator.add, Field(description="Append-only list of status messages for streaming UI updates.")]



# Dynamically import the scraper because the file name contains a dot
spec = importlib.util.spec_from_file_location("naukri_scraper", "src/backend/scraper/naukri.com_scraper.py")
naukri_scraper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(naukri_scraper)

async def load_resume_node(state: GraphState) -> GraphState:
    """
    Asynchronously loads and parses the candidate's resume document.

    Args:
        state (GraphState): The current graph state containing `resume_input`.

    Returns:
        GraphState: An updated state dictionary containing the extracted `resume_text`.
                    If no input is provided, returns an empty string.
    """
    resume_input = state.get("resume_input", "")
    if not resume_input:
        return {"resume_text": ""}
    docs_dict = await process_document(resume_input)
    resume_text = perform_final_union(docs_dict)
    return {"resume_text": resume_text}

async def load_jd_node(state: GraphState) -> GraphState:
    """
    Asynchronously loads and parses the target job description (JD).
    
    Supports both direct URLs (by scraping the JD webpage) and raw document/text input.

    Args:
        state (GraphState): The current graph state containing `jd_input`.

    Returns:
        GraphState: An updated state dictionary containing the extracted `job_description`.
    """
    jd_input = state.get("jd_input", "")
    if not jd_input:
        return {"job_description": ""}
        
    if str(jd_input).startswith("http"):
        jd_text = await get_job_description(jd_input)
        if not jd_text:
             docs_dict = await process_document(jd_input)
             jd_text = perform_final_union(docs_dict)
    else:
        docs_dict = await process_document(jd_input)
        jd_text = perform_final_union(docs_dict)
        
    return {"job_description": jd_text}

async def analyse_node_wrapper(state: GraphState) -> GraphState:
    """
    Analyzes the extracted resume and job description using the AI Brain module.

    This node performs the core cognitive tasks: extracting candidate skills, 
    extracting required skills from the JD, computing the skill gaps, calculating 
    the ATS match score, and generating a structured learning path.

    Args:
        state (GraphState): The current graph state containing `resume_text` and `job_description`.

    Returns:
        GraphState: An updated state dict with `candidate_skills`, `required_skills`, 
                    `skill_gaps`, `ats_score`, and `learning_path`.
    """
    brain_state = {
        "resume_text": state.get("resume_text", ""),
        "job_description": state.get("job_description", "")
    }
    result = analyse_node(brain_state)
    return {
        "candidate_skills": result.get("candidate_skills", []),
        "required_skills": result.get("required_skills", []),
        "skill_gaps": result.get("skill_gaps", []),
        "ats_score": result.get("ats_score", 0),
        "learning_path": result.get("learning_path", [])
    }

async def scrape_jobs_node(state: GraphState) -> GraphState:
    """
    Scrapes external job boards (e.g., Naukri) for current job openings matching the target role.

    This node runs a synchronous Selenium-based scraper within an asyncio executor thread
    to prevent blocking the main event loop during browser automation.

    Args:
        state (GraphState): The current graph state containing `target_role` and `location`.

    Returns:
        GraphState: An updated state dict containing a list of `job_listings`.
    """
    loop = asyncio.get_event_loop()
    keyword = state.get("target_role") or "software engineer"
    location = state.get("location") or ""
    
    # Run the synchronous selenium scraper in a thread
    job_listings = await loop.run_in_executor(
        None, 
        lambda: naukri_scraper.scrape_naukri_jobs(
            keyword=keyword,
            location=location,
            pages=1,
            save_csv=False,
            save_json=False
        )
    )
    return {"job_listings": job_listings}

async def net_surf_node(state: GraphState) -> GraphState:
    """
    Generates dynamic search queries based on skill gaps and fetches relevant web resources.

    This node leverages Tavily to search the web and Gemini to parse the raw search 
    results into highly relevant, structured learning resources for the candidate.

    Args:
        state (GraphState): The current graph state containing `skill_gaps` and `learning_path`.

    Returns:
        GraphState: An updated state dict containing `search_queries` and formatted `skill_resources`.
    """
    dummy_state = {
        "skill_gaps": state.get("skill_gaps", []),
        "learning_path": state.get("learning_path", [])
    }
    dummy_state = await add_queries_to_state(dummy_state)
    dummy_state = await get_skill_resources(dummy_state)
    return {
        "search_queries": dummy_state.get("search_queries", []),
        "skill_resources": dummy_state.get("skill_resources", "")
    }

async def resource_finder_node(state: GraphState) -> GraphState:
    """
    Retrieves static learning resources (Udemy, YouTube, Coursera) for identified skill gaps.

    This node uses a pre-defined or structured mapping to instantly suggest high-quality
    courses and tutorials without needing a live web search.

    Args:
        state (GraphState): The current graph state containing `skill_gaps`.

    Returns:
        GraphState: An updated state dict containing a list of `static_resources`.
    """
    static_resources = []
    for skill in state.get("skill_gaps", []):
        static_resources.extend(get_learning_resources(skill))
    return {"static_resources": static_resources}

async def summarise_node(state: GraphState) -> GraphState:
    """
    Synthesizes a final career prospect summary for the candidate.

    Takes the entire analytical output (skills, gaps, scores) and uses Gemini to 
    draft a short, personalized, and encouraging summary of the candidate's profile.

    Args:
        state (GraphState): The current graph state containing skills, gaps, role, and ATS score.

    Returns:
        GraphState: An updated state dict containing the `career_summary`.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"career_summary": "Summary unavailable due to missing API key."}
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)
    prompt = f"""
    Summarize the career prospects based on the following:
    Candidate Skills: {state.get('candidate_skills')}
    Skill Gaps: {state.get('skill_gaps')}
    Target Role: {state.get('target_role')}
    ATS Score: {state.get('ats_score')}
    
    Write a short, encouraging 3-sentence summary for the candidate.
    """
    try:
        res = await llm.ainvoke(prompt)
        return {"career_summary": res.content}
    except Exception as e:
        return {"career_summary": f"Could not generate summary: {str(e)}"}

def build_main_graph():
    """
    Constructs and compiles the LangGraph Directed Acyclic Graph (DAG) for the backend.

    Topology:
    1. START -> Parallel execution of `load_resume` and `load_jd`.
    2. Both loaders converge -> `analyse` node.
    3. `analyse` node fans out to parallel execution of:
       - `scrape_jobs`
       - `net_surf`
       - `resource_finder`
    4. All enrichment nodes converge -> `summarise` node.
    5. `summarise` -> END.

    Returns:
        CompiledGraph: The compiled runnable graph instance ready for execution.
    """
    graph = StateGraph(GraphState)
    
    graph.add_node("load_resume", load_resume_node)
    graph.add_node("load_jd", load_jd_node)
    graph.add_node("analyse", analyse_node_wrapper)
    graph.add_node("scrape_jobs", scrape_jobs_node)
    graph.add_node("net_surf", net_surf_node)
    graph.add_node("resource_finder", resource_finder_node)
    graph.add_node("summarise", summarise_node)
    
    graph.add_edge(START, "load_resume")
    graph.add_edge(START, "load_jd")
    
    graph.add_edge("load_resume", "analyse")
    graph.add_edge("load_jd", "analyse")
    
    graph.add_edge("analyse", "scrape_jobs")
    graph.add_edge("analyse", "net_surf")
    graph.add_edge("analyse", "resource_finder")
    
    graph.add_edge("scrape_jobs", "summarise")
    graph.add_edge("net_surf", "summarise")
    graph.add_edge("resource_finder", "summarise")
    
    graph.add_edge("summarise", END)
    
    return graph.compile()
