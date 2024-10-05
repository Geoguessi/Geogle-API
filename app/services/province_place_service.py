from fastapi import APIRouter, HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options  
import re
import time

import re
import time

def get_body(url):
    chrome_options = Options()
    chrome_optionsadd_argument("--headless")
    chrome_optionsadd_argument("--no-sandbox")
    chrome_optionsadd_argument("--disable-dev-shm-usage")
    chrome_optionsadd_argument("--disable-browser-side-navigation")
    chrome_optionsadd_argument("--disable-gpu")
    chrome_optionsadd_argument("--window-size=1920,1080")
    chrome_optionsadd_argument("start-maximized")
    chrome_optionsadd_argument("enable-automation")

    

    driver = None
    try:    
        service = ChromeService("/usr/local/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        print(driver.title)

        
        # Wait for page load
        delay = 1 * 60  # seconds
        try:
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'footer')))
            time.sleep(3)  
        except TimeoutException:
            raise HTTPException(status_code=408, detail="Page did not load in time.")
        except WebDriverException as e:
            raise HTTPException(status_code=500, detail=f"WebDriverException: {str(e)}")

        content = driver.page_source
        
        pattern = r'<body[^>]*>(.*?)</body>'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(1)
        else:
            raise HTTPException(status_code=404, detail="Body content not found.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
    finally:
        if driver:
            driver.quit()

def get_container(text):
    container_pattern = r'<section class="Province_province-places-block[^"]*"[^>]*>([\s\S]*?)<\/section>'
    container_match = re.search(container_pattern, text)
    return container_match.group(1)

def get_place_href(url, href_res):
    page_body = get_body(url)
    container = get_container(page_body)
    
    href_pattern = r'<div class="place-card-wrapper"><a[^>]*href="(.*?)"[^>]*>'
    
    base_url = 'https://www.tripniceday.com'
    for href in re.findall(href_pattern, container):
        href_res.append(href) # I remove base_url because peqch tell me to remove it