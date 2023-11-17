
CF_DIR="/tmp/Cloudflare"

# 定义变量CF_CDN_IP，值为列表104.16.0,104.17.0,104.18.0,104.19.0
# CF_CDN_IP=(104.16.0 104.17.0 104.18.0 104.19.0)
CF_CDN_IP=(104.16.0)


URL_SPEED="https://url-test.6565.eu.org/test"

IP_RESULT="result.csv"


ZONE_ID=444f2e8c1ab64a1d390c0cd347357a12 #查看待操作域名的 ZONE_ID（在域名概要页面右下角可以看到）
CF_API_KEY="在用户信息里面查看Global KEY"
CF_API_EMAIL="CloudFlare的登录账号"

DNS_RECORDS=dns_records.json


# 根据ping包获取按照延迟从低到高排序作为Cloud法拉reST优选来源IP
# for i in {1..254};do ping -c1 $CF_CDN_IP.$i |grep from;done | awk '{print $4,$7}' | awk -F ":" '{print $1,$2}' | awk -F "time=" '{print $1,$2}' |sort -nk2 |column -t | head -100 |awk '{print $1}'> $CF_DIR/45102-1-443.txt

function CF_INSTALL(){
    # 如果是第一次使用，则建议创建新文件夹（后续更新时，跳过该步骤）
    mkdir ${CF_DIR}

    # 进入文件夹（后续更新，只需要从这里重复下面的下载、解压命令即可）
    cd ${CF_DIR}

    # 下载 CloudflareST 压缩包（自行根据需求替换 URL 中 [版本号] 和 [文件名]）
    wget -N https://ghproxy.6565.eu.org/https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.2.4/CloudflareST_linux_amd64.tar.gz
    # 如果你是在国内服务器上下载，那么请使用下面这几个镜像加速：
    # wget -N https://download.fgit.ml/XIU2/CloudflareSpeedTest/releases/download/v2.2.4/CloudflareST_linux_amd64.tar.gz
    # wget -N https://download.fgit.gq/XIU2/CloudflareSpeedTest/releases/download/v2.2.4/CloudflareST_linux_amd64.tar.gz
    # wget -N https://ghproxy.com/https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.2.4/CloudflareST_linux_amd64.tar.gz
    # 如果下载失败的话，尝试删除 -N 参数（如果是为了更新，则记得提前删除旧压缩包 rm CloudflareST_linux_amd64.tar.gz ）

    # 解压（不需要删除旧文件，会直接覆盖，自行根据需求替换 文件名）
    tar -zxf CloudflareST_linux_amd64.tar.gz

    # 赋予执行权限
    chmod +x CloudflareST

}

function CF_GET_IP(){
        curl --location --request GET 'http://ip.flares.cloud/whole/ip_list.csv' \
        --header 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0' \
        -s -o ${CF_DIR}/ip_list.csv
}

function CF_SPEED_TEST()
{
    CF_IP_FILE="ip.txt"


    # 清空文件ip.txt
    echo "" > $CF_IP_FILE
    # for循环CF_CDN_IP，根据每个值获取完整IP列表，比如循环104.16.0，根据0-254，获取到的ip为104.16.0.0到104.16.0.254并追加到ip.txt文件中
    for i in ${CF_CDN_IP[@]};do for j in {0..254};do echo $i.$j >> $CF_IP_FILE;done;done
    # 清空result.csv
    echo "" >$IP_RESULT 
    # 延迟140毫秒一下，下载速度30MB/s,
    $CF_DIR/CloudflareST -tp 443 -f $CF_DIR/$CF_IP_FILE -url $URL_SPEED -sl 30 -tl 140 -dn 10

}



function DELETE_DNS_RECORD()
{
    curl --location --request GET "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
    --header "X-Auth-Key: ${CF_API_KEY}" \
    --header "X-Auth-Email: ${CF_API_EMAIL}" \
    -s -o ${DNS_RECORDS}

    # 获取待删除域名cvproxy.6565.eu.org的域名对应的id
    DNS_LIST_DEL=($(cat ${DNS_RECORDS} | jq -r '.result[] | select(.zone_name == "6565.eu.org" and .name == "cfproxy.6565.eu.org") | .id'))

    for RECORD_ID in ${DNS_LIST_DEL[@]};do
        curl --location --request DELETE "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records/${RECORD_ID}" \
        --header "X-Auth-Key: ${CF_API_KEY}" \
        --header "X-Auth-Email: ${CF_API_EMAIL}" 
    done  
}



#增加DNS记录
#TTL=1 为自动
#proxied=true 使用CF的CDN,等于false是不使用
#data传入变量格式： "'"$EVN"'"
#设置变量

function ADD_DNS_RECORD()
{
    # 添加优选IP解析记录
    IP=$(cat $IP_RESULT | sed 1d |awk -F "," '{print $1}')

    for ip in $IP
    do
        curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
            -H "X-Auth-Email:${CF_API_EMAIL}" \
            -H "X-Auth-Key:${CF_API_KEY}" \
            -H "Content-Type:application/json" \
            --data '{"type":"A","name":"cfproxy","content":"'"${ip}"'","ttl":1,"priority":10,"proxied":false}'
    done
}



function example()
{
#增加DNS记录
#TTL=1 为自动
#proxied=true 使用CF的CDN,等于false是不使用
#data传入变量格式： "'"$EVN"'"
#设置变量
    while read line
    do
        ZONE_NAME=$(ECHO "$line" | awk '{print $1}')
        ZONE_ID=$(ECHO "$line" | awk '{print $2}') 
        curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
            -H "X-Auth-Email:${CF_API_EMAIL}" \
            -H "X-Auth-Key:${CF_API_KEY}" \
            -H "Content-Type:application/json" \
            --data '{"type":"A","name":"@","content":"'"${CONTENT_A}"'","ttl":1,"priority":10,"proxied":true}'

        curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
            -H "X-Auth-Email:${CF_API_EMAIL}" \
            -H "X-Auth-Key:${CF_API_KEY}" \
            -H "Content-Type:application/json" \
            --data '{"type":"CNAME","name":"www","content":"'"${CONTENT_CNAME}"'","ttl":1,"priority":10,"proxied":false}'

        curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
            -H "X-Auth-Email:${CF_API_EMAIL}" \
            -H "X-Auth-Key:${CF_API_KEY}" \
            -H "Content-Type:application/json" \
            --data '{"type":"CNAME","name":"m","content":"'"${CONTENT_CNAME}"'","ttl":1,"priority":10,"proxied":false}'
    done < $PWD/zone_id.cf
}


# CF_INSTALL # 安装优选测试服务
# CF_GET_IP  # 获取优选IP列表
CF_SPEED_TEST # 执行优选IP删选的函数
DELETE_DNS_RECORD # 执行删除dns记录的函数
ADD_DNS_RECORD # 执行添加dns记录的函数