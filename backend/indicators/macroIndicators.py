import re
import pendulum
from collections import defaultdict
import requests
import json
from config.GlobalConfig import AKTOOLS_BASE_URL
from config.cached_akshare_request import cached_akshare_request
import os


# 定义全局配置字典
INDICATORS = {}

# 加载 JSON 配置文件
def load_indicators():
    global INDICATORS
    # 获取当前文件的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建 config 文件的绝对路径
    config_path = os.path.join(current_dir, '..', 'config', 'indicators.json')
    
    with open(config_path, 'r', encoding='utf-8') as json_file:
        INDICATORS = json.load(json_file)


# 通用方法：从缓存获取数据，若不存在则调用 AkTools API
# @cached(ttl=CACHE_TTL, serializer=JsonSerializer())
def get_data_from_cache_or_api(indicator: str):

    result = []
    api_url = f"{AKTOOLS_BASE_URL}/{indicator}"
    aktools_response = requests.get(api_url, timeout=180)
    aktools_response.raise_for_status()
    data = aktools_response.json()
    if data:
        result = process_indicator_data(INDICATORS[indicator], data)
    return result

def add_date_separators(date_string):
    if date_string.isdigit():
        if len(date_string) == 6:  # 处理 YYYYMM 形式
            return f"{date_string[:4]}-{date_string[4:6]}"
        elif len(date_string) == 8:  # 处理 YYYYMMDD 形式
            return f"{date_string[:4]}-{date_string[4:6]}-{date_string[6:8]}"
    return date_string


def process_indicator_data(indicator, data):
    sdl = process_time_format(data, indicator['xField'], indicator['timeFormat'])

    return aggregate_data(sdl, indicator['xField'], indicator['yFields'])


def smart_date_parser(date_string, output_format):
    # 1. 将所有中文字符替换为 `-`
    clean_date_string = re.sub(r'[\u4e00-\u9fff]', '-', date_string)

    # 2. 删除空格、T或.之后的内容，包括这个字符
    clean_date_string = re.split(r'[ T.]', clean_date_string)[0]

    # 3. 去除左右两端所有非数字的字符
    clean_date_string = re.sub(r'^[^\d]+|[^\d]+$', '', clean_date_string)

    # 4. 将中间连续 2 个或以上的 `-` 替换为一个 `-`
    clean_date_string = re.sub(r'-{2,}', '-', clean_date_string)

    clean_date_string = add_date_separators(clean_date_string)

    parsed_date = pendulum.parse(clean_date_string, strict=False)
    fd = parsed_date.format(output_format)
    return fd


def process_time_format(data: list, time_key: str, date_format: str) -> list:
    for item in data:
        if time_key in item:
            try:
                item[time_key] = smart_date_parser(item[time_key], date_format)
            except ValueError:
                pass
    sorted_data = sorted(data, key=lambda x: pendulum.parse(x[time_key]))
    return sorted_data


def aggregate_data(data: list, x_field: str, y_fields: list) -> dict:
    """对格式化后的数据进行聚合，生成适用于 ECharts 的数据格式"""
    aggregated = defaultdict(lambda: defaultdict(float))

    # 聚合数据
    for item in data:
        x_value = item[x_field]
        if x_value is None:
            continue

        # 累加 y_fields 中的值
        for y_field in y_fields:
            if y_field in item and isinstance(item[y_field], (int, float)):
                aggregated[x_value][y_field] += item[y_field]

    # 准备 ECharts 格式的数据
    x_data = list(aggregated.keys())
    series_data = {y_field: [] for y_field in y_fields}

    # 构建 ECharts 格式的 series 数据
    for x_value in x_data:
        for y_field in y_fields:
            series_data[y_field].append(aggregated[x_value][y_field])

    # 返回适合 ECharts 的数据格式
    return {
        "xData": x_data,
        "series": [
            {
                "name": y_field,
                "type": "line",
                "coordinateSystem": 'cartesian2d',
                "data": series_data[y_field]
            }
            for y_field in y_fields
        ]
    }
