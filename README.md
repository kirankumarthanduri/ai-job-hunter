# AI Job Hunter

An autonomous AI-powered job search and application assistant built with Streamlit, Google Gemini, and SerpAPI.

## Features

- **Smart Job Search** — Builds an optimized search query from your preferences using Gemini AI and fetches live job listings via SerpAPI Google Jobs.
- **AI Filtering** — Filters fetched jobs against your requirements using Gemini to surface the most relevant matches.
- **HR Email Finder** — Automatically searches for HR/recruiter contact emails for each matched company using Google search + Gemini extraction.
- **Bulk Email Generation** — Generates a personalized job application email for every filtered job, ready to review and edit.
- **One-click Apply** — Send your application email (with resume attachment) to each job directly from the app.
- **Excel Export** — Saves all filtered jobs (with HR emails and drafts) to `filtered_jobs.xlsx`.

## Supported Roles

- AI Program Manager
- AI Implementation Lead
- Project Manager - Transformation
- BI Lead
- BI Manager
- Digital Transformation

## Setup

### Prerequisites

- Python 3.9+
- A [SerpAPI](https://serpapi.com/) key
- A [Google Gemini](https://ai.google.dev/) API key
- A Gmail account with an App Password for sending emails

### Installation

```bash
git clone https://github.com/<your-repo>/ai-job-hunter.git
cd ai-job-hunter
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key
SERPAPI_KEY=your_serpapi_key
EMAIL_ADDRESS=your_gmail@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
```

### Run Locally

```bash
streamlit run streamlit_app.py
```

## Deployment

The app is containerized and deployed to AWS EKS. See [`.github/workflows/eks-deploy.yml`](.github/workflows/eks-deploy.yml) and [`k8s/deployment.yaml`](k8s/deployment.yaml) for CI/CD and Kubernetes configuration.

## How It Works

1. Fill in your job preferences and candidate details.
2. Click **Search Jobs** — the app queries, filters, finds HR emails, and generates application emails for all matched jobs automatically.
3. Review each job card: edit the HR email or draft if needed.
4. Click **Send Email** on any job to apply with your resume attached.
