'''
Since you can use the official APIs to request data from the API,
you can use the API to get data instead of scraping it from the website.
This is more efficient and less likely to break if the website changes.
One downside though you need a partnership with LinkedIn to access the API,
and there may be limitations on the amount of data you can access.
We will use Job Board API to get job postings data instead of linkedin API.import requests'''
import os
from dotenv import load_dotenv
import pandas as pd
from typing import List, Dict
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class JobBoardAPIClient:
    def __init__(self):
        # Example with Adzuna API (free tier available)
        self.adzuna_app_id = os.getenv('ADZUNA_APP_ID')
        self.adzuna_app_key = os.getenv('ADZUNA_APP_KEY')
        self.base_url = 'http://api.adzuna.com/v1/api/jobs'
        
        # Example with JSearch API (RapidAPI)
        self.jsearch_api_key = os.getenv('JSEARCH_API_KEY')
        self.jsearch_base_url = 'https://jsearch.p.rapidapi.com'
        
    def search_adzuna_jobs(self, what: str, where: str = "us", results: int = 10) -> pd.DataFrame:
        """Search jobs using Adzuna API"""
        try:
            url = f"{self.base_url}/{where}/search/{results}"
            params = {
                'app_id': self.adzuna_app_id,
                'app_key': self.adzuna_app_key,
                'what': what,
                'content-type': 'application/json'
            }
            
            response =response.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            jobs = []
            
            for job in data.get('results', []):
                jobs.append({
                    'title': job.get('title', 'N/A'),
                    'company': job.get('company', {}).get('display_name', 'N/A'),
                    'location': f"{job.get('location', {}).get('area', ['N/A'])[0]}",
                    'salary_min': job.get('salary_min', 'N/A'),
                    'salary_max': job.get('salary_max', 'N/A'),
                    'description': job.get('description', 'N/A')[:200] + '...',
                    'url': job.get('redirect_url', 'N/A'),
                    'posted': job.get('created', 'N/A')
                })
            
            return pd.DataFrame(jobs)
            
        except Exception as e:
            logger.error(f"Adzuna API request failed: {e}")
            return pd.DataFrame()
    
    def search_jsearch_jobs(self, query: str, page: int = 1) -> pd.DataFrame:
        """Search jobs using JSearch API (RapidAPI)"""
        try:
            url = f"{self.jsearch_base_url}/search"
            headers = {
                'X-RapidAPI-Key': self.jsearch_api_key,
                'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
            }
            params = {
                'query': query,
                'page': str(page)
            }
            
            response = response.get(url, headers=headers, params=params)# request, not response
            response.raise_for_status()
            
            data = response.json()
            jobs = []
            
            for job in data.get('data', []):
                jobs.append({
                    'title': job.get('job_title', 'N/A'),
                    'company': job.get('employer_name', 'N/A'),
                    'location': job.get('job_city', 'N/A') + ', ' + job.get('job_state', 'N/A'),
                    'employment_type': job.get('job_employment_type', 'N/A'),
                    'description': job.get('job_description', 'N/A')[:200] + '...',
                    'url': job.get('job_apply_link', 'N/A'),
                    'posted': job.get('job_posted_at_datetime_utc', 'N/A')
                })
            
            return pd.DataFrame(jobs)
            
        except Exception as e:
            logger.error(f"JSearch API request failed: {e}")
            return pd.DataFrame()

def main():
    """Example usage of legitimate job APIs"""
    client = JobBoardAPIClient()
    
    # Search using Adzuna
    print("Searching jobs via Adzuna...")
    adzuna_jobs = client.search_adzuna_jobs("Data Scientist", "us", 5)
    if not adzuna_jobs.empty:
        print(adzuna_jobs.head())
        adzuna_jobs.to_csv('adzuna_jobs.csv', index=False)
    
    # Search using JSearch
    print("\nSearching jobs via JSearch...")
    jsearch_jobs = client.search_jsearch_jobs("Data Scientist", 1)
    if not jsearch_jobs.empty:
        print(jsearch_jobs.head())
        jsearch_jobs.to_csv('jsearch_jobs.csv', index=False)

if __name__ == "__main__":
    main()
#Rewrite this file into lowercase in order for it to be below other files
