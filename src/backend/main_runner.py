import asyncio
from typing import TypedDict, Annotated, List, Dict, Any, Union
import operator

from langgraph.graph import StateGraph, START, END

from src.backend.loaders.all_around_loader import process_document, perform_final_union
from src.backend.loaders.jina_loader_jd import get_job_description
from src.utilities.brain import analyse_node
from src.utilities.net_surf import add_queries_to_state, get_skill_resources

from pydantic import Field
from src.utilities.resource_finder import get_learning_resources

# FORCING UPDATE
class GraphState(TypedDict):
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

async def load_resume_node(state: GraphState) -> GraphState:
    pass 

async def load_jd_node(state: GraphState) -> GraphState:
    pass

async def analyse_node_wrapper(state: GraphState) -> GraphState:
    pass

async def scrape_jobs_node(state: GraphState) -> GraphState:
    pass

async def net_surf_node(state: GraphState) -> GraphState:
    pass

async def resource_finder_node(state: GraphState) -> GraphState:
    pass

async def summarise_node(state: GraphState) -> GraphState:
    pass

def build_main_graph():
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
