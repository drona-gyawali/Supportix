import requests

url = "http://127.0.0.1:8000/app/alert/msg/"
data = {"message": "Disk space is High!"}

response = requests.post(url, json=data)
print(response.json())
