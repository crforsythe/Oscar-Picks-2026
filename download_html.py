import requests

url = "https://en.wikipedia.org/wiki/98th_Academy_Awards"
headers = {"User-Agent": "Mozilla/5.0"}
resp = requests.get(url, headers=headers)
with open("page.html", "w") as f:
    f.write(resp.text)
