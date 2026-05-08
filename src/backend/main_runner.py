import asyncio
from typing import TypedDict, Annotated, List, Dict, Any, Union
import operator

from langgraph.graph import StateGraph, START, END

from src.backend.loaders.all_around_loader import process_document, perform_final_union
from src.backend.loaders.jina_loader_jd import get_job_description
from src.utilities.brain import analyse_node
from src.utilities.net_surf import add_queries_to_state, get_skill_resources

class GraphState(TypedDict):
    resume_input: str
    jd_input: str
    target_role: str
    location: str
    
    resume_text: str
    job_description: str
    
    candidate_skills: List[str]
    required_skills: List[str]
    skill_gaps: List[str]
    ats_score: int
    learning_path: List[Dict[str, Any]]
    
    search_queries: List[str]
    skill_resources: str
    
    job_listings: List[Dict[str, Any]]
    
    career_summary: str
    
    error: str
    status_messages: Annotated[List[str], operator.add]

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

async def summarise_node(state: GraphState) -> GraphState:
    pass

def build_main_graph():
    graph = StateGraph(GraphState)
    
    graph.add_node("load_resume", load_resume_node)
    graph.add_node("load_jd", load_jd_node)
    graph.add_node("analyse", analyse_node_wrapper)
    graph.add_node("scrape_jobs", scrape_jobs_node)
    graph.add_node("net_surf", net_surf_node)
    graph.add_node("summarise", summarise_node)
    
    graph.add_edge(START, "load_resume")
    graph.add_edge("load_resume", "load_jd")
    graph.add_edge("load_jd", "analyse")
    graph.add_edge("analyse", "scrape_jobs")
    graph.add_edge("scrape_jobs", "net_surf")
    graph.add_edge("net_surf", "summarise")
    graph.add_edge("summarise", END)
    
    return graph.compile()
