'''
By: unorz
'''
import time  # 导入时间模块
import hashlib  # 导入哈希模块
import base64  # 导入base64编码模块
import pyaes  # 导入AES加密模块
import requests  # 导入HTTP请求模块
from urllib.parse import quote  # 导入URL编码模块

urls = []  # 订阅链接列表
# 生成请求密钥
def get_request_key(t, i, k):
    ts = str(t)  # 将时间戳转换为字符串
    # 根据时间戳的奇偶性选择索引
    r = [5,11,11,8,27,12,9,21] if t & 1 != 0 else [16,8,10,12,26,11,2,18]
    # 根据索引构建密钥
    key = i[r[0]]+i[r[1]]+ts[r[2]]+i[r[3]]+i[r[4]]+ts[r[5]]+i[r[6]]+i[r[7]]
    key += k[int(ts[11])] if len(k) else i[int(ts[11])]  # 处理密钥的附加部分
    return key  # 返回生成的密钥

# 生成解密密钥
def get_decrypt_key(t, i, k):
    ts = str(t)  # 将时间戳转换为字符串
    r = [5,11,11,8,27,12,9,21] if t & 1 != 0 else [16,8,10,12,26,11,2,18]
    # 根据索引构建密钥
    key = i[r[0]]+i[r[1]]+ts[r[2]]+i[r[3]]+i[r[4]]+ts[r[5]]+i[r[6]]+i[r[7]]
    key += k[r[0]]+k[r[1]]+ts[r[2]]+k[r[3]]+k[r[4]]+ts[r[5]]+k[r[6]]+k[r[7]]  # 添加解密密钥部分
    return key  # 返回解密密钥

# 获取当前时间戳（毫秒）
def timestamp():
    return int(time.time() * 1000)  # 返回当前时间戳

# 生成请求ID
def gen_req_id():
    t = int(time.time() / 1800)  # 获取当前时间（半小时为单位）
    return hashlib.md5(f'req_id_{t}'.encode()).hexdigest()  # 返回MD5哈希

# 生成序列号
def gen_serial_num():
    t = int(time.time() * 1000)  # 获取当前时间戳（毫秒）
    return hashlib.md5(f'serial_num_{t}'.encode()).hexdigest()  # 返回MD5哈希

# AES解密函数
def aes_decrypt(key, text):
    textbytes = base64.b64decode(text)  # 对密文进行base64解码
    decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key.encode(), b'A-16-Byte-String'))  # 创建解密器
    plainbytes = decrypter.feed(textbytes)  # 解密数据
    plainbytes += decrypter.feed()  # 完成解密
    return plainbytes.decode('utf-8')  # 返回解密后的字符串

# 准备请求参数
def prepare_params(params):
    params['clientModel'] = 'V1936A'  # 添加客户端型号
    params['clientType'] = 'Android'  # 添加客户端类型
    params['promoteChannel'] = 'S100'  # 添加推广渠道
    params['rankVersion'] = '10'  # 添加版本信息
    params['version'] = 'v2.0.4'  # 添加API版本
    params = dict(sorted(params.items()))  # 对参数进行排序
    param_str = ''  # 初始化参数字符串
    for k in params.keys():  # 遍历所有参数
        param_str += f'{k}={params[k]}&'  # 拼接参数字符串
    param_str = param_str.rstrip('&')  # 去掉末尾的&
    sign_key = get_request_key(params['requestTimestamp'], params['requestId'], params.get('token', ''))  # 生成签名密钥
    params['sign'] = hashlib.md5(f'{param_str}{sign_key}'.encode()).hexdigest()  # 计算签名
    return params  # 返回处理后的参数

session = requests.Session()  # 创建一个会话对象
session.trust_env = False  # 不信任环境变量

# 定义请求头
headers = {
    'Accept-Language': 'zh-CN,zh;q=0.8',  # 设置接受的语言
    'User-Agent': 'Mozilla/5.0 (Linux; U; Android 7.1.2; zh-cn; V1936A Build/N2G47O) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',  # 设置用户代理
    'Content-Type': 'application/x-www-form-urlencoded'  # 设置内容类型
}

# 登录函数
def login(serial):
    try:
        params = prepare_params({  # 准备请求参数
            'requestId': gen_req_id(),  # 生成请求ID
            'requestTimestamp': timestamp(),  # 获取当前时间戳
            'serialNumber': serial  # 添加序列号
        })
        response = session.post('https://api.go01.top/proxy/user/auto/login', headers=headers, data=params)  # 发送登录请求
        response.raise_for_status()  # 检查请求是否成功
        return response.json().get('data').get('token')  # 返回token
    except Exception as e:
        print(f'登录失败：{e}')  # 捕获异常并打印错误信息

# 获取节点列表函数
def node_list(serial, token):
    try:
        params = prepare_params({  # 准备请求参数
            'requestId': gen_req_id(),  # 生成请求ID
            'requestTimestamp': timestamp(),  # 获取当前时间戳
            'serialNumber': serial,  # 添加序列号
            'token': token,  # 添加token
            'vipType': 'vip'  # 添加VIP类型
        })
        response = session.post('https://api.go01.top/proxy/user/fetch/node/list', headers=headers, data=params)  # 发送请求
        response.raise_for_status()  # 检查请求是否成功
        return response.json().get('data')  # 返回节点列表
    except Exception as e:
        print(f'获取节点列表失败：{e}')  # 捕获异常并打印错误信息

# 获取节点详细信息函数
def node_detail(serial, token, node_id):
    try:
        t = timestamp()  # 获取当前时间戳
        rid = gen_req_id()  # 生成请求ID
        params = prepare_params({  # 准备请求参数
            'requestId': rid,  # 添加请求ID
            'requestTimestamp': t,  # 添加时间戳
            'serialNumber': serial,  # 添加序列号
            'token': token,  # 添加token
            'nodeId': node_id  # 添加节点ID
        })
        response = session.post('https://api.go01.top/proxy/user/fetch/node/detail', headers=headers, data=params)  # 发送请求
        response.raise_for_status()  # 检查请求是否成功
        data = response.json().get('data')  # 获取返回的数据
        key = get_decrypt_key(t, rid, token)  # 生成解密密钥
        info = aes_decrypt(key, data.get('content')).split(',')  # 解密节点信息并分割
        trojan = f'trojan://{info[3]}@{info[1]}:{info[2]}?security=tls&type=tcp&headerType=none&allowInsecure=1#{quote(data.get("name"))}'  # 构建trojan链接
        print(trojan)  # 打印链接
        # 将解密后的订阅链接加入到订阅链接列表
        urls.append(trojan)
    except Exception as e:
        print(f'获取节点信息失败：{e}')  # 捕获异常并打印错误信息

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

if __name__ == "__main__":       
     
    serial = gen_serial_num()  # 生成序列号
    
    token = login(serial)  # 登录并获取token
    
    if token:  # 如果token存在
        nodes = node_list(serial, token)  # 获取节点列表
        for node in nodes:  # 遍历节点
            node_detail(serial, token, node.get('id'))  # 获取每个节点的详细信息
    

    post_to_dpaste_another(urls)  # 将订阅链接上传到dpaste
