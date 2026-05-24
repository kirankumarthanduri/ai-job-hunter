import streamlit as st
import os
from app.agents import (
    query_builder_agent,
    job_fetch_agent,
    ai_filter_agent,
    email_agent,
    enrich_jobs_with_hr_emails_and_emails
)
from app.email_service import send_email
from app.excel_service import save_jobs_to_excel

st.set_page_config(page_title="AI Job Hunter ASP", layout="wide")

st.title("🤖 Autonomous AI Job Hunter")
st.markdown("Search → Filter → Generate Email → Apply")

# -------------------------------
# JOB FILTER SECTION
# -------------------------------

st.header("🔎 Job Preferences")

col1, col2, col3 = st.columns(3)

with col1:
    position = st.selectbox(
        "Select Position",
        [
            "AI Program Manager",
            "AI Implementation Lead",
            "Project Manager - Transformation",
            "BI Lead",
            "BI Manager",
            "Digital Transformation"
        ]
    )

with col2:
    experience = st.selectbox(
        "Experience Level",
        [
            "Fresher",
            "0-1 years",
            "1-3 years",
            "3-5 years",
            "5+ years"
        ]
    )

with col3:
    location = st.selectbox(
        "Location",
        [
            "India",
            "USA",
            "Remote",
            "Europe",
            "Canada"
        ]
    )

skills = st.text_input("Enter Required Skills (comma separated)")

# -------------------------------
# CANDIDATE SECTION
# -------------------------------

st.header("👤 Candidate Details")

col4, col5 = st.columns(2)

with col4:
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")

with col5:
    phone = st.text_input("Your Phone")
    profile = st.text_area("Short Profile Summary")

resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

# -------------------------------
# SEARCH BUTTON
# -------------------------------

if st.button("🚀 Search Jobs"):

    if not name or not email:
        st.warning("Please fill in your Name and Email before searching.")
    else:
        user_input = f"""
        Position: {position}
        Experience: {experience}
        Location: {location}
        Skills: {skills}
        """

        candidate = {
            "name": name,
            "email": email,
            "phone": phone,
            "profile": profile
        }

        optimized_query = query_builder_agent(user_input)
        jobs = job_fetch_agent(optimized_query)

        if jobs:
            filtered_jobs = ai_filter_agent(jobs, user_input)

            if filtered_jobs:
                with st.spinner("Finding HR emails and preparing application emails for all jobs..."):
                    enriched = enrich_jobs_with_hr_emails_and_emails(filtered_jobs, candidate)
                st.session_state.jobs = enriched
                save_jobs_to_excel(enriched)
                st.success(f"{len(enriched)} jobs found and emails prepared!")
            else:
                st.warning("No matching jobs found.")
        else:
            st.error("No jobs found.")


# -------------------------------
# DISPLAY JOBS IF AVAILABLE
# -------------------------------

if "jobs" in st.session_state:

    st.subheader("📋 Filtered Jobs")

    # Save resume once for reuse across all send actions
    resume_path = None
    if resume_file:
        resume_dir = os.path.join("/tmp", "resumes")
        os.makedirs(resume_dir, exist_ok=True)
        resume_path = os.path.join(resume_dir, resume_file.name)
        with open(resume_path, "wb") as f:
            f.write(resume_file.getbuffer())

    for i, job in enumerate(st.session_state.jobs):
        with st.expander(f"{job['title']} - {job['company']}"):
            st.write("📍 Location:", job["location"])
            st.write("🔗 Link:", job["link"])
            st.write(job["description"])

            st.markdown("---")

            # HR email row — editable so user can correct if wrong
            hr_email_key = f"hr_email_{i}"
            found_hr = job.get("hr_email", "")
            hr_email_input = st.text_input(
                "HR Email",
                value=found_hr,
                key=hr_email_key,
                placeholder="HR email (auto-found or enter manually)"
            )

            # Draft email — editable
            draft_key = f"draft_{i}"
            draft = st.text_area(
                "Application Email Draft",
                value=job.get("email_draft", ""),
                height=250,
                key=draft_key
            )

            if st.button(f"📨 Send Email for {job['title']}", key=f"send_{i}"):
                if not hr_email_input:
                    st.warning("Please enter the HR email before sending.")
                else:
                    try:
                        send_email(
                            hr_email_input,
                            f"Application for {job['title']}",
                            draft,
                            attachment_path=resume_path
                        )
                        st.success(f"✅ Email sent to {hr_email_input}!")
                    except Exception as e:
                        st.error(f"❌ Failed to send email: {e}")
