#!/bin/bash
#
# Author: greedy_alpha@163.com
#
# 基于雅虎API获取股票历史数据
# 需传入要获取的股票代码、起止时间、时间周期等参数


###############################
# 参数校验
###############################

if [ $# -lt 3 ]; then
    echo "Error: Please enter correct parameters"
    exit 1
else
    code=$1
    sday=$2
    eday=$3
    if [ $# -gt 3 ]; then
        inte=$4
    else
        inte="1d"
    fi
fi


###############################
# 基础配置
###############################

HOME=$(cd "$(dirname "$0")" || exit; pwd)
cd "$HOME" || exit;

s_tms=$(date -d ${sday} +%s)
e_tms=$(date -d ${eday} +%s)

api="https://query1.finance.yahoo.com/v7/finance/download"
args="events=history&includeAdjustedClose=true"

data_path=../../data
file_name=${code}-${sday}-${eday}-${inte}.csv

###############################
# 函数实现
###############################

get_data() {
    url="${api}/${code}?period1=${s_tms}&period2=${e_tms}&interval=${inte}&${args}"
    curl -k ${url} > ${data_path}/${file_name}
}


###############################
# 数据处理
###############################

main() {
    get_data
}

main


