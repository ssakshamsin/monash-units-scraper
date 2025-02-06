import requests
import json
import time

def fetch_and_extract_units(total_results, size=100):
    units = []  # List to hold unit details (name, code, url)
    
    for start in range(0, total_results, size):
        url = f"https://api-ap-southeast-2.prod.courseloop.com/publisher/search-all?from={start}&query=&searchType=advanced&siteId=monash-prod-pres&siteYear=current&size={size}"

        # Send GET request to fetch data from the API
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("data", {}).get("results", [])
            
            # Extract unit details (name, code, URL)
            for unit in results:
                unit_details = {
                    "name": unit.get("title"),
                    "code": unit.get("code"),
                    "url": f"https://handbook.monash.edu{unit.get('uri')}"  # Construct full URL
                }
                units.append(unit_details)
                
            print(f"Fetched {len(results)} units from {start} to {start + size - 1}")
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
        #time.sleep(10)

    return units

def save_units_to_json(units, filename="monash_units.json"):
    # Save extracted units to a JSON file
    with open(filename, 'w') as f:
        json.dump(units, f, indent=4)
    print(f"Saved {len(units)} units to {filename}")

# Set the total number of units to be fetched
total_results = 6076  # Replace with the total number of units for the year
units = fetch_and_extract_units(total_results)

# Save extracted units to a JSON file
save_units_to_json(units)





from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import re

with open("monash_units.json", "r") as f:
    units = json.load(f)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def clean_html(text):
    return re.sub(r"<.*?>", "", text) if text else text

def extract_assessments(page_content):
    assessments = page_content.get("assessments", [])
    if assessments:
        formatted_assessments = []
        for a in assessments:
            number = a.get("number", "N/A")
            name = a.get("assessment_name", "Unnamed Assessment")
            weight = a.get("weight", "0")
            formatted_assessments.append(f"{name}({weight}%)")
        
        return "; ".join(formatted_assessments)
    
    elif page_content.get("handbook_assessment_summary"):
        return clean_html(page_content["handbook_assessment_summary"])
    
    return "No assessment data available"
    
    formatted_assessments = []
    for a in assessments:
        number = a.get("number", "N/A")
        name = a.get("assessment_name", "Unnamed Assessment")
        weight = a.get("weight", "0")
        formatted_assessments.append(f"{name}({weight}%)")
    
    return "; ".join(formatted_assessments)

extracted_data = []

for unit in units:
    unit_code = unit["code"]
    unit_url = unit["url"]
    time.sleep(1)
    try:
        driver.get(unit_url)
        time.sleep(2)  # Allow JavaScript to load

        script_element = driver.find_element(By.ID, "__NEXT_DATA__")
        json_data = json.loads(script_element.get_attribute("innerHTML"))
        page_content = json_data["props"]["pageProps"]["pageContent"]

        unit_info = {
            "code": clean_html(page_content.get("unit_code", "")),
            "name": clean_html(page_content.get("title", "")),
            "faculty": clean_html(page_content.get("school", {}).get("value", "")),
            "credit_points": clean_html(page_content.get("credit_points", "")),
            "assessment_summary": extract_assessments(page_content),
            "url": unit_url
        }
        
        extracted_data.append(unit_info)
        print(f"Extracted: {unit_code}, {len(extracted_data)}")

        if len(extracted_data)==10:
            break
    except Exception as e:
        print(f"ERROR PROCESSING{unit_code}: {e}\n")
        continue

# Save extracted data to a new JSON file
with open("monash_units_extracted.json", "w") as f:
    json.dump(extracted_data, f, indent=4)

print("Extraction complete. Data saved to monash_units_extracted.json")
driver.quit()
