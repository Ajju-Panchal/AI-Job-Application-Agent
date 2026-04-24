import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.tools import tool

# Make sure your GOOGLE_API_KEY is set in your environment variables
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.1, # Low temperature ensures strict adherence to JSON formatting
    google_api_key="Google API Key here"

)

# Global variables to hold state for the current run
temp_data = {}
current_job_title = ""
current_job_description = ""

# Helper function to ensure the LLM output is clean JSON
def clean_json_response(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"): 
        text = text[7:]
    elif text.startswith("```"): 
        text = text[3:]
    if text.endswith("```"): 
        text = text[:-3]
    return text.strip()

@tool
def update_prof_summary() -> str:
    """Updates the professional summary. Call this tool first."""
    global temp_data, current_job_title, current_job_description
    prompt = f"""
    Rewrite this professional summary to align with a {current_job_title} role.
    Ensure it highlights relevant experience from the JD: {current_job_description}
    Current Summary: {temp_data.get('professional_summary', '')}
    Return ONLY the raw updated text string.
    """
    resp = llm.invoke(prompt)
    temp_data['professional_summary'] = resp.content.strip()
    print("--- Tool Executed: Professional Summary Updated ---")
    return "Summary updated successfully."

@tool
def update_tech_skills() -> str:
    """Updates the technical skills section. Call this tool second."""
    global temp_data, current_job_title, current_job_description
    prompt = f"""
    Reorder and optimize these technical skills for a {current_job_title} role based on this JD: {current_job_description}.
    Ensure skills like FastAPI, Django, and AWS are prioritized if present. I don't need two Priortized skills and Optimized Skills, just make the changes according to current skills format given below.
    Current Skills: {json.dumps(temp_data.get('technical_skills', {}))}. Keep the same formatting.
    Return ONLY valid JSON representing the dictionary. Do not include markdown formatting.
    """
    resp = llm.invoke(prompt)
    try:
        temp_data['technical_skills'] = json.loads(clean_json_response(resp.content))
        print("--- Tool Executed: Technical Skills Updated ---")
        return "Skills updated successfully."
    except Exception as e: 
        return f"Failed to parse JSON: {e}"

@tool
def update_work_exp() -> str:
    """Updates the work experience section. Call this tool third."""
    global temp_data, current_job_title, current_job_description
    prompt = f"""
    Tailor the 'highlights' arrays in this work experience for a {current_job_title} role.
    Focus on backend scaling, API integrations, and AI/ML deployments as mentioned in the JD: {current_job_description}.
    Current Experience: {json.dumps(temp_data.get('work_experience', []))}
    Return ONLY valid JSON representing the list of dictionaries.
    """
    resp = llm.invoke(prompt)
    try:
        temp_data['work_experience'] = json.loads(clean_json_response(resp.content))
        print("--- Tool Executed: Work Experience Updated ---")
        return "Experience updated successfully."
    except Exception as e: 
        return f"Failed to parse JSON: {e}"

@tool
def update_project() -> str:
    """Updates the projects section. Call this tool fourth."""
    global temp_data, current_job_title, current_job_description
    prompt = f"""
    Tailor the descriptions of these projects for a {current_job_title} role.
    Emphasize Python, REST APIs, ML model deployments, and AWS based on the JD: {current_job_description}.
    Current Projects: {json.dumps(temp_data.get('projects', []))}
    Return ONLY valid JSON representing the list of dictionaries.
    """
    resp = llm.invoke(prompt)
    try:
        temp_data['projects'] = json.loads(clean_json_response(resp.content))
        print("--- Tool Executed: Projects Updated ---")
        return "Projects updated successfully."
    except Exception as e: 
        return f"Failed to parse JSON: {e}"

def generate_tailored_json(job_title: str, job_description: str, base_resume_path: str, output_json_path: str):
    """
    This function resets the state for each new job and triggers the LLM agent to tailor the resume.
    """
    global temp_data, current_job_title, current_job_description
    
    print(f"\n[Agent] Tailoring resume for: {job_title}")
    
    # 1. Reset the state for THIS specific job so data doesn't bleed between loops
    current_job_title = job_title
    current_job_description = job_description
    
    # Load a fresh copy of the base resume
    with open(base_resume_path, 'r') as file:
        temp_data = json.load(file)

    # 2. Create the Agent with Strict Execution Instructions
    system_instruction = """
    You are an expert resume writer AI. 
    To complete the user's request, you MUST execute ALL FOUR of the following tools in order:
    1. update_prof_summary
    2. update_tech_skills
    3. update_work_exp
    4. update_project

    Do not stop until all four tools have been successfully called. 
    Once finished, inform the user that the JSON state has been fully updated.
    """

    agent = create_agent(
        model=llm,
        tools=[update_prof_summary, update_tech_skills, update_work_exp, update_project],
        system_prompt=system_instruction,
    )

    # 3. Run the Agent
    agent.invoke({
        "messages": [{"role": "user", "content": f"Update my resume for the {job_title} position."}]
    })

    # 4. Save the tailored JSON
    with open(output_json_path, 'w') as outfile:
        json.dump(temp_data, outfile, indent=2)
    
    print(f"[Agent] Saved JSON to {output_json_path}")
