from typing import List, Dict, Optional
from Logger import setup_logger
from html import unescape

import csv
import requests
import time
import os
import sqlite3
import json
import pandas as pd
import re

# 设置logger
logger = setup_logger()

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))

class ETL:
    BASE_URL = "https://api.cnyes.com/media/api/v1/newslist/category/headline"
    HEADERS = {
        'Origin': 'https://news.cnyes.com/',
        'Referer': 'https://news.cnyes.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

    def __init__(self):
        self.ensure_store_directory()
        self.db_path = os.path.join(project_root, 'Store', 'Transformed_data.db')
        logger.info(f"数据库路径设置为：{self.db_path}")

    def ensure_store_directory(self):
        """确保Store目录存在"""
        store_path = os.path.join(project_root, 'Store')
        if not os.path.exists(store_path):
            os.makedirs(store_path)
            logger.info(f"创建Store目录：{store_path}")

    def Extract(self, page: int = 1, limit: int = 30) -> Optional[List[Dict]]:
        """提取：从API获取新闻列表并保存原始数据"""
        params = {'page': page, 'limit': limit}
        try:
            response = requests.get(self.BASE_URL, headers=self.HEADERS, params=params)
            response.raise_for_status()
            data = response.json()['items']['data']
            
            # 保存原始数据到CSV
            raw_data_path = os.path.join(project_root, 'Store', 'Raw_data.csv')
            df = pd.DataFrame(data)
            df.to_csv(raw_data_path, index=False, mode='a', header=not os.path.exists(raw_data_path))
            logger.info(f"原始数据已保存到 {raw_data_path}")
            
            return data
        except requests.RequestException as e:
            logger.error(f'提取数据失败: {e}')
            return None

    def Clean_text(self, text: str) -> str:
        """清理文本，移除HTML标签和特殊字符"""
        # 解码HTML实体
        text = unescape(text)
        # 移除HTML标签，包括 </p>
        text = re.sub(r'<[^>]+>', '', text)
        # 移除特殊字符，保留基本标点符号
        text = re.sub(r'[^\w\s.,!?;:，。！？；：]', '', text)
        return text.strip()

    def Transform(self, newslist_info: List[Dict]) -> List[Dict]:
        """转换：处理和清洗数据"""
        transformed_data = []
        for news in newslist_info:
            transformed_news = {
                'newsId': news.get('newsId'),
                'url': f"https://news.cnyes.com/news/id/{news.get('newsId')}",
                'title': self.Clean_text(news.get('title', '')),
                'content': self.Clean_text(news.get('content', '')),
                'summary': self.Clean_text(news.get('summary', '')),
                'keyword': self._process_field(news.get('keyword')),
                'publishAt': self._process_field(news.get('publishAt')),
                'categoryName': self.Clean_text(news.get('categoryName', '')),
                'categoryId': news.get('categoryId')
            }
            transformed_data.append(transformed_news)
        return transformed_data

    def Load_to_csv(self, transformed_data: List[Dict], filename: str) -> None:
        """加载：将转换后的数据保存到CSV文件"""
        fieldnames = ['newsId', 'url', 'title', 'content', 'summary', 'keyword', 'publishAt', 'categoryName', 'categoryId']
        
        file_exists = os.path.isfile(filename)
        
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for news in transformed_data:
                writer.writerow(news)
        
        logger.info(f"已将 {len(transformed_data)} 条新闻加载到 {filename}")

    def Load_to_sqlite(self, transformed_data: List[Dict]) -> None:
        """加载：将转换后的数据保存到SQLite数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 确保数据库表存在
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS news (
                        newsId INTEGER PRIMARY KEY,
                        url TEXT,
                        title TEXT,
                        content TEXT,
                        summary TEXT,
                        keyword TEXT,
                        publishAt TEXT,
                        categoryName TEXT,
                        categoryId INTEGER
                    )
                ''')
                for news in transformed_data:
                    cursor.execute('''
                        INSERT OR REPLACE INTO news 
                        (newsId, url, title, content, summary, keyword, publishAt, categoryName, categoryId)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', tuple(news.values()))
            logger.info(f"成功将 {len(transformed_data)} 条新闻加载到 SQLite 数据库 {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"数据库操作失败：{str(e)}")
            raise

    def _process_field(self, value):
        """处理字段值"""
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False)
        elif isinstance(value, (int, float)) and len(str(value)) == 10:  # 假设是 UNIX 时间戳
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(value))
        return str(value)

    def is_news_exists(self, news_id: int) -> bool:
        """检查新闻是否已存在于数据库中"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM news WHERE newsId = ?", (news_id,))
            return cursor.fetchone() is not None

    def run_etl(self, page: int = 1, limit: int = 30, csv_filename: str = 'Transformed_data.csv'):
        """运行完整的ETL流程"""
        # 提取
        raw_data = self.Extract(page, limit)
        if not raw_data:
            logger.error("提取数据失败，ETL流程终止")
            return

        # 转换
        transformed_data = self.Transform(raw_data)

        # 加载
        store_path = os.path.join(project_root, 'Store')
        csv_file_path = os.path.join(store_path, csv_filename)
        self.Load_to_csv(transformed_data, csv_file_path)
        self.Load_to_sqlite(transformed_data)

        logger.info("ETL流程完成")

# 使用示例
if __name__ == "__main__":
    etl = ETL()
    etl.run_etl()
