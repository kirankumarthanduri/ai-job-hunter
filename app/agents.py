import re
import json
from serpapi import GoogleSearch
from google import genai
from app.config import GEMINI_API_KEY, SERPAPI_KEY

GEMINI_MODEL = "gemini-2.5-flash"

client = genai.Client(api_key=GEMINI_API_KEY)


def query_builder_agent(user_input):
    print("🧠 Building optimized job search query...")

    prompt = f"""
    Convert this job requirement into a clean Google job search query.

    User Requirement:
    {user_input}

    Return only the optimized search query.
    """

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return response.text.strip()


def job_fetch_agent(query):
    print("🔎 Searching Google Jobs...")

    params = {
        "engine": "google_jobs",
        "q": query,
        "api_key": SERPAPI_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    jobs = []

    if "jobs_results" in results:
        for job in results["jobs_results"]:
            jobs.append({
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("location"),
                "description": job.get("description"),
                "link": job.get("related_links", [{}])[0].get("link", "")
            })

    print(f"✅ Fetched {len(jobs)} jobs")
    return jobs


def ai_filter_agent(jobs, user_input):
    print("🤖 AI Filtering jobs based on user requirements...")

    prompt = f"""
    User Requirement:
    {user_input}

    Below is job data in JSON format:
    {json.dumps(jobs)}

    IMPORTANT:
    - Return ONLY valid JSON
    - No markdown
    - No explanation
    - No backticks
    - Only pure JSON list
    """

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    raw_text = response.text.strip()

    # Strip markdown code fences if present
    if raw_text.startswith("```"):
        lines = raw_text.split("\n")
        raw_text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        filtered_jobs = json.loads(raw_text)
        print(f"✅ {len(filtered_jobs)} jobs matched AI filter")
        return filtered_jobs
    except json.JSONDecodeError as e:
        print(f"⚠ Could not parse AI response as JSON: {e}")
        print("DEBUG Gemini Output:", raw_text)
        return jobs


def email_agent(job, candidate_details):
    print("✉ Generating Personalized Email...")

    prompt = f"""
    Write a professional job application email.

    Candidate:
    Name: {candidate_details['name']}
    Email: {candidate_details['email']}
    Phone: {candidate_details['phone']}
    Profile: {candidate_details['profile']}

    Job:
    {json.dumps(job)}

    Return only email body.
    """

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return response.text


def hr_email_finder_agent(company, job_title):
    print(f"📧 Finding HR email for {company}...")

    params = {
        "engine": "google",
        "q": f'"{company}" HR recruiter email "{job_title}" OR careers OR recruitment contact',
        "api_key": SERPAPI_KEY,
        "num": 5
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    snippets = []
    for result in results.get("organic_results", [])[:5]:
        snippets.append(result.get("snippet", ""))
        snippets.append(result.get("title", ""))

    # First try to extract email directly with regex
    combined = " ".join(snippets)
    emails_found = re.findall(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", combined)
    if emails_found:
        return emails_found[0]

    # Fall back to Gemini extraction
    prompt = f"""
    Extract a valid HR or recruitment email address for the company "{company}" from these search snippets.

    Snippets:
    {chr(10).join(snippets)}

    Return ONLY the email address. If none found, return "Not found".
    """

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    result_text = response.text.strip()
    return result_text if "@" in result_text else None


def enrich_jobs_with_hr_emails_and_emails(jobs, candidate_details):
    """Attach hr_email and email_draft to each job in-place."""
    for job in jobs:
        company = job.get("company", "")
        title = job.get("title", "")
        job["hr_email"] = hr_email_finder_agent(company, title) or ""
        job["email_draft"] = email_agent(job, candidate_details)
    return jobs
