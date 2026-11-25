# AI Job Application Agent

A Python command-line prototype that finds recent public LinkedIn job listings, uses Google Gemini through LangChain to tailor resume content for each listing, generates a Word resume from a template, and emails the result with the job link.

> **This tool prepares application materials; it does not submit job applications.** Review every generated resume for accuracy before using it.

## How it works

Running `main.py` performs this flow:

1. Searches LinkedIn's public job listings for **AI Engineer** roles in **Ontario, Canada**, using a four-hour recency filter and one results page by default.
2. Fetches each listing's description and skips entries without a title, company, or description.
3. Loads `current_resume.json` as the source resume for each job.
4. Uses Gemini (`gemini-2.5-flash-lite`) to tailor the professional summary, skills, work highlights, and project descriptions to the job description.
5. Renders the tailored data into `Ajay_Luhar_Demo_Resume.docx` and saves a `.docx` file under `Tailored_Resumes/`.
6. Emails the job title, company, job link, and resume attachment when SMTP credentials are configured. If they are not configured, it skips the email step.

The temporary tailored JSON file is deleted after document generation. Generated Word documents remain in `Tailored_Resumes/`.

## Project files

| File | Purpose |
| --- | --- |
| `main.py` | Runs the scrape, tailoring, document generation, and email workflow. |
| `job_scrapper.py` | Queries LinkedIn's public jobs endpoint and extracts listing descriptions. |
| `resume_generator.py` | Uses LangChain and Google Gemini to tailor resume sections. |
| `convert_json_to_doc.py` | Converts resume JSON into a Word document using `docxtpl` and `python-docx`. |
| `email_notifier.py` | Sends a Gmail SMTP email with the generated resume attached. |
| `current_resume.json` | Base resume data used for every job. Replace this with your own accurate information. |
| `Ajay_Luhar_Demo_Resume.docx` | Word template used to render the final resume. |
| `requirements.txt` | Python package dependencies. |

## Requirements

- Python 3.10 or newer
- A Google AI API key for Gemini
- A Gmail account and an app password if you want email notifications
- Internet access to reach LinkedIn's public job pages, Google's API, and Gmail SMTP

## Setup

Clone the repository and enter its directory:

```bash
git clone https://github.com/Ajju-Panchal/AI-Job-Application-Agent.git
cd AI-Job-Application-Agent
```

Create and activate a virtual environment, then install the pinned dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source .venv/bin/activate
```

Install packages:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configuration

### Google Gemini API key

`resume_generator.py` currently passes a placeholder string (`"Google API Key here"`) as `google_api_key`; it does not read `GOOGLE_API_KEY` from the environment despite the nearby comment. Before running the agent, replace that placeholder with your key, or update the code to read the key from an environment variable. Keep API keys out of source control.

For example, the code can use:

```python
google_api_key=os.environ["GOOGLE_API_KEY"]
```

Then set the variable in your shell before starting the program.

### Email notifications (optional)

`email_notifier.py` reads these environment variables:

- `SENDER_EMAIL`: Gmail address used to send notifications
- `SENDER_PASSWORD`: Gmail app password (not your normal account password)

The recipient address is currently fixed in `email_notifier.py`. Change `receiver_email` there if needed. If either sender variable is missing, email is skipped; the resume generation flow can continue.

PowerShell example:

```powershell
$env:SENDER_EMAIL = "you@example.com"
$env:SENDER_PASSWORD = "your-gmail-app-password"
```

macOS or Linux example:

```bash
export SENDER_EMAIL="you@example.com"
export SENDER_PASSWORD="your-gmail-app-password"
```

Do not commit real credentials. For local development, store them in a local `.env` file only if you also add it to `.gitignore` and load it explicitly in the application; the current code does not automatically load `.env` files.

## Before the first run

1. Replace `current_resume.json` with your own resume. Preserve the JSON structure and valid JSON syntax so the template and tailoring code can use its fields.
2. Update or replace the `.docx` template. Its `docxtpl` placeholders must match the keys in the resume JSON; the renderer also builds a `formatted_skills` list for the skills section.
3. Set up the Gemini key as described above.
4. Review the configuration in `main.py` (`keyword`, `location`, and `pages`) and the email recipient in `email_notifier.py`.

### Important: converter import side effect

`convert_json_to_doc.py` currently calls `generate_resume_from_template(...)` in a module-level example at the bottom of the file. Because `main.py` imports that module, the example runs during startup and expects a `tailored_resume.json` file to exist. A clean checkout may fail before the main workflow begins. Move that example call inside an `if __name__ == "__main__":` guard (or remove it) before running `main.py`.

## Run

After completing the configuration and addressing the converter import side effect:

```bash
python main.py
```

Generated resumes are written to:

```text
Tailored_Resumes/
```

The current output filename includes the company name. If multiple listings have the same company name, they may overwrite one another.

## Customize search

Edit the call to `scrape_linkedin_jobs(...)` in `main.py`:

```python
jobs = await scrape_linkedin_jobs(
    keyword="AI Engineer",
    location="Ontario, Canada",
    pages=1,
)
```

Each page requests up to ten listings. The scraper currently filters LinkedIn results to postings from the past four hours (`f_TPR=r14400`) and waits between description requests. LinkedIn can change or restrict its public pages, so scraping may return no results or fail intermittently.

## Privacy and responsible use

- The base resume contains personal information. Keep your own resume file private and do not commit sensitive personal data to a public repository.
- Tailoring uses a third-party LLM API. Review the provider's data handling terms before sending resume or job data.
- LLM-generated resume edits can be inaccurate. Check all claims, dates, skills, and experience before submitting an application.
- This prototype does not track previously processed jobs, prevent duplicate alerts, or apply on your behalf.

## Troubleshooting

- **Google API authentication error:** Make sure `resume_generator.py` uses your valid API key; the checked-in placeholder is not a working key.
- **Missing `tailored_resume.json` at startup:** Address the module-level example call in `convert_json_to_doc.py` as described above.
- **No jobs found:** Try another keyword or location, increase `pages`, or retry later. Results depend on LinkedIn's public endpoint.
- **Email skipped:** Set both `SENDER_EMAIL` and `SENDER_PASSWORD` in the current shell.
- **Email authentication fails:** Use a Gmail app password and confirm that Gmail SMTP access is available for the account.



