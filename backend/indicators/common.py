import numpy as np
import pandas as pd
import json

def repair_dataframe_data(df):
    df = df.fillna(0).replace([np.inf, -np.inf], 0)
    return df

def convert_value(val):
    """
    检查值的类型并转换为原生 Python 类型
    """
    if isinstance(val, (np.generic, np.bool_)):
        return val.item()  # 转换 numpy 数据类型为原生类型
    elif isinstance(val, pd.Timestamp):
        return val.strftime('%Y-%m-%d %H:%M:%S')  # 转换为标准时间格式
    elif isinstance(val, np.datetime64):
        timestamp = pd.Timestamp(val)  # 转为 pandas 时间戳
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(val, (int, float, np.float64)):  # 处理数字类型
        return float(val)  # 强制转换为原生 Python 类型（包括 np.float64）
    elif isinstance(val, np.ndarray):
        return val.tolist()  # 转换 numpy 数组为 Python 列表
    return val

def NP2Dict(df_or_series):
    """
    将 pandas DataFrame 或 Series 转换为字典，并自动处理类型转换。
    """
    # 使用 pandas 的 to_json 方法将 DataFrame 或 Series 转换为 JSON 字符串
    json_str = df_or_series.to_json(orient='records')  # 'records' 会把每行数据转换为一个字典
    # 将 JSON 字符串解析为 Python 字典
    dict_result = json.loads(json_str)
    
    # 遍历每个字典记录
    for i, record in enumerate(dict_result):
        # 如果 record 是字典（这一行应该是字典），则逐个转换值
        if isinstance(record, dict):
            for key, value in record.items():
                record[key] = convert_value(value)
        else:
            # 如果 record 不是字典，直接转换
            dict_result[i] = convert_value(record)
    
    return dict_result