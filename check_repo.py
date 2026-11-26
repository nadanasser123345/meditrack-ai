import requests

url = 'https://api.github.com/repos/nadanasser123345/meditrack-ai/contents'
res = requests.get(url)
print('STATUS:', res.status_code)
if res.status_code == 200:
    for item in res.json():
        print(f"[{item['type']}] {item['name']}")
else:
    print(res.text)
