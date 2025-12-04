from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import pandas as pd
from ftfy import fix_text
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue

MAX_WORKERS = 4  
CHECKPOINT_EVERY = 500
TOTAL_PAGES = 831
MAX_RETRIES = 1
PAGE_LOAD_TIMEOUT = 8
DETAIL_PAGE_TIMEOUT = 6

jobs_queue = queue.Queue()
jobs_count = 0
jobs_lock = threading.Lock()

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-images")  
    options.add_argument("--disable-javascript")  
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    options.page_load_strategy = 'eager'  
    
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
    }
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver

def safe_find_text(parent, by, selector, default="NA"):
    """Safely find and extract text with retry logic"""
    for _ in range(2):
        try:
            elems = parent.find_elements(by, selector)
            return elems[0].text.strip() if elems else default
        except StaleElementReferenceException:
            time.sleep(0.1)
    return default

def clean_text(text):
    if not text or text == "NA":
        return text
    text = fix_text(text)
    text = text.replace("\u00a0", " ").strip()
    text = text.lstrip("•●-–= ").rstrip("•●-–= ")
    return text

def extract_job_description(driver):
    try:
        desc_section = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section.css-5pnqc5 div"))
        )
        
        all_text = desc_section.get_attribute('innerText')
        if all_text:
            lines = [clean_text(line) for line in all_text.split('\n') if line.strip()]
            return "\n".join(f"- {line}" for line in lines[:20])  
        return "NA"
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
        return "NA"

def get_requirements(driver):
    try:
        section = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section.css-5pnqc5 div.css-1lqavbg"))
        )
        all_text = section.get_attribute('innerText')
        if all_text:
            lines = [clean_text(line) for line in all_text.split('\n') if line.strip()]
            return "\n".join(f"- {line}" for line in lines[:15])  
        return "NA"
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
        return "NA"

def scrape_job_details(driver, link, title, retry_count=0):
    if retry_count >= MAX_RETRIES:
        return None
    
    try:
        driver.get(link)
        
        WebDriverWait(driver, DETAIL_PAGE_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.css-bjn8wh"))
        )
        
        job_data = {}
        
        section = driver.find_element(By.CSS_SELECTOR, "div.css-bjn8wh")
        job_data["Title"] = clean_text(title)
        job_data["Company"] = safe_find_text(section, By.CLASS_NAME, "css-9iujih")
        job_data["Date"] = safe_find_text(section, By.CLASS_NAME, "css-154erwh")
        job_data["Job Type"] = safe_find_text(section, By.CSS_SELECTOR, ".css-dmid6b.eoyjyou0")
        job_data["Work Setting"] = safe_find_text(section, By.CSS_SELECTOR, ".css-oos404.eoyjyou0")
        
        try:
            strong = driver.find_element(By.CSS_SELECTOR, "strong.css-1vlp604")
            location_text = strong.get_attribute('innerText')
            if ',' in location_text:
                job_data["Location"] = location_text.split(',')[-1].strip()
            else:
                job_data["Location"] = location_text.strip()
        except:
            job_data["Location"] = "NA"
        
        try:
            details_section = driver.find_element(By.CSS_SELECTOR, "section.css-pbzohz")
            details_text = details_section.get_attribute('innerText')
            
            lines = details_text.split('\n')
            details_dict = {}
            for i in range(len(lines)-1):
                if ':' in lines[i] or lines[i].endswith('Needed') or lines[i].endswith('Level'):
                    key = lines[i].replace(':', '').strip()
                    value = lines[i+1].strip() if i+1 < len(lines) else "NA"
                    details_dict[key] = value
            
            job_data["Experience Needed"] = details_dict.get("Experience Needed", "NA")
            job_data["Career Level"] = details_dict.get("Career Level", "NA")
            job_data["Education Level"] = details_dict.get("Education Level", "NA")
            job_data["Salary"] = details_dict.get("Salary", "NA")
            job_data["Job Categories"] = details_dict.get("Job Categories", "NA")
            
            try:
                skills_elements = details_section.find_elements(By.CSS_SELECTOR, "a.css-g65o95 span.css-1vi25m1")
                job_data["Skills"] = ", ".join([s.text for s in skills_elements[:10]])  
            except:
                job_data["Skills"] = "NA"
        except:
            job_data["Experience Needed"] = "NA"
            job_data["Career Level"] = "NA"
            job_data["Education Level"] = "NA"
            job_data["Salary"] = "NA"
            job_data["Job Categories"] = "NA"
            job_data["Skills"] = "NA"
        
        job_data["Job Description"] = extract_job_description(driver)
        job_data["Job Requirements"] = get_requirements(driver)
        job_data["Link"] = link
        
        return job_data
        
    except (TimeoutException, StaleElementReferenceException) as e:
        return scrape_job_details(driver, link, title, retry_count + 1)
    except Exception as e:
        return None

def scrape_page(page_num, driver=None):
    if driver is None:
        driver = create_driver()
        local_driver = True
    else:
        local_driver = False
    
    page_jobs = []
    url = f"https://wuzzuf.net/search/jobs/?a=navbl&start={page_num}"
    
    try:
        driver.get(url)
        
        WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
            EC.presence_of_element_located((By.CLASS_NAME, "css-pkv5jc"))
        )
        
        job_cards = driver.find_elements(By.CLASS_NAME, "css-pkv5jc")
        
        jobs_to_scrape = []
        for job in job_cards:
            try:
                title_elem = job.find_element(By.CSS_SELECTOR, "a.css-o171kl")
                title = title_elem.text.strip()
                link = title_elem.get_attribute("href")
                jobs_to_scrape.append((title, link))
            except:
                continue
        
        for title, link in jobs_to_scrape:
            job_data = scrape_job_details(driver, link, title)
            if job_data:
                page_jobs.append(job_data)
                
                with jobs_lock:
                    global jobs_count
                    jobs_count += 1
        
        
    except TimeoutException:
        print(f"Page {page_num} timeout")
    except Exception as e:
        print(f"Page {page_num} error: {str(e)[:50]}")
    finally:
        if local_driver:
            driver.quit()
    
    return page_jobs

def save_checkpoint(jobs_data):
    if not jobs_data:
        return
    
    df = pd.DataFrame(jobs_data)
    file_exists = os.path.exists("wuzzuf_full_jobs.csv")
    df.to_csv("wuzzuf_full_jobs.csv", index=False, mode='a',
              header=not file_exists, encoding='utf-8-sig')

def worker_thread(page_nums):
    driver = create_driver()
    all_jobs = []
    
    try:
        for page_num in page_nums:
            page_jobs = scrape_page(page_num, driver)
            all_jobs.extend(page_jobs)
            
            if len(all_jobs) >= CHECKPOINT_EVERY:
                save_checkpoint(all_jobs)
                all_jobs = []
        
        if all_jobs:
            save_checkpoint(all_jobs)
            
    finally:
        driver.quit()
    
    return len(all_jobs)

def main():
    start_time = time.time()
    
    if os.path.exists("wuzzuf_full_jobs.csv"):
        os.remove("wuzzuf_full_jobs.csv")
        pages = list(range(TOTAL_PAGES))
    chunk_size = len(pages) // MAX_WORKERS
    page_chunks = [pages[i:i + chunk_size] for i in range(0, len(pages), chunk_size)]
    
    if len(page_chunks) > MAX_WORKERS:
        page_chunks[-2].extend(page_chunks[-1])
        page_chunks = page_chunks[:-1]
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(worker_thread, chunk) for chunk in page_chunks]
        
        for future in as_completed(futures):
            try:
                result = future.result()
            except Exception as e:
                print(f"Worker failed: {e}")
    
    elapsed_time = time.time() - start_time
    print(f"Scraping completed in {elapsed_time/60:.1f} minutes")
    print(f"Total jobs scraped: {jobs_count}")
    
    if os.path.exists("wuzzuf_full_jobs.csv"):
        df = pd.read_csv("wuzzuf_full_jobs.csv")

if __name__ == "__main__":
    main()