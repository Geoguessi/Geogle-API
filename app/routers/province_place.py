from fastapi import APIRouter, HTTPException
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from app.services.province_place_service import get_body, get_container, get_place_href
import re
import time
import threading

router = APIRouter()

@router.get("/province/{province}/places")
def province_places(province: str):
    first_page = get_body(f'https://www.tripniceday.com/province/{province}/places?page=1')
    container = get_container(first_page)
    place_amount_pattern = r'<p class="Province_count-text[^"]*"[^>]*>([\s\S]*?)<strong>([\s\S]*?)<\/strong>([\s\S]*?)<\/p>'
    place_amount_match = re.search(place_amount_pattern, container)
    place_amount = int(place_amount_match.group(2).replace(',', ''))
    max_page = min(10, place_amount//20 + int(place_amount%20 != 0))
    processes = []
    href_res = []

    for i in range(1, max_page + 1):
        url = f'https://www.tripniceday.com/province/{province}/places?page={i}'
        
        p = threading.Thread(target=get_place_href, args=(url, href_res))
        processes.append(p)
        p.start() 

    for p in processes:
        p.join()
    
    return {"href_res": href_res}