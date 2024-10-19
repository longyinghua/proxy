import requests
import json
import base64
import pyaes
import re
import random
import uuid  # 导入uuid模块

# 密钥和用户ID
# encryption_key = "c3e7254f65b8c39e9d6391fd422140f3"  # 此变量未被使用,已注释
uid = "3690911436885991424"  # 注释掉原来的uid
# uid_tg_hello_world = "3690911436885991424"  # 注释掉原来的uid
uid_long = "3672449415702126592"  # 新增的uid变量

decrypted_subscribe_links = []

def generate_uuid():
    """
    生成一个随机的UUID
    :return: 生成的UUID
    """
    return str(uuid.uuid4())

def decrypt_data(encrypted_data, key, iv):
    """
    使用AES算法解密数据
    :param encrypted_data: 加密的数据
    :param key: AES密钥
    :param iv: 初始化向量
    :return: 解密后的字符串
    """
    decrypted_data = base64.b64decode(encrypted_data)  # 对加密数据进行Base64解码
    aes = pyaes.AESModeOfOperationCBC(key, iv=iv)  # 创建AES解密对象,使用CBC模式
    decrypted_output = b""  # 初始化解密输出
    while decrypted_data:  # 循环处理数据直到全部解密
        decrypted_output += aes.decrypt(decrypted_data[:16])  # 解密每一块16字节的数据
        decrypted_data = decrypted_data[16:]
    padding_length = decrypted_output[-1]  # 获取填充长度
    return decrypted_output[:-padding_length].decode('utf-8')  # 去掉填充并解码为字符串

def fetch_vpn_nodes():
    """
    从API获取VPN节点信息
    :return: JSON格式的节点信息
    """
    api_url = "https://api.9527.click/v2/node/list"  # API的URL
    headers = {
        'Host': 'api.9527.click',
        'Content-Type': 'application/json',
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'User-Agent': 'International/3.3.35 (iPhone; iOS 18.0.1; Scale/3.00)',
        'Accept-Language': 'zh-Hans-CN;q=1',
        'Accept-Encoding': 'gzip, deflate, br'
    }  # 请求头信息
    payload = {
        "key": "G8Jxb2YtcONGmQwN7b5odg==",
        "uid": uid,  # 使用uid_long
        "vercode": "1",
        #"uuid": "0273F74A-3F2E-44FB-8F87-717C9E3518E3"  # 保留原有的uuid注释
        "uuid": generate_uuid()  # 使用新生成的uuid
    }  # 请求体数据
    response = requests.post(api_url, headers=headers, json=payload)  # 发送POST请求
    if response.status_code == 200:
        return json.loads(response.text)  # 如果请求成功,返回JSON数据
    else:
        print(f"Failed to fetch data: {response.status_code}")  # 如果请求失败,打印错误码
        return None

def generate_subscription_links():
    """
    生成订阅链接并发布到dpaste.com
    """
    encrypted_key = b'VXH2THdPBsHEp+TY'
    encrypted_iv = b'VXH2THdPBsHEp+TY'
    node_data = fetch_vpn_nodes()  # 获取节点数据
    if not node_data:
        print("Failed to fetch node data")
        return
    if 'data' not in node_data:
        print("Data format error")
        return
    for node in node_data['data']:  # 遍历节点数据
        if 'ip' in node and node['ip']:  # 检查节点数据中是否有'ip'键,并且对应的值不为空
            node['ip'] = decrypt_data(node['ip'], encrypted_key, encrypted_iv)  # 如果有,调用decrypt_data函数解密IP地址

        if 'host' in node and node['host']:  # 检查节点数据中是否有'host'键,并且对应的值不为空
            node['host'] = decrypt_data(node['host'], encrypted_key, encrypted_iv)  # 如果有,调用decrypt_data函数解密主机名

        if 'ov_host' in node and node['ov_host']:  # 检查节点数据中是否有'ov_host'键,并且对应的值不为空
            node['ov_host'] = decrypt_data(node['ov_host'], encrypted_key, encrypted_iv)  # 如果有,调用decrypt_data函数解密覆盖主机名

        host = node.get('host') or node.get('ip')  # 尝试获取节点数据中的'host',如果不存在,则尝试获取'ip'
        name = node.get('name', 'Unknown')  # 尝试获取节点数据中的'name',如果不存在,则默认为'Unknown'
        link = f"trojan://{uid}@{host}:443?allowInsecure=1#{name}"  # 生成订阅链接
        decrypted_subscribe_links.append(link)  # 添加到链接列表

    decrypted_subscribe_links.sort(key=lambda link: re.search(r'#(\w+)', link).group(1) if re.search(r'#(\w+)', link) else '')  # 根据节点名称排序
    encoded_content = base64.b64encode('\n'.join(decrypted_subscribe_links).encode('utf-8')).decode('utf-8')  # 将链接编码为Base64
    # post_to_dpaste(encoded_content)  # 发布到dpaste.com
    
    post_to_dpaste_another(decrypted_subscribe_links)  # 发布到dpaste.com

def post_to_dpaste(encoded_content):
    """
    将Base64编码的订阅链接发布到dpaste.com
    :param encoded_content: 编码后的订阅链接内容
    """
    response = requests.post("https://dpaste.com/api/v2/", data={"content": encoded_content})  # 发送POST请求
    if response.status_code == 201:
        dpaste_url = response.text.strip() + ".txt"  # 生成dpaste链接
        print("Subscription link generated...")  # 打印提示信息
        print("Link:", dpaste_url)  # 打印链接
    else:
        print("Failed to post to dpaste, status code:", response.status_code)  # 如果请求失败,打印错误码


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
        'expiry_days': 1,
        'private': True
    }
    dpaste_response = requests.post(dpaste_url, data=dpaste_data)

    if dpaste_response.ok:
        print("订阅：", dpaste_response.text.strip() + ".txt")
    else:
        print("上传失败，状态码：", dpaste_response.status_code)


if __name__ == "__main__":
    generate_subscription_links()  # 执行主程序


