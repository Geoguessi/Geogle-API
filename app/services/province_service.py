import requests
import re


url = 'https://www.tripniceday.com/en/country/th'

res = requests.get(url)
content = res.content.decode('utf-8')
pattern = r'<body>(.*?)</body>'
match = re.search(pattern, content, re.DOTALL)
if match:
    body = match.group(1)
else:
    raise ValueError("Body content not found")
a_link_re = r'<a[^>]*href="([^"]*)"[^>]*title="([^"]*)"[^>]*>([^<]+)</a>'
li_re = f'<li class="province-item">.*?{a_link_re}.*?</li>'

province_pattern = re.compile(li_re)
provinces = []

for province in province_pattern.findall(body):
    provinces.append(province[2]) 
    
def get_provinces():
    return provinces