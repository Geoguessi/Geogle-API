import requests
import re
import html
from fastapi import HTTPException
from app.models.dashboard import Dashboard, SectionDivider


def get_body(url):
    try:
        res = requests.get(url)
        res.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching URL: {str(e)}")

    content = res.content.decode('utf-8')

    pattern = r'<body>(.*?)</body>'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        raise HTTPException(status_code=404, detail="Body content not found")

    return match.group(1)


def get_recommend_detail(text: str, *args, **kwargs):
    a_pattern = r'<a[^>]*>([\s\S]*?)<\/noscript>'
    link_pattern = r'<a[^>]*href="(\/[^"]*?)"'
    title_pattern = r'<a[^>]*title="([^"]*?)"'

    a_match = re.search(a_pattern, text)

    if a_match is not None:
        a_tag = a_match.group()

        link = 'https://www.tripniceday.com' + re.search(link_pattern, a_tag).group(1)
        title = re.search(title_pattern, a_tag).group(1)

        image_pattern = r'<noscript>.*?<img[^>]*src="([^"]*)"[^>]*>'
        image = re.search(image_pattern, a_tag)
        imgSrc = html.unescape(f'https://www.tripniceday.com{image.group(1)}')

        return title, imgSrc, link

    return None, None, None


def get_foodie_detail(text: str, *args, **kwargs):
    detail_container_pattern = r'<div class="Province_caption[^"]*"[^"]*>([\s\S]*?)<\/div>'
    link_pattern = r'<a[^>]*href="(\/[^"]*?)"'
    title_pattern = r'<a[^>]*title="([^"]*?)"'
    image_pattern = r'<noscript>.*?<img[^>]*src="([^"]*)"[^>]*>'
    

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
    image_pattern = r'<noscript>.*?<img[^>]*src="([^"]*)"[^>]*>'

    province = kwargs.get('province', None)

    a_match = re.search(a_pattern, text)

    if province is not None:
        link = f'https://www.tripniceday.com/province/{province}'
    else:
        link = 'https://www.tripniceday.com/'

    if a_match is not None:
        a_tag = a_match.group(1)

        title = re.search(title_pattern, a_tag).group(1)

        image = re.search(image_pattern, text)
        imgSrc = html.unescape(f'https://www.tripniceday.com{image.group(1)}')

        return title, imgSrc, link

    return None, None, None


def get_attration_list_detail(text: str, *args, **kwargs):
    title = link = imgSrc = None

    image_pattern = r'<noscript>.*?<img[^>]*src="([^"]*)"[^>]*>'
    title_pattern = r'<div class="cursor-div" title="([^"]*?)"'

    province = kwargs.get('province', None)
    image_match = re.search(image_pattern, text)
    title_match = re.search(title_pattern, text)

    if image_match and title_match:
        if province is not None:
            link = f'https://www.tripniceday.com/province/{province}'
        else:
            link = 'https://www.tripniceday.com/'

        imgSrc = html.unescape(f'https://www.tripniceday.com{image_match.group(1)}')
        title = title_match.group(1)

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
        }
        dashboard.append(pd)

    return dashboard


def scrap_province_page(province_path):
    province_url = 'https://www.tripniceday.com/province'

    try:
        body = get_body(f'{province_url}/{province_path}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching province page: {str(e)}")

    if not body:
        raise HTTPException(status_code=404, detail=f"Province {province_path} not found")

    ProvinceDashboard = {
        Dashboard.RECOMMENDATION: None,
        Dashboard.FOODIE: None,
        Dashboard.ATTRACTION: None
    }

    try:
        ProvinceDashboard[Dashboard.RECOMMENDATION] = get_province_detail(body, SectionDivider.recommendation_pattern, get_recommend_detail)
        ProvinceDashboard[Dashboard.FOODIE] = get_province_detail(body, SectionDivider.foodie_pattern, get_foodie_detail)
        ProvinceDashboard[Dashboard.ATTRACTION] = get_province_detail(body, SectionDivider.MAIN_ATTRACTION, get_main_attraction_detail, province_path)
        ProvinceDashboard[Dashboard.ATTRACTION].extend(get_province_detail(body, SectionDivider.ATTRACTION_LIST, get_attration_list_detail, province_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing province details: {str(e)}")

    return ProvinceDashboard


AllProvinceDashboard = {}


def scrap_all_province_page(province_path):
    province_url = 'https://www.tripniceday.com/province'

    try:
        body = get_body(f'{province_url}/{province_path}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching province page: {str(e)}")

    if not body:
        raise HTTPException(status_code=404, detail=f"Province {province_path} not found")

    AllProvinceDashboard[province_path] = {
        Dashboard.RECOMMENDATION: None,
        Dashboard.FOODIE: None,
        Dashboard.ATTRACTION: None
    }

    try:
        AllProvinceDashboard[province_path][Dashboard.RECOMMENDATION] = get_province_detail(body, SectionDivider.recommendation_pattern, get_recommend_detail)
        AllProvinceDashboard[province_path][Dashboard.FOODIE] = get_province_detail(body, SectionDivider.foodie_pattern, get_foodie_detail)
        AllProvinceDashboard[province_path][Dashboard.ATTRACTION] = get_province_detail(body, SectionDivider.MAIN_ATTRACTION, get_main_attraction_detail, province_path)
        AllProvinceDashboard[province_path][Dashboard.ATTRACTION].extend(get_province_detail(body, SectionDivider.ATTRACTION_LIST, get_attration_list_detail, province_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing province details: {str(e)}")
