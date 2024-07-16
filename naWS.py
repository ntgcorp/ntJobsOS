
IN COSTRUZIONE
------------

Approach 1: Using json parameter
import requests

response = requests.post('https://httpbin.org/post', json={'id': 1, 'name': 'Jessa'})

print("Status code: ", response.status_code)
print("Printing Entire Post Request")
print(response.json())
Output:

Status code:  200

Printing Entire Post Request

{'args': {}, 
'data': '{"id": 1, "name": "Jessa"}', 
'files': {}, 'form': {}, 
'headers': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 
'Content-Length': '26', 
'Content-Type': 'application/json', 
'Host': 'httpbin.org', 
'User-Agent': 'python-requests/2.21.0'}, '
json': {'id': 1, 'name': 'Jessa'}, 
'origin': 'xxx.xx.xx.xx, xxx.xx.xx.xx', 'url': 'https://httpbin.org/post'}