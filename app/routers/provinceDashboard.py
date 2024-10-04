from fastapi import APIRouter, HTTPException
import requests
import threading
import re
from app.services.provinceDashboard_service import get_body, scrap_province_page ,scrap_all_province_page, AllProvinceDashboard
import pandas as pd
from fastapi.responses import StreamingResponse
from app.services.province_service import get_provinces
import io

router = APIRouter()


@router.get("/province/{province_name}")
def dashboard(province_name: str):
    
    main_page_body = get_body(url = 'https://www.tripniceday.com/en/country/th')
    link_pattern = r'<a[^>]*href="(\/[^"]*?)"'
    title_pattern = r'<a[^>]*title="([^"]*?)"'
    image_pattern = fr'<noscript>.*?<img[^>]*src="([^"]*)"[^>]*>'
    
    # <li class="province-item"><a href="#" title="Kanchanaburi">Kanchanaburi</a></li>
    a_link_re = r'<a[^>]*href="([^"]*)"[^>]*title="([^"]*)"[^>]*>([^<]+)</a>'
    li_re = f'<li class="province-item">.*?{a_link_re}.*?</li>'

    province_pattern = re.compile(li_re)
    provinces = []

    for province in province_pattern.findall(main_page_body):
        provinces.append(province[2]) 
        
    
    province_path = province_name.replace(' ', '-').lower()
    
    dashboard = scrap_province_page(province_path)

    return dashboard

@router.get("/provinces/csv")
def csv():
    processes = []
    provinces = get_provinces()
    for province in provinces:
        province_path = province.replace(' ', '-').lower()

        process = threading.Thread(target=scrap_all_province_page, args=(province_path, ))
        process.start() 
        
        processes.append(process)

    for p in processes:
        p.join()
    
    flat_data = []
    for province, categories in AllProvinceDashboard.items():
        for category, items in categories.items():
            for item in items:
                flat_data.append({
                    "province": province,
                    "category": category,
                    "title": item["title"],
                    "link": item["link"],
                    "image": item["image"],
                })

    
    df = pd.DataFrame(flat_data)
    
    # df.to_csv("province_data.csv", index=False)
    
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)  

    return StreamingResponse(csv_buffer, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=province_data.csv"})