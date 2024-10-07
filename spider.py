import csv
import requests
import time
import os
from typing import List, Dict, Optional
import sqlite3
import json
from logger import logger

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))

class CnyesNewsSpider:
    BASE_URL = "https://api.cnyes.com/media/api/v1/newslist/category/headline"
    HEADERS = {
        'Origin': 'https://news.cnyes.com/',
        'Referer': 'https://news.cnyes.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

    def __init__(self):
        self.db_path = os.path.join(project_root, 'cnyes_news.db')
        logger.info(f"数据库路径设置为：{self.db_path}")

    def get_newslist_info(self, page: int = 1, limit: int = 30) -> Optional[List[Dict]]:
        """获取新闻列表"""
        params = {'page': page, 'limit': limit}
        try:
            response = requests.get(self.BASE_URL, headers=self.HEADERS, params=params)
            response.raise_for_status()
            return response.json()['items']['data']
        except requests.RequestException as e:
            logger.error(f'请求失败: {e}')
            return None

    def save_news_to_csv(self, newslist_info: List[Dict], filename: str) -> None:
        """将新闻列表追加到 CSV 文件"""
        fieldnames = ['newsId', 'url', 'title', 'content', 'summary', 'keyword', 'publishAt', 'categoryName', 'categoryId']
        
        file_exists = os.path.isfile(filename)
        
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for news in newslist_info:
                news['url'] = f"https://news.cnyes.com/news/id/{news['newsId']}"
                writer.writerow({field: self._process_field(news.get(field, '')) for field in fieldnames})
        
        logger.info(f"已将 {len(newslist_info)} 条新闻追加到 {filename}")

    def save_news_to_sqlite(self, newslist_info: List[Dict]) -> None:
        """将新闻列表存储到 SQLite 数据库"""
        logger.info(f"尝试连接数据库：{self.db_path}")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for news in newslist_info:
                    news['url'] = f"https://news.cnyes.com/news/id/{news['newsId']}"
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO news 
                        (newsId, url, title, content, summary, keyword, publishAt, categoryName, categoryId)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', tuple(self._process_field(news.get(field, '')) for field in [
                        'newsId', 'url', 'title', 'content', 'summary', 'keyword', 'publishAt', 'categoryName', 'categoryId'
                    ]))
            logger.info(f"成功将 {len(newslist_info)} 条新闻存储到 SQLite 数据库 {self.db_path}")
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