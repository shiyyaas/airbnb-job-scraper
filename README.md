# Airbnb Job Scraper 🏠

A Python web scraper that collects job listings from [Airbnb's careers page](https://careers.airbnb.com/positions/) and saves them into a structured Excel file.

## 📦 Libraries Used

- `requests` — HTTP requests to fetch web pages
- `BeautifulSoup4` — Parsing HTML content
- `pandas` — Structuring and exporting data
- `openpyxl` — Writing Excel (.xlsx) files

## 📊 Data Collected

| Column | Description |
|---|---|
| JobTitle | Title of the job position |
| Department | Department the job belongs to |
| Location | City/Country of the job |
| WorkType | Remote/Hybrid/On-site |
| ExperienceRequired | Years of experience required |
| SkillsRequired | Required technical skills |
| Salary | Salary range (if available) |
| JobURL | Direct link to the job posting |
| JobDescriptionSummary | Brief summary of the job |

## 🚀 How to Run

1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/airbnb-job-scraper.git
cd airbnb-job-scraper
```

2. Install dependencies

```bash
pip install requests beautifulsoup4 pandas openpyxl
```

3. Run the scraper

```bash
python3 genai_scraper.py
```

4. Output file `Airbnb_Jobs.xlsx` will be generated in the same folder

## 📁 Files

- `genai_scraper.py` — Main scraper script
- `Airbnb_Jobs.xlsx` — Sample output Excel file

## ✅ Features

- Scrapes all job listings across multiple pages (pagination handled)
- Extracts key details for each job
- Gracefully handles missing fields with N/A
- Saves data to a clean, formatted Excel file

## 🏷️ Task

This project was built as part of the **Generative AI Interest Group** tasks on [μLearn](https://app.mulearn.org)

---
