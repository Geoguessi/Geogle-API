from fastapi import APIRouter, HTTPException
import requests
import re
import html
import json

from app.services.place_service import get_body, content_scrap, scrap_all_content

router = APIRouter()

@router.get("/place/{place_name}")
def place(place_name: str):
    place_data = {}
    link = f'https://www.tripniceday.com/place/{place_name}'
    place_data['link'] = link
    body = get_body(link)
    place_content_pattern = r'<article class="place-content-wrapper">([\s\S]*?)<\/article>'
    place_content_match = re.search(place_content_pattern, body)
    place_content = place_content_match.group(1)
    # name scrap
    name_pattern = r'<h1 class="Place_place-name[^"]*"[^>]*>([\s\S]*?)<\/h1>'
    place_data["name"] = content_scrap(place_content, name_pattern, 1)
    
    # address scrap
    address_pattern = r'<div class="Place_place-address[^"]*"[^>]*>([\s\S]*?)<\/div>'
    address = content_scrap(place_content, address_pattern, 1)
    address_text_pattern = r'<\/i>(.*?)<\/p>'
    place_data["address"] = content_scrap(address, address_text_pattern, 1)
    
    # description scrap
    description_pattern = r'<div class="entry-content content-with-lines[^"]*"[^>]*><p>([\s\S]*?)<\/p>'
    place_data['description'] = content_scrap(place_content, description_pattern, 1)
    
    # tags scrap
    tags_container_pattern = r'<div class="tags-wrapper[^"]*"[^>]*>([\s\S]*?)<\/div>'
    tags_container = content_scrap(place_content, tags_container_pattern, 1)

    tags_list = []
    if tags_container is not None:
        tag_list_pattern = r'<li>([\s\S]*?)<\/li>'
        tag_list = scrap_all_content(tags_container, tag_list_pattern)

        inner_list_a = r'<a[^>]*>([\s\S]*?)<\/a>'
        for li in tag_list:
            tags_list.append(content_scrap(li, inner_list_a, 1))
    place_data['tags'] = tags_list
    
    #image scrap
    image_container_pattern = r'<div class="Place_place-main-image[^"]*"[^>]*>([\s\S]*?)<\/div>'
    image_container = content_scrap(place_content, image_container_pattern, 1)

    if (image_container is not None):
        image_pattern = r'<noscript>.*?<img[^>]*src="([^"]*)"[^>]*>'
        image = content_scrap(image_container, image_pattern, 1)
        imgSrc = html.unescape(f'https://www.tripniceday.com{image}')
        place_data['image'] = imgSrc
    else:
        place_data['image'] = None
    return place_data