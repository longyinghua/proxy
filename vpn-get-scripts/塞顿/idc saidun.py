import requests
import json
import time
import uuid
import base64
import os
from Crypto.Cipher import AES
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

# 手动填充函数 (PKCS7填充)
def manual_pad(data, block_size=16):
    pad_length = block_size - (len(data) % block_size)
    return data + (chr(pad_length) * pad_length)

# 手动去填充函数
def manual_unpad(padded_data):
    pad_length = ord(padded_data[-1])
    return padded_data[:-pad_length]

# AES加密函数
def encrypt_aes(data, key, iv):
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    padded_data = manual_pad(data)
    ct_bytes = cipher.encrypt(padded_data.encode('utf-8'))
    return base64.b64encode(ct_bytes).decode('utf-8')

# AES解密函数
def decrypt_aes(encrypted_data, key, iv):
    encrypted_bytes = base64.b64decode(encrypted_data)
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    decrypted_padded = cipher.decrypt(encrypted_bytes)
    decrypted = manual_unpad(decrypted_padded.decode('utf-8'))
    return decrypted

# 准备HTTP请求的headers
def prepare_headers(session, device_uuid):
    current_timestamp = str(int(time.time()))
    header_data = {
        "h-time": current_timestamp,
        "h-client": "android",
        "h-oem": "website",
        "jOlaWEOrIfkemD11xzNwyjNSijWwyzncv": device_uuid,
        "h-version": "2.2.3",
        "h-language": "CN"
    }

    key = iv = "ubje0xtjWTpZyGTV"
    encrypted_header = encrypt_aes(json.dumps(header_data), key, iv)
    return {
        "jOlaACOrIfkemD12xzNwxjNSijWwyzncvde": encrypted_header
    }

# 获取VPN节点列表
def lines_list(session, device_uuid):
    url = "http://api.saidun.biz/vpn/lines_list"
    headers = prepare_headers(session, device_uuid)
    response = session.post(url, data={}, headers=headers)
    return response.text

# 获取VPN节点协议
def node_protocol(session, device_uuid, code):
    url = "http://api.saidun.biz/vpn/node_protocol"
    data = {
        "code": code
    }
    headers = prepare_headers(session, device_uuid)
    response = session.post(url, data=data, headers=headers)
    return response.text

# 处理每个节点获取URL并解密
def process_node(session, device_uuid, node):
    code = node['code']
    node_protocol_result = node_protocol(session, device_uuid, code)
    nodeProtocolObj = json.loads(node_protocol_result)
    url = nodeProtocolObj['result']['url']
    decrypted_url = decrypt_aes(url, 'TmPrPhkOf8by0cvx', 'TmPrPhkOf8by0cvx')
    return decrypted_url

# 读取缓存的UUID并检查时间
def get_cached_uuid(file_path="uuid_cache.json"):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            cached_time = datetime.strptime(data["timestamp"], '%Y-%m-%d %H:%M:%S')
            current_time = datetime.now()
            if current_time - cached_time < timedelta(hours=1):  # 检查是否超过60分钟
                return data["uuid"]
    return None

# 保存新的UUID到缓存文件
def save_uuid_to_cache(uuid_value, file_path="uuid_cache.json"):
    with open(file_path, 'w') as f:
        data = {
            "uuid": uuid_value,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        json.dump(data, f)

# 获取UUID,若缓存存在则使用,否则生成新的
def get_uuid():
    cached_uuid = get_cached_uuid()
    if cached_uuid:
        return cached_uuid
    else:
        new_uuid = str(uuid.uuid4())
        save_uuid_to_cache(new_uuid)
        return new_uuid

# 获取代理URL,使用并发进行优化
def get_proxy_url():
    session = requests.Session()
    device_uuid = get_uuid()  # 使用缓存或生成的UUID

    # 获取节点列表
    lines_list_result = lines_list(session, device_uuid)
    linesOjb = json.loads(lines_list_result)
    nodes = linesOjb['result']['nodes']
    
    # 使用线程池并发请求节点协议
    urls = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_node = {executor.submit(process_node, session, device_uuid, node): node for node in nodes}
        
        for future in as_completed(future_to_node):
            try:
                url = future.result()
                urls.append(url)
            except Exception as exc:
                print(f'节点生成异常: {exc}')

    # 输出所有解密后的URL
    for url in urls:
        print(url)
    
    # 输出节点总数(中文)
    # print(f"共{len(nodes)}个节点")
    
    return urls

def post_to_dpaste_another(decrypted_subscribe_links):
    """
    将订阅链接上传到dpaste
    :param decrypted_subscribe_links: 订阅链接列表
    :return: None
    """
    encoded_data = base64.b64encode('\n'.join(decrypted_subscribe_links).encode('utf-8')).decode('utf-8')
    dpaste_url = "https://dpaste.com/api/"
    dpaste_data = {
        'content': encoded_data,
        'syntax': 'text',
        'expiry_days': 7,
        'private': True
    }
    dpaste_response = requests.post(dpaste_url, data=dpaste_data)

    if dpaste_response.ok:
        print("订阅：", dpaste_response.text.strip() + ".txt")
    else:
        print("上传失败，状态码：", dpaste_response.status_code)

if __name__ == "__main__":
    # get_proxy_url()
    urls = get_proxy_url()
    
    post_to_dpaste_another(urls)
