#!/bin/bash

# 检查Piplist是否存在
if [ ! -x "./Piplist" ]; then
    echo "错误: 未找到可执行文件 Piplist，请确保在脚本相同目录下存在该文件。"
    exit 1
fi

# 检查temp目录是否存在，不存在则创建
if [ ! -d "temp" ]; then
    mkdir "temp"
fi

# 下载cf.local.iplist文件
curl -L -o cf.local.iplist https://raw.githubusercontent.com/MortezaBashsiz/CFScanner/main/config/cf.local.iplist

# 检查下载是否成功
if [ $? -ne 0 ]; then
    echo "下载 cf.local.iplist 文件失败。脚本终止。"
    exit 1
fi

# 计数器初始化
count=1

# 遍历cf.local.iplist文件
while IFS= read -r line; do
    # 跳过空行
    if [ -z "$line" ]; then
        continue
    fi

    # 构建输出文件路径，以数字编号命名
    output_file="temp/${count}.txt"

    # 执行Piplist命令
    ./Piplist -IP "$line" -O "$output_file"

    echo "处理行: $line，输出文件: $output_file"

    # 增加计数器
    ((count++))
done < "cf.local.iplist"
