import akshare as ak
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification, TextClassificationPipeline, pipeline
import torch

# 全局加载 FinBERT 模型和 tokenizer
def load_finbert_pipeline():
    model_name = 'yiyanghkust/finbert-tone'
    device = 0 if torch.cuda.is_available() else -1
    finbert_pipeline = pipeline("sentiment-analysis", model=model_name, tokenizer=model_name, device=device, return_all_scores=True)
    return finbert_pipeline

# 初始化情感分析 pipeline
finbert_pipeline = load_finbert_pipeline()

# 批量分析情感
def analyze_sentiment_batch(titles):
    # 批量分析情感
    sentiment_scores = finbert_pipeline(titles)

    results = []
    for scores in sentiment_scores:
        # 打印调试信息
        # print(scores)

        # 使用label获取各类情感得分，注意标签名称的大小写
        positive_score = next((s['score'] for s in scores if s['label'].lower() == 'positive'), 0.0)
        negative_score = next((s['score'] for s in scores if s['label'].lower() == 'negative'), 0.0)
        neutral_score = next((s['score'] for s in scores if s['label'].lower() == 'neutral'), 0.0)

        # 计算情感得分，范围在 -10 到 +10
        sentiment_score = (positive_score - negative_score) * 10

        # 将得分限制在 -10 到 +10
        sentiment_score = max(min(sentiment_score, 10), -10)

        results.append(sentiment_score)

    return results

def analyze_news_sentiment():
    # 从 akshare 获取数据
    stock_info_global_cls_df = ak.stock_info_global_cls(symbol="重点")
    
    # 按标题去重，并保留第一次出现的条目
    stock_info_global_cls_df = stock_info_global_cls_df.drop_duplicates(subset="标题", keep="first")
    
    # 按发布时间排序，并选择最新的 20 条新闻
    stock_info_global_cls_df = stock_info_global_cls_df.sort_values(by="发布时间", ascending=False).head(20).reset_index(drop=True)
    
    # 只提取标题列并转换为列表
    titles = stock_info_global_cls_df['标题'].tolist()

    # 批量执行情感分析
    sentiment_results = analyze_sentiment_batch(titles)

    # 整理结果
    results = []
    for i, row in stock_info_global_cls_df.iterrows():
        title = row['标题']
        content = row['内容']
        ptime = str(row['发布日期']) + ' ' + str(row['发布时间'])
        sentiment_score = sentiment_results[i]
        
        results.append({
            '标题': title,
            '内容': content,
            '时间': ptime,
            '情感得分': round(sentiment_score, 2)
        })

    return results

