
CF_DIR="/opt/Cloudflare"

# 定义变量CF_CDN_IP，值为列表104.16.0,104.17.0,104.18.0,104.19.0
# CF_CDN_IP=(104.16.0 104.17.0 104.18.0 104.19.0 162.159.0 172.65.0 173.245.49)
# CF_CDN_IP=(104.16.0 104.16.1 104.16.2 104.16.3 104.16.4 104.16.5 104.16.6 104.16.7 104.16.8 104.16.9 104.16.10 104.16.11 104.16.12等。。。)
CF_CDN_IP=(104.16.0)


# URL_SPEED="http://cachefly.cachefly.net/100mb.test"
URL_SPEED="https://url-test.6565.eu.org/test"
# URL_SPEED="spurl.api.030101.xyz/100mb"

IP_RESULT="result.csv"

speedurl="https://speed.cloudflare.com/__down?bytes=$((speedtestMB * 1000000))" #官方测速链接
proxygithub="https://mirror.ghproxy.com/" #反代github加速地址，如果不需要可以将引号内容删除，如需修改请确保/结尾 例如"https://mirror.ghproxy.com/"


ZONE_ID_6565=444f2e8c1ab64a1d390c0cd347357a12 #查看待操作域名的 ZONE_ID（在域名概要页面右下角可以看到）
ZONE_ID_9595=088f1d09e380de1abce2f7d97970e109
CF_API_KEY="xxxxxxxxxxxx"
CF_API_EMAIL="longyinghua126@gmail.com"

DNS_RECORDS=dns_records.json


# 根据ping包获取按照延迟从低到高排序作为Cloud法拉reST优选来源IP
# for i in {1..254};do ping -c1 $CF_CDN_IP.$i |grep from;done | awk '{print $4,$7}' | awk -F ":" '{print $1,$2}' | awk -F "time=" '{print $1,$2}' |sort -nk2 |column -t | head -100 |awk '{print $1}'> $CF_DIR/45102-1-443.txt

function CF_INSTALL(){
    # 如果是第一次使用，则建议创建新文件夹（后续更新时，跳过该步骤）
    mkdir ${CF_DIR}

    # 进入文件夹（后续更新，只需要从这里重复下面的下载、解压命令即可）
    cd ${CF_DIR}

    # 发送 API 请求获取仓库信息（替换 <username> 和 <repo>）
    latest_version=$(curl -s https://api.github.com/repos/XIU2/CloudflareSpeedTest/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
    if [ -z "$latest_version" ]; then
        latest_version="v2.2.4"
        echo "下载版本号: $latest_version"
    else
        echo "最新版本号: $latest_version"
    fi
    # 下载文件到当前目录
    curl -L -o CloudflareST.tar.gz "${proxygithub}https://github.com/XIU2/CloudflareSpeedTest/releases/download/$latest_version/CloudflareST_linux_amd64.tar.gz"


    # 下载 CloudflareST 压缩包（自行根据需求替换 URL 中 [版本号] 和 [文件名]）
    #wget -N https://ghproxy.6565.eu.org/https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.2.4/CloudflareST_linux_amd64.tar.gz

    # 如果你是在国内服务器上下载，那么请使用下面这几个镜像加速：
    # wget -N https://download.fgit.ml/XIU2/CloudflareSpeedTest/releases/download/v2.2.4/CloudflareST_linux_amd64.tar.gz
    # wget -N https://download.fgit.gq/XIU2/CloudflareSpeedTest/releases/download/v2.2.4/CloudflareST_linux_amd64.tar.gz
    # wget -N https://ghproxy.com/https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.2.4/CloudflareST_linux_amd64.tar.gz
    # 如果下载失败的话，尝试删除 -N 参数（如果是为了更新，则记得提前删除旧压缩包 rm CloudflareST_linux_amd64.tar.gz ）

    # 解压（不需要删除旧文件，会直接覆盖，自行根据需求替换 文件名）
    #tar -zxf CloudflareST_linux_amd64.tar.gz

    tar -xf CloudflareST.tar.gz

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

    # ./CloudflareST -tp 443 -f ip.txt -url https://url-test.6565.eu.org/test -sl 30 -tl 140 -dn 10  # 根据ip.txt文件进行测试
    

    # ./CloudflareST -ip 104.16.0.0/24  -allip -n 500 -tp 443 -url https://url-test.6565.eu.org/test  -sl 30 -tl 100 -dn 10  # 命令行根据ip段进行测试

}

function CF_PROXY_IP()
{
    rm -f txt.zip && rm -rf cf-ip-zip

    curl -s --location --request GET 'https://zip.baipiao.eu.org/' --header 'User-Agent: Apifox/1.0.0 (https://apifox.com)' --header 'Accept: */*' --header 'Host: zip.baipiao.eu.org' -o txt.zip

    mkdir cf-ip-zip

    unzip -q txt.zip -d cf-ip-zip 

    cd cf-ip-zip

    cat $(ls -l  |grep 0-80.txt  |awk '{print $9}') >${CF_DIR}/80-cf.txt
    cat $(ls -l  |grep 1-443.txt  |awk '{print $9}') >${CF_DIR}/443-cf.txt

    cd ${CF_DIR}


    $CF_DIR/CloudflareST -tp 443 -f $PWD/443-cf.txt -url https://url-test.6565.eu.org/test -sl 30 -tl 140 -dn 10 -o $PWD/443-result.csv

    # $CF_DIR/CloudflareST -tp 80 -f $PWD/80-cf.txt -url https://url-test.6565.eu.org/test -sl 30 -tl 140 -dn 10 -o $PWD/80-result.csv
}


function DELETE_DNS_RECORD()
{
    curl --location --request GET "https://api.cloudflare.com/client/v4/zones/${ZONE_ID_6565}/dns_records" \
    --header "X-Auth-Key: ${CF_API_KEY}" \
    --header "X-Auth-Email: ${CF_API_EMAIL}" \
    -s -o ${DNS_RECORDS}

    # 获取待删除域名cvproxy.6565.eu.org的域名对应的id
    DNS_LIST_DEL=($(cat ${DNS_RECORDS} | jq -r '.result[] | select(.zone_name == "6565.eu.org" and .name == "cfproxy.6565.eu.org") | .id'))

    for RECORD_ID in ${DNS_LIST_DEL[@]};do
        curl --location --request DELETE "https://api.cloudflare.com/client/v4/zones/${ZONE_ID_6565}/dns_records/${RECORD_ID}" \
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
        curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID_6565}/dns_records" \
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

function CF_good_cdn(){
    # 参考项目：https://github.com/cmliu/CloudFlareIPlus
    # https://github.com/cmliu/ASN2IPv4CIDRs
    ipplushtxt=IPlus.txt
    old_script=CFIPlus-new.sh
    cd ${CF_DIR} && rm -f $ipplushtxt && rm -f $old_script && rm -f ${DNS_RECORDS}
    wget ${proxygithub}https://raw.githubusercontent.com/longyinghua/proxy/master/cf-good/CFIPlus-new.sh 
    chmod +x CFIPlus-new.sh 
    # bash CFIPlus-new.sh
    bash CFIPlus-new.sh 2096 209242 #选择需要测试端口

    $CF_DIR/CloudflareST -tp 2096  -f $CF_DIR/$ipplushtxt -url $URL_SPEED #家庭软路由测试，有时候因为-tl延迟或者-sl速度都会导致测速没有结果，直接忽略速度和延迟进行测试才会有一点速度结果，跟测速url没有关系

    # ./CloudflareST -tp 2096 -url https://url-test.6565.eu.org/test -ip 89.116.250.0/24,45.94.169.0/24,167.68.11.0/24,45.131.4.0/22,194.53.53.0/24,194.152.44.0/24,199.33.230.0/23,185.193.28.0/22,154.83.22.0/23,83.118.224.0/22 -allip   #这样直接指定ip段内所有IP进行优选也是可行的

    # ./CloudflareST -tp 2096 -url https://url-test.6565.eu.org/test  -allip -sl 10   #默认使用ip.txt文件中的ip，使用-allip参数可以测试所有ip，-sl参数设置下载速度下线为10MB/s

    # $CF_DIR/CloudflareST -tp 2096 -n 500 -f $CF_DIR/$ipplushtxt -url $URL_SPEED -sl 30 -tl 140 -dn 10   #延时上线140ms，下载速度30MB/s，获取20个

    # ./CloudflareST -f ./IPlus.txt -n 500 -tp 2096 -url https://url-test.6565.eu.org/test  -sl 30 -tl 130 -dn 10

    # 删除DNS解析记录
    curl --location --request GET "https://api.cloudflare.com/client/v4/zones/${ZONE_ID_9595}/dns_records" \
    --header "X-Auth-Key: ${CF_API_KEY}" \
    --header "X-Auth-Email: ${CF_API_EMAIL}" \
    -s -o ${DNS_RECORDS}

    # 获取待删除域名goodcf.9595.eu.org的域名对应的id
    DNS_LIST_DEL=($(cat ${DNS_RECORDS} | jq -r '.result[] | select(.zone_name == "9595.eu.org" and .name == "goodcf.9595.eu.org") | .id'))

    for RECORD_ID in ${DNS_LIST_DEL[@]};do
        curl --location --request DELETE "https://api.cloudflare.com/client/v4/zones/${ZONE_ID_9595}/dns_records/${RECORD_ID}" \
        --header "X-Auth-Key: ${CF_API_KEY}" \
        --header "X-Auth-Email: ${CF_API_EMAIL}" 
    done  

    
    # 添加优选IP解析记录
    IP=$(cat $IP_RESULT | sed 1d |awk -F "," '{print $1}')

    for ip in $IP
    do
        curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID_9595}/dns_records" \
            -H "X-Auth-Email:${CF_API_EMAIL}" \
            -H "X-Auth-Key:${CF_API_KEY}" \
            -H "Content-Type:application/json" \
            --data '{"type":"A","name":"goodcf","content":"'"${ip}"'","ttl":1,"priority":10,"proxied":false}'
    done

}

CF_INSTALL # 安装优选测试服务
# CF_GET_IP  # 获取优选IP列表
# CF_PROXY_IP # 执行优选CF的反代IP测试
# CF_SPEED_TEST # 执行优选IP删选的函数
# DELETE_DNS_RECORD # 执行删除dns记录的函数
# ADD_DNS_RECORD # 执行添加dns记录的函数
CF_good_cdn # 执行优选企业保留CDN测试
