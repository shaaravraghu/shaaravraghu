import requests
from bs4 import BeautifulSoup
import re

USERNAME = "shaaravraghu"

periods = {
    "Today": "",
    "This Week": "?since=weekly",
    "This Month": "?since=monthly"
}

results = []

headers = {
    "User-Agent": "Mozilla/5.0"
}

for period, suffix in periods.items():

    url = "https://github.com/trending/developers" + suffix

    html = requests.get(url, headers=headers).text

    soup = BeautifulSoup(html, "html.parser")

    devs = soup.select("article.Box-row")

    rank = None

    for i, dev in enumerate(devs, start=1):

        username = dev.find("p").text.strip().replace("@","")

        if username.lower() == USERNAME.lower():
            rank = i
            break

    if rank:
        results.append(f"| {period} | 🏆 #{rank} |")
    else:
        results.append(f"| {period} | Not Trending |")

table = """| Period | Rank |
|---|---|
"""

table += "\n".join(results)

readme = open("README.md","r",encoding="utf-8").read()

pattern = r'<!-- TRENDING_START -->(.*?)<!-- TRENDING_END -->'

replacement = f"""<!-- TRENDING_START -->
{table}
<!-- TRENDING_END -->"""

readme = re.sub(pattern, replacement, readme, flags=re.S)

open("README.md","w",encoding="utf-8").write(readme)
