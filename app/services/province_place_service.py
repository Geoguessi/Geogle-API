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
import logging

def get_body(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")

    driver = None
    try:    
        remote_url = 'http://selenium:4444/wd/hub'
        driver = webdriver.Remote(command_executor=remote_url, options=chrome_options)
        driver.get(url)
        logging.info(f"Navigated to {url} with title: {driver.title}")

        # Wait for page load
        delay = 2 * 60  # seconds
        try:
            WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.TAG_NAME, 'body')))
            logging.info("Page loaded successfully.")
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