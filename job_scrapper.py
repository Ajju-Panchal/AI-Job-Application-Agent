'''

import asyncio
import httpx
from bs4 import BeautifulSoup
import csv

async def main() -> None:
    url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    params = {
        "keywords": "AI Engineer",
        "location": "Canada",
        "trk": "public_jobs_jobs-search-bar_search-submit",
        "start": "0",
        "f_TPR": "r3600"  # r3600 = Past 1 hour (3600 seconds)
    }
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=1, i",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        # Adding a User-Agent is highly recommended for individual page requests
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }

    job_postings = []
    pages = 3

    # Open the HTTP client once for all requests
    async with httpx.AsyncClient(timeout=15.0) as client:
        for page in range(pages):
            print(f"Scraping search page {page + 1}...")
            params["start"] = str(page * 10)

            response = await client.get(url, headers=headers, params=params)
            soup = BeautifulSoup(response.content, "lxml")
            job_li_elements = soup.select("li")

            for job_li_element in job_li_elements:
                link_element = job_li_element.select_one('a[data-tracking-control-name="public_jobs_jserp-result_search-card"]')
                
                # We split the URL at the '?' to remove tracking tags. It makes the URL cleaner.
                link = link_element["href"].split('?')[0] if link_element else None

                title_element = job_li_element.select_one("h3.base-search-card__title")
                title = title_element.text.strip() if title_element else None

                company_element = job_li_element.select_one("h4.base-search-card__subtitle")
                company = company_element.text.strip() if company_element else None

                publication_date_element = job_li_element.select_one("time.job-search-card__listdate")
                publication_date = publication_date_element["datetime"] if publication_date_element else None

                description = None
                
                # --- NEW LOGIC: Fetch the individual job description ---
                if link:
                    try:
                        print(f" Fetching description for: {title}...")
                        job_response = await client.get(link, headers=headers)
                        job_soup = BeautifulSoup(job_response.content, "lxml")
                        
                        # LinkedIn public job descriptions are usually inside this div class
                        desc_element = job_soup.select_one("div.show-more-less-html__markup")
                        
                        if desc_element:
                            # get_text with a newline separator keeps paragraph formatting
                            description = desc_element.get_text(separator="\n", strip=True)
                        
                        # CRITICAL: Pause for 2 seconds to avoid getting IP banned by LinkedIn
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        print(f"  -> Error fetching description: {e}")

                job_posting = {
                    "url": link,
                    "title": title,
                    "company": company,
                    "publication_date": publication_date,
                    "description": description  # Add description to our dictionary
                }
                job_postings.append(job_posting)

    # Export the scraped data to CSV
    print(f"\nDone! Exporting {len(job_postings)} jobs to CSV.")
    with open("job_postings.csv", mode="w", newline="", encoding="utf-8") as file:
        # Added "description" to the fieldnames
        writer = csv.DictWriter(file, fieldnames=["url", "title", "company", "publication_date", "description"])
        writer.writeheader()
        writer.writerows(job_postings)

# Run the async function
if __name__ == "__main__":
    asyncio.run(main())
'''

import asyncio
import httpx
from bs4 import BeautifulSoup

async def scrape_linkedin_jobs(keyword="AI Engineer", location="Ontario, Canada", pages=1) -> list:
    url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    params = {
        "keywords": keyword,
        "location": location,
        "trk": "public_jobs_jobs-search-bar_search-submit",
        "start": "0",
        "f_TPR": "r14400"  # Past 4 hours
    }
    headers = {
        "accept": "*/*",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }

    job_postings = []

    async with httpx.AsyncClient(timeout=15.0) as client:
        for page in range(pages):
            print(f"[Scraper] Scraping search page {page + 1}...")
            params["start"] = str(page * 10)

            response = await client.get(url, headers=headers, params=params)
            soup = BeautifulSoup(response.content, "lxml")
            job_li_elements = soup.select("li")

            for job_li_element in job_li_elements:
                link_element = job_li_element.select_one('a[data-tracking-control-name="public_jobs_jserp-result_search-card"]')
                link = link_element["href"].split('?')[0] if link_element else None

                title_element = job_li_element.select_one("h3.base-search-card__title")
                title = title_element.text.strip() if title_element else None

                company_element = job_li_element.select_one("h4.base-search-card__subtitle")
                company = company_element.text.strip() if company_element else None

                description = None
                
                # Fetch the individual job description
                if link and title:
                    try:
                        print(f"[Scraper] Fetching description for: {title} at {company}...")
                        job_response = await client.get(link, headers=headers)
                        job_soup = BeautifulSoup(job_response.content, "lxml")
                        
                        desc_element = job_soup.select_one("div.show-more-less-html__markup")
                        if desc_element:
                            description = desc_element.get_text(separator="\n", strip=True)
                        
                        await asyncio.sleep(2) # Prevent IP Ban
                    except Exception as e:
                        print(f"[Scraper] Error fetching description: {e}")

                if title and company and description:
                    job_postings.append({
                        "url": link,
                        "title": title,
                        "company": company,
                        "description": description 
                    })

    return job_postings

# If you run this file directly, it will test itself without breaking main.py
if __name__ == "__main__":
    jobs = asyncio.run(scrape_linkedin_jobs())
    print(f"Found {len(jobs)} jobs.")