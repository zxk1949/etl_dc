import requests

res = requests.post('http://127.0.0.1:8000/api/login/', data={'username': 'admin', 'password': 'admin1'})
print(res.text)