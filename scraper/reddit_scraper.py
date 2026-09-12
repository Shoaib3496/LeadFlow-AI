import requests

url = "https://www.reddit.com/r/forhire/new.json"

headers = {
    "User-Agent": "LeadFlowAI/1.0"
}

response = requests.get(url, headers=headers)

print("Status Code:", response.status_code)

if response.status_code == 200:
    data = response.json()

    posts = data["data"]["children"]

    for post in posts[:10]:
        title = post["data"]["title"]
        print(title)
else:
    print("Failed to fetch data")