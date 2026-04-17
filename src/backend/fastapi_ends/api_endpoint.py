from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from linkdin import scrape_linkedin_pro
from jobs_profile import get_full_job_profile

app = FastAPI(
    title="LinkedIn Job Scraper API",
    description="Scrape LinkedIn job listings and enrich them with full job descriptions.",
    version="1.0.0"
)
executor = ThreadPoolExecutor()


class ScrapeRequest(BaseModel):
    keywords: str = Field(..., example="Software Engineer")
    location: str = Field(..., example="India")
    num_pages: int = Field(1, example=2)
    filters: dict = Field({}, example={"f_TPR": "r2592000"})


class ProfileRequest(BaseModel):
    jobs: list[dict] = Field(..., example=[{"jobUrl": "https://www.linkedin.com/jobs/view/1234567890"}])


class FullRequest(BaseModel):
    keywords: str = Field(..., example="Data Scientist")
    location: str = Field(..., example="Bangalore, India")
    num_pages: int = Field(1, example=1)
    filters: dict = Field({}, example={})
    n: Optional[int] = Field(None, example=5)


def run_scrape(req: ScrapeRequest):
    return scrape_linkedin_pro(
        keywords=req.keywords,
        location=req.location,
        num_pages=req.num_pages,
        **req.filters
    )


def enrich_jobs(jobs: list[dict]):
    detailed = []
    for job in jobs:
        url = job.get("jobUrl")
        if url:
            profile = get_full_job_profile(url)
            job.update(profile)
        detailed.append(job)
    return detailed


@app.post(
    "/jobs",
    summary="Scrape LinkedIn Jobs",
    description="Scrape LinkedIn for job listings based on keywords, location, and optional filters. Returns the full list of jobs found.",
    tags=["Scraping"]
)
async def get_jobs(req: ScrapeRequest):
    loop = asyncio.get_event_loop()
    jobs = await loop.run_in_executor(executor, lambda: run_scrape(req))
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found")
    return jobs


@app.post(
    "/jobs/slice",
    summary="Scrape LinkedIn Jobs (First N)",
    description="Same as /jobs but returns only the first `n` results. Pass `n` as a query parameter e.g. `/jobs/slice?n=3`.",
    tags=["Scraping"]
)
async def get_jobs_slice(req: ScrapeRequest, n: int = Query(..., ge=1, description="Number of jobs to return")):
    loop = asyncio.get_event_loop()
    jobs = await loop.run_in_executor(executor, lambda: run_scrape(req))
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found")
    return jobs[:n]


@app.post(
    "/profiles",
    summary="Enrich Jobs with Full Descriptions",
    description="Pass in a list of jobs (each must have a `jobUrl`) and get back enriched profiles. Use `n` to limit how many get processed.",
    tags=["Enrichment"]
)
async def get_profiles(req: ProfileRequest, n: Optional[int] = Query(None, ge=1, description="Only enrich the first n jobs")):
    if not req.jobs:
        raise HTTPException(status_code=400, detail="Jobs list is empty")
    jobs = req.jobs[:n] if n is not None else req.jobs
    loop = asyncio.get_event_loop()
    detailed = await loop.run_in_executor(executor, lambda: enrich_jobs(jobs))
    return detailed

@app.post(
    "/jobs-with-profiles",
    summary="Scrape + Enrich in One Shot",
    description="Scrapes LinkedIn jobs and immediately enriches each one with the full job description. Use `n` in the body to limit how many jobs get enriched — useful to avoid long wait times.",
    tags=["Combined"]
)

async def get_jobs_with_profiles(req: FullRequest):
    loop = asyncio.get_event_loop()
    scrape_req = ScrapeRequest(
        keywords=req.keywords,
        location=req.location,
        num_pages=req.num_pages,
        filters=req.filters
    )
    jobs = await loop.run_in_executor(executor, lambda: run_scrape(scrape_req))
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found")
    if req.n is not None:
        jobs = jobs[:req.n]
    detailed = await loop.run_in_executor(executor, lambda: enrich_jobs(jobs))
    return detailed