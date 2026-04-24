import asyncio
import os
import re

# Import your modules
from job_scrapper import scrape_linkedin_jobs
from resume_generator import generate_tailored_json
from convert_json_to_doc import generate_resume_from_template
from email_notifier import send_job_alert # <--- NEW IMPORT



# Helper to clean company names for file saving (removes illegal characters)
def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).replace(" ", "_")

async def run_ai_agent():
    print("========================================")
    print("STARTING JOB APPLICATION AI AGENT")
    print("========================================")

    # 1. Scrape the Jobs
    # I set pages=1 to keep testing fast. Increase this when ready.
    jobs = await scrape_linkedin_jobs(keyword="AI Engineer", location="Ontario, Canada", pages=1)
    print("Jobs count: ",len(jobs))

    if not jobs:
        print("No jobs found in the last hour. Exiting.")
        return

    print(f"\n---> Found {len(jobs)} jobs with full descriptions. Beginning Tailoring Process...\n")

    # Ensure output directory exists
    os.makedirs("Tailored_Resumes", exist_ok=True)

    # 2. Loop through each job found
    for index, job in enumerate(jobs):
        company_clean = clean_filename(job['company'])
        
        # Create dynamic file names for this specific job
        temp_json_path = f"Tailored_Resumes/temp_{company_clean}.json"
        final_doc_path = f"Tailored_Resumes/Ajay_Luhar_{company_clean}_Resume.docx"

        print(f"\n--- Processing Job {index + 1}/{len(jobs)}: {job['title']} at {job['company']} ---")

        # Step A: Give the Job Description to the LLM to create tailored JSON
        generate_tailored_json(
            job_title=job['title'],
            job_description=job['description'],
            base_resume_path='current_resume.json', 
            output_json_path=temp_json_path
        )

        # Step B: Convert the tailored JSON into the final Word Document
        print(f"[Docx] Generating Word Document...")
        generate_resume_from_template(
            json_filepath=temp_json_path, 
            template_filepath='Ajay_Luhar_Demo_Resume.docx', 
            output_filepath=final_doc_path
        )

        # Optional Step C: Delete the temporary JSON to keep your folder clean
        if os.path.exists(temp_json_path):
            os.remove(temp_json_path)

        # Step D: Send the email with the attachment <--- NEW CODE
        send_job_alert(
            company_name=job['company'],
            job_title=job['title'],
            job_link=job['url'],
            resume_path=final_doc_path
        )
            
        print(f"SUCCESS! Ready to apply to {job['company']}.")

if __name__ == "__main__":
    asyncio.run(run_ai_agent())