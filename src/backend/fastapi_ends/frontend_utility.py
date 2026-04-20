import requests

BASE_URL = "http://127.0.0.1:8000"


def scrape_jobs(keywords: str, location: str, num_pages: int = 1, filters: dict = None) -> list[dict]:
    response = requests.post(f"{BASE_URL}/jobs", json={
        "keywords": keywords,
        "location": location,
        "num_pages": num_pages,
        "filters": filters or {},
    })
    response.raise_for_status()
    return response.json()


def scrape_jobs_slice(keywords: str, location: str, n: int, num_pages: int = 1, filters: dict = None) -> list[dict]:
    response = requests.post(f"{BASE_URL}/jobs/slice", json={
        "keywords": keywords,
        "location": location,
        "num_pages": num_pages,
        "filters": filters or {},
    }, params={"n": n})
    response.raise_for_status()
    return response.json()


def enrich_profiles(jobs: list[dict], n: int = None) -> list[dict]:
    response = requests.post(f"{BASE_URL}/profiles", json={
        "jobs": jobs,
    }, params={"n": n} if n else {})
    response.raise_for_status()
    return response.json()


def scrape_and_enrich(keywords: str, location: str, num_pages: int = 1, filters: dict = None, n: int = None) -> list[dict]:
    response = requests.post(f"{BASE_URL}/jobs-with-profiles", json={
        "keywords": keywords,
        "location": location,
        "num_pages": num_pages,
        "filters": filters or {},
        "n": n,
    })
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    jobs = scrape_jobs("Software Engineer", "India", num_pages=1, filters={"f_TPR": "r2592000"})
    print(f"Found {len(jobs)} jobs")

    sliced = scrape_jobs_slice("Software Engineer", "India", n=3)
    print(f"Sliced to {len(sliced)} jobs")

    enriched = enrich_profiles(sliced, n=2)
    print(f"Enriched {len(enriched)} jobs")

    full = scrape_and_enrich("Data Scientist", "Remote", n=2)
    print(f"Full pipeline returned {len(full)} jobs")
