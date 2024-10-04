from fastapi import FastAPI
import requests
import re
from bs4 import BeautifulSoup as bs
import html, json
import threading
import uuid
import pandas as pd
from http_exceptions import HTTPException
from fastapi.responses import StreamingResponse
import io

app = FastAPI()


@app.get("/")
def index():
    url = 'https://www.tripniceday.com/en/country/th'

    res = requests.get(url)
    content = res.content.decode('utf-8')

    pattern = r'<body>(.*?)</body>'
    match = re.search(pattern, content, re.DOTALL)

    body = match.group(1)
    # beauty_html = bs(body, 'html.parser').prettify()
    # <li class="province-item"><a href="#" title="Kanchanaburi">Kanchanaburi</a></li>
    a_link_re = r'<a[^>]*href="([^"]*)"[^>]*title="([^"]*)"[^>]*>([^<]+)</a>'
    li_re = f'<li class="province-item">.*?{a_link_re}.*?</li>'

    province_pattern = re.compile(li_re)
    provinces = []

    for province in province_pattern.findall(body):
        provinces.append(province[2]) 

    province_url = 'https://www.tripniceday.com/province'
    links = []

    for province in provinces:
        province_path = province.replace(' ', '-').lower()
        links.append(f'{province_url}/{province_path}')

    return { "provinces": provinces ,"links": links}



# ProvinceDashboard 
    
class SectionDivider:
    nest_div_pattern = r'<div.*?>.*?<\/div>.*?'

    recommendation_pattern: str = r'<div class="place-card-item Province_recommended-item[^"]*"[^"]*>(.*?)<\/div>'
    foodie_pattern: str = fr'<div class="Province_foodie-image[^"]*"[^"]*>(.*?{nest_div_pattern*2})<\/div>'
    MAIN_ATTRACTION: str = fr'<div class="Province_main-attraction-block[^"]*"[^"]*>(.*?{nest_div_pattern*4})<\/div>'
    ATTRACTION_LIST: str = fr'<div class="col-md-6 col-lg-4"><div class="place-card-item full-width">(.*?)<\/div><\/div>'

class Dashboard:
    RECOMMENDATION = 'recommendation'
    FOODIE = 'foodie'
    ATTRACTION = 'attraction'

def get_body(url):
    res = requests.get(url)
    content = res.content.decode('utf-8')

    pattern = r'<body>(.*?)</body>'
    match = re.search(pattern, content, re.DOTALL)
    
    return match.group(1)

ProvinceDashboard = {}
main_page_body = get_body(url = 'https://www.tripniceday.com/en/country/th')
link_pattern = r'<a[^>]*href="(\/[^"]*?)"'
title_pattern = r'<a[^>]*title="([^"]*?)"'
image_pattern = fr'<noscript>.*?<img[^>]*src="([^"]*)"[^>]*>'

def get_recommend_detail(text: str, *args, **kwargs):
    a_pattern = r'<a[^>]*>([\s\S]*?)<\/noscript>'
    link_pattern = r'<a[^>]*href="(\/[^"]*?)"'
    title_pattern = r'<a[^>]*title="([^"]*?)"'
    
    a_match = re.search(a_pattern, text)
    
    if a_match is not None:
        a_tag = a_match.group()

        link = 'https://www.tripniceday.com' + re.search(link_pattern, a_tag).group(1)
        title = re.search(title_pattern, a_tag).group(1)

        image_pattern = fr'<noscript>.*?<img[^>]*src="([^"]*)"[^>]*>'
        image = re.search(image_pattern, a_tag)
        imgSrc = html.unescape(f'https://www.tripniceday.com{image.group(1)}')
        return title, imgSrc, link

    return None, None, None

def get_foodie_detail(text: str, *args, **kwargs):
    detail_container_pattern = r'<div class="Province_caption[^"]*"[^"]*>([\s\S]*?)<\/div>'
    link_pattern = r'<a[^>]*href="(\/[^"]*?)"'
    title_pattern = r'<a[^>]*title="([^"]*?)"'
    image_pattern = fr'<noscript>.*?<img[^>]*src="([^"]*)"[^>]*>'
    
    detail_container_match = re.search(detail_container_pattern, text)
    
    if detail_container_match is not None:
        detail_container_tag = detail_container_match.group()

        link = 'https://www.tripniceday.com' + re.search(link_pattern, detail_container_tag).group(1)
        title = re.search(title_pattern, detail_container_tag).group(1)

        image = re.search(image_pattern, text)
        imgSrc = html.unescape(f'https://www.tripniceday.com{image.group(1)}')

        return title, imgSrc, link

    return None, None, None

def get_main_attraction_detail(text: str, *args, **kwargs):
    a_pattern = r'<div class="Province_action[^"]*"[^"]*>([\s\S]*?)<\/div>'
    title_pattern = r'<a[^>]*title="([^"]*?)"'
    image_pattern = fr'<noscript>.*?<img[^>]*src="([^"]*)"[^>]*>'

    province = kwargs.get('province', None)
    
    a_match = re.search(a_pattern, text)

    if (province is not None):
        link = f'https://www.tripniceday.com/province/{province}'
    else:
        link = f'https://www.tripniceday.com/'
    
    if a_match is not None:
        a_tag = a_match.group(1)

        title = re.search(title_pattern, a_tag).group(1)

        image = re.search(image_pattern, text)
        imgSrc = html.unescape(f'https://www.tripniceday.com{image.group(1)}')

        return title, imgSrc, link

    return None, None, None

def get_attration_list_detail(text: str, *args, **kwargs):
    title = link = imgSrc = None

    image_pattern = fr'<noscript>.*?<img[^>]*src="([^"]*)"[^>]*>'
    title_pattern = r'<div class="cursor-div" title="([^"]*?)"'

    province = kwargs.get('province', None)
    image_match = re.search(image_pattern, text)
    title_macth = re.search(title_pattern, text)

    if (image_match and title_macth):
        if (province is not None):
            link = f'https://www.tripniceday.com/province/{province}'
        else:
            link = f'https://www.tripniceday.com/'

        imgSrc = html.unescape(f'https://www.tripniceday.com{image_match.group(1)}')
        
        title = title_macth.group(1)

    return title, imgSrc, link

def get_province_detail(body: str, pattern: str, detail_getter, province: str = None):
    dashboard = []
    match = re.findall(pattern, body, re.DOTALL)
    
    for m in match:
        title, image, link = detail_getter(m, province=province)
        pd = {
            'title': title, 
            'link': link,
            'image': image,
            'id': str(uuid.uuid4())
        }
        dashboard.append(pd)

    return dashboard

def scrap_province_page(province_path):
    province_url = 'https://www.tripniceday.com/province'
    body = get_body(f'{province_url}/{province_path}')

    ProvinceDashboard[province_path] = {
        Dashboard.RECOMMENDATION: None,
        Dashboard.FOODIE: None,
        Dashboard.ATTRACTION: None
    }

    ProvinceDashboard[province_path][Dashboard.RECOMMENDATION] = get_province_detail(body, SectionDivider.recommendation_pattern, get_recommend_detail)
    ProvinceDashboard[province_path][Dashboard.FOODIE] = get_province_detail(body, SectionDivider.foodie_pattern, get_foodie_detail)
    ProvinceDashboard[province_path][Dashboard.ATTRACTION] = get_province_detail(body, SectionDivider.MAIN_ATTRACTION, get_main_attraction_detail, province_path)
    ProvinceDashboard[province_path][Dashboard.ATTRACTION].extend(get_province_detail(body, SectionDivider.ATTRACTION_LIST, get_attration_list_detail, province_path))




# <li class="province-item"><a href="#" title="Kanchanaburi">Kanchanaburi</a></li>
a_link_re = r'<a[^>]*href="([^"]*)"[^>]*title="([^"]*)"[^>]*>([^<]+)</a>'
li_re = f'<li class="province-item">.*?{a_link_re}.*?</li>'

province_pattern = re.compile(li_re)
provinces = []

for province in province_pattern.findall(main_page_body):
    provinces.append(province[2]) 
    
processes = []

for province in provinces:
    province_path = province.replace(' ', '-').lower()

    process = threading.Thread(target=scrap_province_page, args=(province_path, ))
    process.start() 

    processes.append(process)

for p in processes:
    p.join()

@app.get("/search/{province_name:str}")
def search(province_name:str):
    province_data = ProvinceDashboard.get(province_name.lower().replace(' ', '-'), None)
    if not province_data:
        return {"error": "Province not found"}

    # # Iterate over each section ('recommend', 'foodie', 'attraction') and add 'id' to each item
    # for key in ['recommendation', 'foodie', 'attraction']:
    #     if key in province_data:
    #         # Add 'id' to each item in the list using uuid
    #         for item in province_data[key]:
    #             item['id'] = str(uuid.uuid4())  # Generate a unique UUID and convert it to a string

    return province_data
@app.get("/all")
def all():
    return ProvinceDashboard

@app.get("/csv")
def csv():
    flat_data = []
    for province, categories in ProvinceDashboard.items():
        for category, items in categories.items():
            for item in items:
                flat_data.append({
                    "province": province,
                    "category": category,
                    "title": item["title"],
                    "link": item["link"],
                    "image": item["image"],
                    "id": item["id"]
                })

    
    df = pd.DataFrame(flat_data)
    
    # df.to_csv("province_data.csv", index=False)
    
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)  

    return StreamingResponse(csv_buffer, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=province_data.csv"})
    


# ดึงข้อมูลสถานที่จาก id

def get_body(url):
    res = requests.get(url)
    content = res.content.decode('utf-8')

    pattern = r'<body>(.*?)</body>'
    match = re.search(pattern, content, re.DOTALL)
    
    return match.group(0)

@app.get("/place/{item_id}")
def get_data(item_id: str):
    # Flatten the dictionary and search for the link by id
    for province, categories in ProvinceDashboard.items():
        for category, items in categories.items():
            for item in items:
                if item["id"] == item_id:
                    link = item["link"]
    
    # If the id was not found, raise a 404 error
    raise HTTPException(status_code=404, detail="Item not found")


