import requests
from bs4 import BeautifulSoup
import time
import json

def scrape_linkedin_pro(keywords, location, num_pages=1, **filters):
    all_jobs = []
    base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    for page in range(num_pages):
        params = {
            "keywords": keywords,
            "location": location,
            "start": page * 10
        }
        params.update(filters)

        response = requests.get(base_url, params=params, headers=headers)
        
        if response.status_code != 200:
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find_all('li')
        
        if not job_cards:
            break
            
        for job in job_cards:
            try:
                title = job.find('h3', class_='base-search-card__title').text.strip()
                company = job.find('h4', class_='base-search-card__subtitle').text.strip()
                job_location = job.find('span', class_='job-search-card__location').text.strip()
                link = job.find('a', class_='base-card__full-link')['href'].split('?')[0] 
                
                #logo_tag = job.find('img', class_='artdeco-entity-image')
                #company_logo = (logo_tag.get('data-delayed-url') or logo_tag.get('src', "")) if logo_tag else ""
                
                time_tag = job.find('time')
                date_posted = time_tag.get('datetime', "") if time_tag else ""
                ago_time = time_tag.text.strip() if time_tag else ""
                
                salary_tag = job.find('span', class_='job-search-card__salary-info')
                salary = salary_tag.text.strip() if salary_tag else "Not Listed"

                all_jobs.append({
                    "position": title,
                    "company": company,
                    #"companyLogo": company_logo,
                    "location": job_location,
                    "date": date_posted,
                    "agoTime": ago_time,
                    "salary": salary,
                    "jobUrl": link
                })
                
            except AttributeError:
                continue 
        
        if page < num_pages - 1:
            time.sleep(3)
            
    return all_jobs

if __name__ == "__main__":
    my_jobs = scrape_linkedin_pro(
        # keywords="Software Engineer ", 
        # location="Amritsar,India",
        # f_E="1,2",
        # f_JT="F,P",
        # f_TPR="r86400",
        # sortBy="DD"
        keywords="Software Engineer",
        location="India",
        num_pages=2,
        f_TPR="r2592000"  # Past Month
    )
    
    with open("jobs.json", "w", encoding="utf-8") as f:
        print(" Dumping the json ")
        json.dump(my_jobs, f, indent=8)
        print(" Done Dumping ")