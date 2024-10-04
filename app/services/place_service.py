import requests
import re

def get_body(url):
    res = requests.get(url)
    content = res.content.decode('utf-8')

    pattern = r'<body>(.*?)</body>'
    match = re.search(pattern, content, re.DOTALL)
    
    return match.group(0)


def content_scrap(to_scrap: str, pattern: str, group_number: int = 0):
    content_match = re.search(pattern, to_scrap)

    if content_match is None:
        return None

    return content_match.group(group_number)

def scrap_all_content(to_scrap: str, pattern: str):
    return re.findall(pattern, to_scrap)