import requests

res = requests.get("https://webhookbin.net/v1/makebin")
print(res.text)
