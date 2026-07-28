import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

BASE_URL = "https://careers.airbnb.com"
JOBS_URL = "https://careers.airbnb.com/positions/"
HEADERS  = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def scrape_job_listings():
    """Scrape all job cards across all pages."""

    all_jobs = []
    page_num = 1

    while True:
        # Build URL for each page
        if page_num == 1:
            url = JOBS_URL
        else:
            url = f"{BASE_URL}/positions/page/{page_num}/"

        print(f"  Scraping page {page_num}: {url}")

        response = requests.get(url, headers=HEADERS)

        # If page doesn't exist, stop
        if response.status_code == 404:
            print(f"  No more pages. Stopped at page {page_num}.")
            break

        if response.status_code != 200:
            print(f"  Failed to fetch page {page_num}. Status: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        # Find all job cards on this page
        job_cards = soup.find_all("li", class_=lambda c: c and "inner-grid" in c)

        # If no jobs found on this page, stop
        if not job_cards:
            print(f"  No jobs found on page {page_num}. Stopping.")
            break

        print(f"  Found {len(job_cards)} jobs on page {page_num}")

        for card in job_cards:
            try:
                title_span = card.find("span", class_="text-size-4")
                if not title_span:
                    continue

                a_tag     = title_span.find("a")
                job_title = a_tag.get_text(strip=True) if a_tag else "N/A"
                job_url   = a_tag["href"] if a_tag else "N/A"

                if job_url.startswith("/"):
                    job_url = BASE_URL + job_url

                meta_div = card.find("div", class_=lambda c: c and "text-size-3" in c)
                spans    = meta_div.find_all("span") if meta_div else []

                clean_spans = [
                    s.get_text(strip=True)
                    for s in spans
                    if s.get_text(strip=True) not in ["•", ""]
                ]

                department = clean_spans[0] if len(clean_spans) > 0 else "N/A"
                work_type  = clean_spans[1] if len(clean_spans) > 1 else "N/A"

                location_div = card.find(
                    "div", class_=lambda c: c and "col-span-3" in c
                )
                location_span = (
                    location_div.find("span") if location_div else None
                )
                location = (
                    location_span.get_text(strip=True)
                    if location_span else "N/A"
                )

                all_jobs.append({
                    "job_title"  : job_title,
                    "department" : department,
                    "work_type"  : work_type,
                    "location"   : location,
                    "job_url"    : job_url,
                })

            except Exception as e:
                print(f"  Error parsing job card: {e}")
                continue

        # Check if there is a next page
        next_link = soup.find("link", rel="next")
        if not next_link:
            print(f"  No more pages after page {page_num}.")
            break

        page_num += 1
        time.sleep(1)  # Be polite between page requests

    print(f"\n  Total jobs found across all pages: {len(all_jobs)}")
    return all_jobs


def scrape_job_details(job_url):
    """Visit each job page and extract Description, Skills, Experience."""

    try:
        response = requests.get(job_url, headers=HEADERS)

        if response.status_code != 200:
            return "N/A", "N/A", "N/A"

        soup = BeautifulSoup(response.text, "html.parser")

        # Airbnb job pages have the description in a main content div
        desc_div = soup.find("div", class_=lambda c: c and "prose" in c)

        if not desc_div:
            # Fallback: grab the largest text block
            desc_div = soup.find("main")

        full_text = desc_div.get_text(separator=" ", strip=True) if desc_div else ""

        # First 300 characters as summary
        description_summary = full_text[:300] + "..." if len(full_text) > 300 else full_text

        # Extract experience
        experience = "N/A"
        exp_pattern = re.search(
            r"(\d+\+?\s*(?:to\s*\d+)?\s*years?[^\.\,]{0,30})",
            full_text,
            re.IGNORECASE
        )
        if exp_pattern:
            experience = exp_pattern.group(1).strip()

        # Extract skills from keywords
        skill_keywords = [
            "Python", "SQL", "Java", "JavaScript", "TypeScript",
            "React", "Node.js", "AWS", "GCP", "Azure", "Docker",
            "Kubernetes", "Spark", "Kafka", "TensorFlow", "PyTorch",
            "Machine Learning", "Deep Learning", "NLP", "Data Analysis",
            "Tableau", "Excel", "R", "Scala", "Go", "Swift", "Kotlin",
            "C++", "Ruby", "Airflow", "dbt", "Hadoop", "Snowflake"
        ]

        found_skills = [
            skill for skill in skill_keywords
            if re.search(rf"\b{re.escape(skill)}\b", full_text, re.IGNORECASE)
        ]

        skills = ", ".join(found_skills) if found_skills else "N/A"

        return description_summary, experience, skills

    except Exception as e:
        print(f"  Error fetching job details: {e}")
        return "N/A", "N/A", "N/A"


def main():
    print("Airbnb Career Page Scraper")

    # Scrape all pages
    all_jobs = scrape_job_listings()[:20]

    if not all_jobs:
        print("No jobs found. Exiting.")
        return

    print(f"\n  Fetching details for each job (this may take a while...)\n")

    enriched_jobs = []

    for i, job in enumerate(all_jobs, start=1):
        print(f"  [{i}/{len(all_jobs)}]  {job['job_title'][:60]}...")

        description, experience, skills = scrape_job_details(job["job_url"])

        enriched_jobs.append({
            "JobTitle"              : job["job_title"],
            "Department"            : job["department"],
            "Location"              : job["location"],
            "WorkType"              : job["work_type"],
            "ExperienceRequired"    : experience,
            "SkillsRequired"        : skills,
            "Salary"                : "N/A",
            "JobURL"                : job["job_url"],
            "JobDescriptionSummary" : description,
        })

        time.sleep(1)  # Be polite between requests

    # Save to Excel
    print(f"\n  Saving data to Excel...")

    df = pd.DataFrame(enriched_jobs)

    output_file = "Airbnb_Jobs.xlsx"
    df.to_excel(output_file, index=False)

    print(f"  Done! {len(enriched_jobs)} jobs saved to '{output_file}'")


if __name__ == "__main__":
    main()