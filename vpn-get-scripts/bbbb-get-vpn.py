import requests
import random
import json
import base64
import urllib3

# 禁止InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generate_device_id():
    return "001168." + ''.join(random.choice("0123456789abcdef") for _ in range(32))

def login_and_get_token():
    url = 'https://94.74.97.241/api/v1/passport/auth/loginByDeviceId'
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'User-Agent': 'BeesVPN/2 CFNetwork/1568.100.1 Darwin/24.0.0'
    }
    payload = {"invite_token": "", "device_id": generate_device_id()}
    try:
        response = requests.post(url, headers=headers, json=payload, verify=False)
        response.raise_for_status()
        return response.json().get('data', {}).get('token')
    except (requests.RequestException, KeyError):
        print('Login failed.')
        return None

def fetch_and_process_subscription(token):
    url = f'https://94.74.97.241/api/v1/client/appSubscribe?token={token}'
    headers = {
        'User-Agent': 'BeesVPN/2 CFNetwork/1568.100.1 Darwin/24.0.0'
    }
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json().get('data', [])
        return [
            sub_item['url'].replace('vless:\\/\\/', 'vless://')
            for item in data for sub_item in item.get('list', [])
            if 'url' in sub_item
        ]
    except (requests.RequestException, KeyError):
        print('获取订阅失败.')
        return None

def post_to_dpaste(encoded_content):
    try:
        response = requests.post("https://dpaste.com/api/", data={'expiry_days': 3, 'content': encoded_content})
        response.raise_for_status()
        dpaste_url = response.text.strip() + ".txt"
        print(f"恭喜你成功获得订阅: {dpaste_url}")
    except requests.RequestException:
        print("你长丑了、获取失败.")

def main():
    token = login_and_get_token()
    if not token:
        return
    urls = fetch_and_process_subscription(token)
    if not urls:
        return
    post_to_dpaste(base64.b64encode("\n".join(urls).encode('utf-8')).decode('utf-8'))

if __name__ == "__main__":
    main()
