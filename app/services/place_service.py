import requests
import re
from fastapi import HTTPException

def get_body(url):
    try:
        res = requests.get(url)
        res.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        content = res.content.decode('utf-8')

        pattern = r'<body>(.*?)</body>'
        match = re.search(pattern, content, re.DOTALL)

        if match:
            return match.group(1)  # Return the first capturing group (body content)
        else:
            raise HTTPException(status_code=404, detail="Body content not found.")

    except requests.HTTPError as http_err:
        raise HTTPException(status_code=res.status_code, detail=f"HTTP error occurred: {str(http_err)}")
    except requests.RequestException as req_err:
        raise HTTPException(status_code=500, detail=f"Request exception occurred: {str(req_err)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

def content_scrap(to_scrap: str, pattern: str, group_number: int = 0):
    content_match = re.search(pattern, to_scrap)

    if content_match is None:
        return None

    return content_match.group(group_number)

def scrap_all_content(to_scrap: str, pattern: str):
    return re.findall(pattern, to_scrap)
