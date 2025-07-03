from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from sentence_transformers import SentenceTransformer, util
from time import sleep
import json
import os


# Load AI model
model = SentenceTransformer('all-MiniLM-L6-v2')


# Your ideal job description
target_job_description = """
Looking for Software Engineering Intern, Software Development Intern, Programming Intern,
Computer Science Intern, Web Development Intern, Full Stack Intern, Frontend Intern,
Backend Intern, Python Intern, Java Intern, JavaScript Intern, React Intern,
Node.js Intern, Database Intern, API Intern, Mobile App Intern, UI/UX Intern,
DevOps Intern, Cloud Intern, AWS Intern, Azure Intern, Git Intern, Agile Intern,
Scrum Intern, Testing Intern, QA Intern, Debugging Intern, Code Review Intern,
Version Control Intern, Software Testing Intern.
"""


# Configuration
CONFIG = {
    'min_match_score': 60,  # Minimum score to consider applying (lowered from 75)
    'max_jobs_per_page': 5,  # Maximum jobs to process per page
    'max_pages': 1,  # Maximum pages to search
    'wait_timeout': 10,  # Timeout for element waits
    'scroll_pause': 2,  # Pause between scrolls
}


# --- CONFIG ---
SEARCH_TERM = "Software Internship"
LOCATION = "United States"
MAX_JOBS_TO_APPLY = 10
WAIT_TIMEOUT = 15


# --- USER INFO ---
USER_INFO = {
    "first_name": "venkata sai gowhith",
    "last_name": "kanisetty",
    "phone_country_code": "+1",
    "phone": "4085908860",
    "email": "gowhithkanisetty@gmail.com",
    "university": "Student at San Jose State University",
    "location": "San Jose, California, United States",
}


PHONE_NUMBER = USER_INFO["phone"]
RESUME_PATH = r"C:\Users\Asus\OneDrive - Vasavi College Of Engineering\Desktop\kali_for_this_time\automation_seliniuem\gowhithresume_main.pdf"


# Function to calculate similarity
def get_match_score(job_text, target_text):
    try:
        embeddings = model.encode([job_text, target_text])
        similarity = util.cos_sim(embeddings[0], embeddings[1])
        return similarity.item() * 100
    except Exception as e:
        print(f"❌ Error calculating similarity: {e}")
        return 0


def setup_driver():
    """Setup Chrome driver with optimized options"""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
   
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def wait_for_element(driver, by, value, timeout=CONFIG['wait_timeout']):
    """Wait for element to be present and return it"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        return None


def wait_for_clickable(driver, by, value, timeout=CONFIG['wait_timeout']):
    """Wait for element to be clickable and return it"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        return element
    except TimeoutException:
        return None


def scroll_to_element(driver, element):
    """Scroll element into view"""
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    sleep(1)


def debug_page_structure(driver):
    """Debug function to inspect LinkedIn page structure"""
    print("🔍 Debugging LinkedIn page structure...")
   
    # Wait for page to load
    sleep(5)
   
    # Try to find job containers with different selectors
    container_selectors = [
        ".job-card-container",
        ".base-search-card",
        "[data-testid='jobsearch-ResultsList__jobCard']",
        ".job-search-card",
        ".search-result-card"
    ]
   
    for selector in container_selectors:
        try:
            containers = driver.find_elements(By.CSS_SELECTOR, selector)
            if containers:
                print(f"✅ Found {len(containers)} job containers with selector: {selector}")
               
                # Inspect first container
                first_container = containers[0]
                print(f"📋 First container HTML structure:")
                print(first_container.get_attribute('outerHTML')[:500] + "...")
               
                # Try to find title elements
                title_elements = first_container.find_elements(By.TAG_NAME, "h3")
                if title_elements:
                    print(f"📝 Found {len(title_elements)} h3 elements")
                    for i, elem in enumerate(title_elements):
                        print(f"   H3[{i}]: {elem.text.strip()}")
               
                # Try to find link elements
                link_elements = first_container.find_elements(By.TAG_NAME, "a")
                if link_elements:
                    print(f"🔗 Found {len(link_elements)} link elements")
                    for i, elem in enumerate(link_elements[:3]):  # Show first 3
                        print(f"   A[{i}]: {elem.text.strip()}")
               
                return selector
            else:
                print(f"❌ No containers found with selector: {selector}")
        except Exception as e:
            print(f"❌ Error with selector {selector}: {e}")
   
    return None


def get_job_details(driver, job_element):
    """Extract job details from job card with improved selectors"""
    try:
        # Get all text content from the job element
        all_text = job_element.text.strip()
        print(f"🔍 Raw job element text: {all_text[:100]}...")
       
        # Try multiple approaches to get title
        title = None
       
        # Approach 1: Look for h3 elements
        try:
            h3_elements = job_element.find_elements(By.TAG_NAME, "h3")
            for h3 in h3_elements:
                text = h3.text.strip()
                if text and len(text) > 3:  # Reasonable title length
                    title = text
                    break
        except:
            pass
        # Approach 2: Look for links with job titles
        if not title:
            try:
                links = job_element.find_elements(By.TAG_NAME, "a")
                for link in links:
                    text = link.text.strip()
                    if text and len(text) > 3 and "apply" not in text.lower():
                        title = text
                        break
            except:
                pass
       
        # Approach 3: Look for any text that might be a title
        if not title:
            try:
                # Split text by lines and look for the most prominent one
                lines = all_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 3 and len(line) < 100:
                        # Skip common non-title text
                        if not any(skip in line.lower() for skip in ['apply', 'save', 'share', 'posted', 'ago']):
                            title = line
                            break
            except:
                pass
       
        if not title:
            title = "Unknown Title"
       
        # Extract company name
        company = "Unknown Company"
        try:
            # Look for company indicators
            company_indicators = ['inc', 'llc', 'corp', 'company', 'ltd', 'group', 'tech', 'systems']
            lines = all_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and line != title:
                    # Check if line contains company indicators
                    if any(indicator in line.lower() for indicator in company_indicators):
                        company = line
                        break
                    # Or if it's a reasonable company name length
                    elif 2 < len(line) < 50 and not any(char.isdigit() for char in line):
                        company = line
                        break
        except:
            pass
       
        # Extract location
        location = "Unknown Location"
        try:
            # Look for location indicators
            location_indicators = ['remote', 'hybrid', 'on-site', 'united states', 'us', 'ca', 'ny', 'tx']
            lines = all_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and line != title and line != company:
                    if any(indicator in line.lower() for indicator in location_indicators):
                        location = line
                        break
                    # Or if it looks like a location (contains comma or common location words)
                    elif ',' in line or any(word in line.lower() for word in ['city', 'state', 'country']):
                        location = line
                        break
        except:
            pass
       
        print(f"📋 Extracted - Title: {title}, Company: {company}, Location: {location}")
       
        return {
            'title': title,
            'company': company,
            'location': location,
            'element': job_element
        }
    except Exception as e:
        print(f"❌ Error extracting job details: {e}")
        return None


def get_job_description(driver):
    """Extract job description from the side panel"""
    try:
        # Wait a bit for the job details to load
        sleep(3)
       
        # Multiple selectors for job description
        desc_selectors = [
            ".jobs-description-content__text",
            ".jobs-description__content",
            ".jobs-box__html-content",
            ".jobs-description",
            "[data-testid='jobsearch-ResultsList__jobDescription']",
            ".jobs-description-content",
            ".jobs-box__html-content",
            ".jobs-description__content__text",
            ".jobs-description__content__text--sticky",
            ".jobs-description__content__text--expandable",
            ".jobs-description__content__text--collapsed",
            ".jobs-description__content__text--expanded"
        ]
       
        for selector in desc_selectors:
            try:
                desc_element = wait_for_element(driver, By.CSS_SELECTOR, selector, timeout=5)
                if desc_element:
                    text = desc_element.text.strip()
                    if text and len(text) > 50:  # Reasonable description length
                        print(f"✅ Found job description with selector: {selector}")
                        return text
            except TimeoutException:
                continue
            except Exception as e:
                print(f"⚠️ Error with selector {selector}: {e}")
                continue
       
        # If no description found, try to get any text content from the main area
        try:
            # Look for any large text blocks that might be the description
            main_content_selectors = [
                "main",
                ".jobs-search__results-list",
                ".jobs-search__results",
                ".jobs-search-results",
                ".jobs-search-results__content"
            ]
           
            for selector in main_content_selectors:
                try:
                    main_element = driver.find_element(By.CSS_SELECTOR, selector)
                    text = main_element.text.strip()
                    if text and len(text) > 100:
                        # Extract the longest text block that might be the description
                        lines = text.split('\n')
                        longest_line = max(lines, key=len)
                        if len(longest_line) > 50:
                            print(f"✅ Found description in main content area")
                            return longest_line
                except:
                    continue
        except:
            pass
       
        print("⚠️ Could not find job description")
        return ""
       
    except Exception as e:
        print(f"❌ Error extracting job description: {e}")
        return ""


def apply_to_job(driver):
    """Attempt to apply to the current job"""
    try:
        # Look for Easy Apply button with multiple selectors
        apply_selectors = [
            "button.jobs-apply-button",
            ".jobs-apply-button",
            "button[aria-label*='Apply']",
            ".jobs-s-apply button",
            "button[data-control-name='jobdetails_topcard_inapply']"
        ]
       
        apply_button = None
        for selector in apply_selectors:
            try:
                apply_button = wait_for_clickable(driver, By.CSS_SELECTOR, selector, timeout=5)
                if apply_button:
                    break
            except TimeoutException:
                continue
       
        if not apply_button:
            print("⚠️ No Easy Apply button found")
            return False
       
        # Scroll to button and click
        scroll_to_element(driver, apply_button)
        sleep(1)
       
        # Check if button is enabled
        if not apply_button.is_enabled():
            print("⚠️ Apply button is disabled")
            return False
       
        apply_button.click()
        print("🎯 Easy Apply button clicked!")
       
        # Wait for application modal/form to appear
        sleep(3)
       
        # Check if we need to fill any forms
        try:
            # Look for common form elements
            form_elements = driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")
            if form_elements:
                print("📝 Application form detected - manual completion required")
                return True
            else:
                print("✅ Application submitted successfully!")
                return True
        except:
            print("✅ Application process initiated")
            return True
           
    except ElementClickInterceptedException:
        print("⚠️ Apply button was intercepted - trying alternative approach")
        try:
            driver.execute_script("arguments[0].click();", apply_button)
            return True
        except:
            return False
    except Exception as e:
        print(f"❌ Error during application: {e}")
        return False


def process_jobs_page(driver, page_num):
    """Process only the top 3 jobs on the current page and robustly apply to each one."""
    print(f"\n📄 Processing page {page_num}...")
   
    # Debug page structure on first page
    if page_num == 1:
        debug_page_structure(driver)
   
    # Try multiple selectors for job containers
    container_selectors = [
        ".job-card-container",
        ".base-search-card",
        "[data-testid='jobsearch-ResultsList__jobCard']",
        ".job-search-card",
        ".search-result-card",
        "li[data-testid='jobsearch-ResultsList__jobCard']"
    ]
   
    job_cards = []
    working_selector = None
   
    for selector in container_selectors:
        try:
            cards = driver.find_elements(By.CSS_SELECTOR, selector)
            if cards:
                job_cards = cards
                working_selector = selector
                print(f"✅ Found {len(cards)} job cards using selector: {selector}")
                break
        except Exception as e:
            print(f"❌ Error with selector {selector}: {e}")
            continue
   
    if not job_cards:
        print("❌ No job cards found with any selector")
        return 0, 0
   
    print(f"Found {len(job_cards)} job listings on page {page_num}")
   
    processed_count = 0
    applied_count = 0
   
    for i, job_card in enumerate(job_cards[:3]):  # Only top 3 jobs
        try:
            # Re-fetch job cards to avoid stale elements
            job_cards = driver.find_elements(By.CSS_SELECTOR, working_selector)
            if i >= len(job_cards):
                break
               
            job_card = job_cards[i]
           
            # Get job details
            job_info = get_job_details(driver, job_card)
            if not job_info:
                continue
               
            print(f"\n🔍 [{i+1}/3] Applying to: {job_info['title']}")
            print(f"   Company: {job_info['company']} | Location: {job_info['location']}")
           
            # Scroll to job card and click
            scroll_to_element(driver, job_card)
            sleep(1)
           
            # Click to open job details
            job_card.click()
            sleep(2)
           
            # Get job description (optional, for logging)
            job_description = get_job_description(driver)
            if len(job_description) > 200:
                print(f"   Job Description Preview: {job_description[:200]}...")
            else:
                print(f"   Job Description: {job_description}")
           
            # Try to find and click Easy Apply
            print(f"✅ Looking for Easy Apply button...")
            easy_apply = None
            easy_apply_selectors = [
                "button.jobs-apply-button",
                ".jobs-apply-button",
                "button[aria-label*='Apply']",
                ".jobs-s-apply button",
                "button[data-control-name='jobdetails_topcard_inapply']"
            ]
            for selector in easy_apply_selectors:
                try:
                    easy_apply = wait_for_clickable(driver, By.CSS_SELECTOR, selector, timeout=5)
                    if easy_apply:
                        print(f"✅ Found Easy Apply button with selector: {selector}")
                        break
                except Exception as e:
                    print(f"⚠️ Error finding Easy Apply with {selector}: {e}")
                    continue
            if not easy_apply:
                print(f"❌ No Easy Apply button found for this job.")
                continue
            # Scroll to and click Easy Apply
            scroll_to_element(driver, easy_apply)
            sleep(1)
            if not easy_apply.is_enabled():
                print("⚠️ Easy Apply button is disabled")
                continue
            try:
                easy_apply.click()
                print("🎯 Clicked Easy Apply button!")
            except Exception as e:
                print(f"❌ Could not click Easy Apply: {e}")
                continue
            # Wait for application modal
            sleep(2)
            modal_found = False
            try:
                modal = wait_for_element(driver, By.CSS_SELECTOR, ".jobs-easy-apply-modal, .artdeco-modal", timeout=5)
                if modal:
                    print("✅ Application modal appeared!")
                    modal_found = True
            except Exception as e:
                print(f"⚠️ Could not detect application modal: {e}")
            if modal_found:
                print(f"✅ Application process started (manual completion may be required).")
                applied_count += 1
            else:
                print(f"⚠️ Application modal not detected. Please check manually.")
            processed_count += 1
            sleep(2)


            # Check if the job is IT-related
            it_keywords = ['software', 'cybersecurity', 'ai', 'machine learning', 'data science', 'developer', 'engineer']
            job_title = job_info['title'].lower()
            job_desc = get_job_description(driver).lower()
            if not any(kw in job_title or kw in job_desc for kw in it_keywords):
                print("❌ Skipping non-IT job:", job_info['title'])
                continue


            # Additional filter for software-related jobs
            if "software" not in job_title and "software" not in job_desc:
                print("❌ Skipping non-software job:", job_info['title'])
                continue
        except Exception as e:
            print(f"❌ Error processing job {i+1}: {e}")
            continue
    return processed_count, applied_count


def search_jobs_with_multiple_terms(driver, search_terms, max_pages_per_term=1):
    """Search jobs using multiple search terms"""
    total_processed = 0
    total_applied = 0
   
    for term_index, search_term in enumerate(search_terms):
        print(f"\n🔍 Searching for: '{search_term}' (Term {term_index + 1}/{len(search_terms)})")
       
        # Construct search URL
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={search_term.replace(' ', '%20')}&location=United%20States"
        driver.get(search_url)
        sleep(5)
       
        # Toggle Easy Apply filter
        toggle_easy_apply_filter(driver)
       
        # Process pages for this search term
        for page in range(1, max_pages_per_term + 1):
            processed, applied = process_jobs_page(driver, page)
            total_processed += processed
            total_applied += applied
           
            # Go to next page if not the last page
            if page < max_pages_per_term:
                try:
                    next_button = wait_for_clickable(driver, By.CSS_SELECTOR, "button[aria-label='Next']")
                    if next_button:
                        next_button.click()
                        sleep(5)
                    else:
                        print("No more pages available for this search term")
                        break
                except:
                    print("Could not navigate to next page for this search term")
                    break
   
    return total_processed, total_applied


def toggle_easy_apply_filter(driver):
    """Toggle the Easy Apply filter on the LinkedIn jobs search page."""
    print("🔘 Attempting to toggle Easy Apply filter...")
    try:
        # Wait for the filter bar to load
        sleep(2)
        # Try multiple selectors for the Easy Apply filter
        filter_selectors = [
            "button[aria-label*='Easy Apply']",  # Most common
            "button[data-control-name*='filter_easy_apply']",
            "label[for*='f_AL']",  # Sometimes a label
            "input[id*='f_AL']",   # Sometimes a checkbox
            "span:contains('Easy Apply')"
        ]
        easy_apply_button = None
        for selector in filter_selectors:
            try:
                easy_apply_button = driver.find_element(By.CSS_SELECTOR, selector)
                if easy_apply_button:
                    print(f"✅ Found Easy Apply filter with selector: {selector}")
                    break
            except Exception:
                continue
        if not easy_apply_button:
            # Try to find by visible text as a fallback
            try:
                all_buttons = driver.find_elements(By.TAG_NAME, "button")
                for btn in all_buttons:
                    if "easy apply" in btn.text.lower():
                        easy_apply_button = btn
                        print(f"✅ Found Easy Apply filter by text.")
                        break
            except Exception:
                pass
        if easy_apply_button:
            try:
                easy_apply_button.click()
                print("🎯 Clicked Easy Apply filter!")
                sleep(2)
            except Exception as e:
                print(f"⚠️ Could not click Easy Apply filter: {e}")
        else:
            print("❌ Could not find Easy Apply filter on the page.")
    except Exception as e:
        print(f"❌ Error toggling Easy Apply filter: {e}")


def wait_for_login(driver):
    print("⚠️ Please log in to LinkedIn manually within 30 seconds...")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "global-nav-search"))
    )
    print("✅ Login detected!")


def search_jobs(driver):
    # Only search for Software Internships with Easy Apply, Past Week, Internship/Co-op
    print(f"🔍 Searching for 'Software Internship' jobs in {LOCATION} (Past week, Internship/Co-op, Easy Apply)...")
    search_url = (
        f"https://www.linkedin.com/jobs/search/?"
        f"keywords=Software%20Internship"
        f"&location={LOCATION.replace(' ', '%20')}"
        f"&f_TPR=r604800"      # Past week
        f"&f_E=1%2C2"          # Internship, Entry level
        f"&f_JT=I%2CC"         # Internship, Co-op
        f"&f_AL=true"          # Easy Apply filter
    )
    driver.get(search_url)
    sleep(3)


def print_manual_fields_checklist():
    print("\n📝 Before submitting, be prepared to fill in (if prompted):")
    print("  - Phone Number (if not in your profile)")
    print("  - Resume upload (sometimes required again)")
    print("  - Screening questions (work authorization, experience, etc.)")
    print("  - Cover letter (optional or required)")
    print("  - Work authorization/visa status")
    print("  - Willingness to relocate/current location")
    print("  - Years of experience in specific skills")
    print("  - Education details")
    print("  - Portfolio/website links (optional)")
    print("  - Custom employer questions (e.g., 'Why do you want this internship?')\n")


def autofill_easy_apply(driver):
    # Helper to fill a field by label, placeholder, or name
    def fill_field(possible_labels, value):
        try:
            # Try by label text
            for label_text in possible_labels:
                labels = driver.find_elements(By.XPATH, f"//label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label_text.lower()}')]")
                for label in labels:
                    # Find associated input
                    input_id = label.get_attribute('for')
                    if input_id:
                        input_elem = driver.find_element(By.ID, input_id)
                        input_elem.clear()
                        input_elem.send_keys(value)
                        print(f"  - Autofilled {label_text} by label.")
                        return True
            # Try by placeholder
            for label_text in possible_labels:
                inputs = driver.find_elements(By.XPATH, f"//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label_text.lower()}')]")
                for input_elem in inputs:
                    input_elem.clear()
                    input_elem.send_keys(value)
                    print(f"  - Autofilled {label_text} by placeholder.")
                    return True
            # Try by name
            for label_text in possible_labels:
                inputs = driver.find_elements(By.XPATH, f"//input[contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label_text.lower()}')]")
                for input_elem in inputs:
                    input_elem.clear()
                    input_elem.send_keys(value)
                    print(f"  - Autofilled {label_text} by name.")
                    return True
        except Exception:
            pass
        return False


    # First Name
    fill_field(["first name", "firstname", "given name"], USER_INFO["first_name"])
    # Last Name
    fill_field(["last name", "lastname", "surname", "family name"], USER_INFO["last_name"])
    # Phone Country Code
    fill_field(["country code", "phone country", "country"], USER_INFO["phone_country_code"])
    # Phone
    fill_field(["phone", "mobile", "phone number", "mobile phone"], USER_INFO["phone"])
    # Email
    fill_field(["email", "email address"], USER_INFO["email"])
    # University/Current Position
    fill_field(["university", "school", "current position", "education", "student at"], USER_INFO["university"])
    # Location
    fill_field(["location", "city", "current location"], USER_INFO["location"])


    # Try to upload resume if upload field is present
    try:
        upload_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
        for upload_input in upload_inputs:
            upload_input.send_keys(RESUME_PATH)
            print("  - Uploaded resume.")
    except Exception:
        pass
    # Print any additional questions
    try:
        questions = driver.find_elements(By.CSS_SELECTOR, ".jobs-easy-apply-form-section__grouping label")
        if questions:
            print("  - Additional questions detected:")
            for q in questions:
                print(f"    * {q.text.strip()}")
    except Exception:
        pass


def close_all_modals(driver):
    # Try to close any open modal overlays or popups
    try:
        # Try Dismiss/Close/Discard/Cancel buttons
        for label in ['Dismiss', 'Close', 'Discard', 'Cancel']:
            try:
                btn = driver.find_element(By.XPATH, f"//button[contains(@aria-label, '{label}') or contains(text(), '{label}')]")
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    print(f"  - Closed modal with '{label}' button.")
                    sleep(1)
            except Exception:
                continue
        # Try clicking overlay itself if present
        overlays = driver.find_elements(By.CSS_SELECTOR, ".artdeco-modal-overlay, .artdeco-modal__actionbar")
        for overlay in overlays:
            try:
                if overlay.is_displayed():
                    overlay.click()
                    print("  - Clicked overlay to close modal.")
                    sleep(1)
            except Exception:
                continue
    except Exception:
        pass


def apply_to_top_jobs(driver, max_jobs=3):
    print(f"🚀 Attempting to apply to the top {max_jobs} jobs...")
    jobs_applied = 0
    for idx in range(max_jobs):
        close_all_modals(driver)  # Ensure all modals are closed before next job
        try:
            # Always re-fetch the job cards to avoid stale element reference
            job_cards = WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".job-card-container, .base-card"))
            )
            if idx >= len(job_cards):
                print(f"No more job cards available (found {len(job_cards)}).")
                break
            job_card = job_cards[idx]
            print(f"\n➡️ [{idx+1}] Opening job card...")
            driver.execute_script("arguments[0].scrollIntoView();", job_card)
            job_card.click()
            # Wait for job details pane to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-details__main-content, .jobs-search__job-details--container"))
                )
            except TimeoutException:
                print("❌ Job details pane did not load.")
                continue
            sleep(2)
            # Now look for Easy Apply button in the job details pane
            easy_apply_btn = None
            try:
                easy_apply_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'jobs-apply-button') and not(@disabled)]"))
                )
            except TimeoutException:
                print("❌ No Easy Apply button for this job in the details pane.")
                continue
            if easy_apply_btn:
                try:
                    easy_apply_btn.click()
                    # Wait for modal to appear
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "jobs-easy-apply-modal"))
                    )
                    print("✅ Clicked Easy Apply and modal opened!")
                    autofill_easy_apply(driver)
                    print_manual_fields_checklist()
                    jobs_applied += 1


                    # --- FULLY AUTOMATE MULTI-STEP APPLICATION ---
                    while True:
                        next_btn = None
                        for btn_text in ['Submit application', 'Submit', 'Next', 'Review', 'Continue']:
                            try:
                                next_btn = driver.find_element(
                                    By.XPATH,
                                    f"//button[not(@disabled) and (contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{btn_text.lower()}') or contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{btn_text.lower()}'))]"
                                )
                                if next_btn.is_displayed() and next_btn.is_enabled():
                                    break
                            except Exception:
                                continue
                        if next_btn and next_btn.is_displayed() and next_btn.is_enabled():
                            next_btn.click()
                            print(f"  - Clicked '{next_btn.text.strip()}' button.")
                            sleep(2)
                            autofill_easy_apply(driver)  # Try to autofill again in case new fields appear
                            continue
                        break  # No more next/review/submit buttons


                    # Wait for modal to close or confirmation to appear
                    try:
                        WebDriverWait(driver, 10).until_not(
                            EC.presence_of_element_located((By.CLASS_NAME, "jobs-easy-apply-modal"))
                        )
                        print("  - Application modal closed.")
                    except TimeoutException:
                        # Try to close modal if still open
                        try:
                            close_btn = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Dismiss') or contains(@aria-label, 'Close')]")
                            close_btn.click()
                            print("  - Clicked Dismiss/Close to close modal.")
                            sleep(1)
                        except Exception:
                            print("  - Could not close modal, moving to next job.")
                    close_all_modals(driver)  # Extra cleanup
                except Exception as e:
                    print(f"❌ Could not click Easy Apply or modal did not open: {e}")
            else:
                print("❌ No Easy Apply button found in the job details pane.")
        except Exception as e:
            print(f"❌ Error processing job {idx+1}: {e}")
    print(f"\n✅ Applied (or started application) for {jobs_applied} jobs.")


def main():
    """Main function to run the LinkedIn job application automation"""
    driver = None
    try:
        # Setup driver
        driver = setup_driver()
       
        # Open LinkedIn and login manually
        driver.get("https://www.linkedin.com/login")
        wait_for_login(driver)
       
        # Search for jobs
        search_jobs(driver)
       
        # Apply to top jobs
        apply_to_top_jobs(driver, MAX_JOBS_TO_APPLY)
       
        print("\n🎉 Done! Closing browser.")
       
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()



