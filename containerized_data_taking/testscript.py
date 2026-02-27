import requests

def get_attribute(entity_str):
    url = "http://localhost:8000/get?keys=" + entity_str
    return requests.get(url).json()[entity_str]

x = get_attribute("run_status")
print(x)
