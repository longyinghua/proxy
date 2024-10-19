import requests
import re
import base64

url = "http://hs.vir-link.cn:2088/api/vpn/subscription_v3"
params = {'e': '917952140@qq.com', 'p': 'tBX/'}
response = requests.get(url, params=params)
data = response.json()

links = []

for item in data.get('data', []):
    for node in item.get('list', []):
        link = node.get('link', 'N/A')
        if 'vless://' in link:
            link = link.split('vless://', 1)[-1]
            link = 'vless://' + link
        links.append(link)

links = sorted(links, key=lambda x: re.sub(r'[^a-zA-Z0-9]', '', x))

encoded_data = base64.b64encode('\n'.join(links).encode('utf-8')).decode('utf-8')

dpaste_url = "https://dpaste.com/api/"
dpaste_data = {
    'content': encoded_data,
    'syntax': 'text',
    'expiry_days': 1,
    'private': True
}
dpaste_response = requests.post(dpaste_url, data=dpaste_data)

if dpaste_response.ok:
    print("订阅：", dpaste_response.text.strip() + ".txt")
else:
    print("上传失败，状态码：", dpaste_response.status_code)