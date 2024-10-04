from fastapi import APIRouter, HTTPException
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import re
import time

def get_body(url):
    driver = webdriver.ChromiumEdge()

    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    #waiting for page load
    delay = 1 * 60 # seconds
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'footer')))
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    except TimeoutException:
        driver.close()
        return ""


    content = driver.page_source
    driver.close()
    
    pattern = r'<body[^>]*>(.*?)</body>'
    match = re.search(pattern, content, re.DOTALL)

    
    return match.group(1)

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