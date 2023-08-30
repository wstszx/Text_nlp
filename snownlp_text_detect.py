import re
import sys
import chardet
import pandas as pd
import os
import time
from snownlp import SnowNLP
import numpy as np

# 读取命令行参数
detect_type = int(sys.argv[1])
excel_path = sys.argv[2]

# 读取 Excel 文件
file_ext = os.path.splitext(excel_path)[1]  # 获取文件后缀名
if file_ext == ".xlsx" or file_ext == ".xlsm":
    df = pd.read_excel(excel_path, header=0, engine="openpyxl")
elif file_ext == ".xls":
    df = pd.read_excel(excel_path, header=0, engine="xlrd")
elif file_ext == ".csv":
    # 使用 chardet 库自动检测文件编码格式
    with open(excel_path, 'rb') as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']
    # print("文件路径：", excel_path, "编码：", encoding)
    # 使用 pandas 读取 csv 文件
    df = pd.read_csv(excel_path, header=0, encoding=encoding)
else:
    print("不支持的文件格式")
    exit()

# 定义列来写入情感分析结果
sentiment_col = "检测结果"

num_rows = df.shape[0]
for i, row in df.iterrows():
    combined_text = " ".join([str(row[col]) for col in df.columns if col != sentiment_col and not pd.isna(row[col])])
        
    # 使用 SnowNLP 进行情感分析
    sentiment = SnowNLP(combined_text).sentiments
    if sentiment > 0.6:
        sentiment_str = '正面'
    elif sentiment < 0.4:
        sentiment_str = '负面'
    else:
        sentiment_str = '中性'
    print(f"文本得分: {sentiment}")    
    print(f"文本内容: {combined_text}")
    print(f"文本分析结果: {sentiment_str}\n")
    
    df.loc[i, sentiment_col] = sentiment_str

# 写入情感分析结果到Excel文件
if file_ext == ".xlsx" or file_ext == ".xls":
    with pd.ExcelWriter(excel_path) as writer:
        df.to_excel(writer, index=False, header=True)
elif file_ext == ".csv":
    df.to_csv(excel_path, index=False, header=True, encoding=encoding)

print("文本分析完成！请检查结果文件 '{}'。".format(excel_path))