import json
import time
import requests
from bs4 import BeautifulSoup

def get_full_job_profile(job_url):
    
    job_id = job_url.split('?')[0].split('-')[-1]
    
    api_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(api_url, headers=headers)
    
    if response.status_code != 200:
        return {"error": "Failed to fetch profile"}
    
    
    # Make a soup object of that scrape that we did for the job description 
      
    soup = BeautifulSoup(response.text, 'html.parser')
    # We have to find the description div 
    description_div = soup.find('div', class_='description__text')
    full_description = description_div.text.strip() if description_div else "No description found"
    
    criteria_dict = {}
    criteria_list = soup.find('ul', class_='description__job-criteria-list')
    
    if criteria_list:
        items = criteria_list.find_all('li')
        for item in items:
            header = item.find('h3', class_='description__job-criteria-subheader').text.strip()
            value = item.find('span', class_='description__job-criteria-text').text.strip()
            criteria_dict[header] = value

    return {
        "job_id": job_id,
        "description": full_description,
        "criteria": criteria_dict
    }

if __name__ == "__main__":
    
    print("    Opening jobs.json    ")
    
    try:
        with open("jobs.json", "r", encoding="utf-8") as file:
            basic_jobs = json.load(file)
    except FileNotFoundError:
        print("Could not find jobs.json ! Did you run the first script ?")
        exit()

    print(f" Found {len(basic_jobs)} jobs. Starting the deep scrape..." )
    print(" Reminder: This will take about 3 seconds per job to avoid getting blocked.\n ")

    detailed_jobs = []

    for index, job in enumerate(basic_jobs):
        print(f"Fetching profile {index + 1} of {len(basic_jobs)}: {job['position']} at {job['company']}")
        
        job_url = job.get('jobUrl')
        
        if job_url:
            profile_details = get_full_job_profile(job_url)
            job.update(profile_details)
            detailed_jobs.append(job)
            time.sleep(3) 

    output_filename = "master_jobs_detailed.json"
    print(f"\nSaving all data to {output_filename}...")

    with open(output_filename, "w", encoding="utf-8") as file:
        json.dump(detailed_jobs, file, indent=4)
        
    print("All done! Your project data is ready.")