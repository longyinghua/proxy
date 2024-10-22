import os  # 导入操作系统接口模块
import requests  # 导入HTTP请求库
import json  # 导入JSON处理库
import time  # 导入时间处理库
import uuid  # 导入UUID生成库
import pyaes  # 导入AES加密库
from Crypto.Cipher import AES  # 导入AES加密库
from Crypto.Util.Padding import pad, unpad  # 导入填充和去填充函数
import base64  # 导入Base64编码库
from requests.adapters import HTTPAdapter  # 导入HTTP适配器
from requests.packages.urllib3.util.retry import Retry  # 导入重试机制
from datetime import datetime, timedelta  # 导入日期时间处理库

proxy_urls = []  # 初始化代理URL列表


def encrypt_aes(data, key, iv):
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))  # 创建AES加密对象
    ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))  # 加密数据
    return base64.b64encode(ct_bytes).decode('utf-8')  # 返回Base64编码的加密字符串

# 解密函数
def decrypt_aes(encrypted_data, key, iv):
    encrypted_bytes = base64.b64decode(encrypted_data)  # 解码Base64加密字符串
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))  # 创建AES解密对象
    decrypted_padded = cipher.decrypt(encrypted_bytes)  # 解密数据
    decrypted = unpad(decrypted_padded, AES.block_size)  # 去除填充
    return decrypted.decode('utf-8')  # 返回解密后的字符串

    
# 请求头准备函数
def prepare_headers(session, device_uuid):
    current_timestamp = str(int(time.time()))  # 获取当前时间戳
    header_data = {
        "h-time": current_timestamp,
        "h-client": "android",
        "h-oem": "website",
        "jOlaWEOrIfkemD11xzNwyjNSijWwyzncv": device_uuid,
        "h-version": "2.2.3",
        "h-language": "CN"
    }
    key = iv = "ubje0xtjWTpZyGTV"  # 设置加密密钥和初始化向量
    
    # encrypted_header = encrypt_aes(json.dumps(header_data), key, iv)  # 加密请求头
    
    encrypted_header = aes_encrypt_1(json.dumps(header_data), key, iv)  # 加密请求头
    
    return {
        "jOlaACOrIfkemD12xzNwxjNSijWwyzncvde": encrypted_header
    }

# 请求重试会话函数
def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()  # 创建或获取请求会话
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)  # 创建HTTP适配器
    session.mount('http://', adapter)  # 挂载HTTP适配器
    session.mount('https://', adapter)  # 挂载HTTPS适配器
    return session

# 获取线路列表函数
def lines_list(session, device_uuid, url):
    headers = prepare_headers(session, device_uuid)  # 准备请求头
    response = requests_retry_session(session=session).post(url, data={}, headers=headers, timeout=10)  # 发送POST请求
    return response.text  # 返回响应文本

# 节点协议函数
def node_protocol(session, device_uuid, code, url):
    data = {"code": code}  # 设置请求数据
    headers = prepare_headers(session, device_uuid)  # 准备请求头
    response = requests_retry_session(session=session).post(url, data=data, headers=headers, timeout=10)  # 发送POST请求
    return response.text  # 返回响应文本

# 保存节点到文件函数
def save_to_file(urls):
    with open("saidun.txt", "a", encoding="utf-8") as file:  # 打开文件进行追加写入
        for url in urls:  # 遍历URL列表
            file.write(url + "\n")  # 写入每个URL
    print("节点已经报保存到saidun.txt文件")  # 输出保存成功信息

# 生成或加载UUID函数
def load_or_generate_uuid():
    uuid_file = "device_uuid.txt"  # 定义UUID文件路径
    current_time = datetime.now()  # 获取当前时间

    if os.path.exists(uuid_file):  # 检查UUID文件是否存在
        with open(uuid_file, "r") as file:  # 打开文件读取
            lines = file.readlines()  # 读取所有行
            if len(lines) == 2:  # 如果文件包含两行
                stored_uuid = lines[0].strip()  # 获取存储的UUID
                stored_time = datetime.fromisoformat(lines[1].strip())  # 获取存储的时间

                # 检查是否已经过去 60 分钟
                if current_time - stored_time < timedelta(minutes=60):
                    return stored_uuid  # 返回存储的UUID

    # 生成新的 UUID 并与当前时间一起保存
    new_uuid = str(uuid.uuid4())  # 生成新的UUID
    with open(uuid_file, "w") as file:  # 打开文件写入
        file.write(new_uuid + "\n")  # 写入新的UUID
        file.write(current_time.isoformat() + "\n")  # 写入当前时间
    return new_uuid  # 返回新生成的UUID

# 从API获取数据函数
def fetch_from_api(lines_list_url, node_protocol_url, device_uuid):
    session = requests.Session()  # 创建请求会话
    urls = []  # 初始化URL列表
    try:
        lines_list_result = lines_list(session, device_uuid, lines_list_url)  # 获取线路列表
        linesOjb = json.loads(lines_list_result)  # 解析JSON响应
        nodes = linesOjb['result']['nodes']  # 获取节点列表
        for n in nodes:  # 遍历节点
            code = n['code']  # 获取节点代码
            node_protocol_result = node_protocol(session, device_uuid, code, node_protocol_url)  # 获取节点协议
            nodeProtocolObj = json.loads(node_protocol_result)  # 解析JSON响应
            url = nodeProtocolObj['result']['url']  # 获取节点URL
            
            decrypted_url = decrypt_aes(url, 'TmPrPhkOf8by0cvx', 'TmPrPhkOf8by0cvx')  # 解密URL
            
            
            print(decrypted_url)  # 输出解密后的URL
            urls.append(decrypted_url)  # 添加到URL列表
    except Exception as e:
        print(f"API 发生错误: {e}")  # 输出错误信息

    save_to_file(urls)  # 保存URL到文件
    return urls  # 返回URL列表

# 上传到dpaste函数
def post_to_dpaste_another(decrypted_subscribe_links):
    """
    将订阅链接上传到dpaste
    :param decrypted_subscribe_links: 订阅链接列表
    :return: None
    """
    encoded_data = base64.b64encode('\n'.join(decrypted_subscribe_links).encode('utf-8')).decode('utf-8')  # 编码订阅链接
    dpaste_url = "https://dpaste.com/api/"  # dpaste API URL
    dpaste_data = {
        'content': encoded_data,
        'syntax': 'text',
        'expiry_days': 7,
        'private': True
    }
    dpaste_response = requests.post(dpaste_url, data=dpaste_data)  # 发送POST请求

    if dpaste_response.ok:  # 如果请求成功
        print("订阅：", dpaste_response.text.strip() + ".txt")  # 输出dpaste链接
    else:
        print("上传失败，状态码：", dpaste_response.status_code)  # 输出失败状态码

# 删除文件函数
def delete_saidun_txt():
    # 获取当前目录的绝对路径
    current_directory = os.path.abspath('.')
    file_path = os.path.join(current_directory, 'saidun.txt')  # 定义文件路径
    
    if os.path.exists(file_path):  # 检查文件是否存在
        os.remove(file_path)  # 删除文件
        # print(f"{file_path} 已成功删除。")  # 输出删除成功信息
    else:
        pass 
        # print(f"{file_path} 文件不存在。")  # 输出文件不存在信息

if __name__ == "__main__":
    
    device_uuid = load_or_generate_uuid()  # 生成或加载设备UUID

    delete_saidun_txt()  # 删除saidun.txt文件
    
    url1 = fetch_from_api(
        "http://api.saidun666.com/vpn/lines_list",
        "http://api.saidun666.com/vpn/node_protocol",
        device_uuid
    )
    
    url2 = fetch_from_api(
        "http://api.saidun.biz/vpn/lines_list",
        "http://api.saidun.biz/vpn/node_protocol",
        device_uuid
    )
    
    proxy_urls = url1 + url2
    
    post_to_dpaste_another(proxy_urls)