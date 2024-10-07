from spider import CnyesNewsSpider
from logger import logger, log_start, log_end
from analyze import NewsAnalyzer
import argparse
import os
import sqlite3

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))

def ensure_directories():
    os.makedirs(os.path.join(project_root, 'Store'), exist_ok=True)
    os.makedirs(os.path.join(project_root, 'output'), exist_ok=True)

def ensure_database():
    db_path = os.path.join(project_root, 'cnyes_news.db')
    logger.info(f"尝试打开数据库文件：{db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # 检查表是否存在，如果不存在则创建
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
            categoryId TEXT
        )
        ''')
        conn.commit()
        conn.close()
        logger.info("数据库连接成功并确保表存在")
    except sqlite3.Error as e:
        logger.error(f"数据库操作失败：{str(e)}")
        raise

def run_spider_and_analyze():
    log_start()
    ensure_directories()
    ensure_database()
    spider = CnyesNewsSpider()
    analyzer = NewsAnalyzer()
    
    try:
        newslist_info = spider.get_newslist_info()
        if newslist_info:
            new_news = [news for news in newslist_info if not spider.is_news_exists(news['newsId'])]
            if new_news:
                csv_file_path = os.path.join(project_root, 'cnyes_news.csv')
                spider.save_news_to_csv(new_news, csv_file_path)
                spider.save_news_to_sqlite(new_news)
                logger.info(f"已添加 {len(new_news)} 條新聞")
                
                # 執行數據分析並更新儀表板
                analyzer.read_csv_file(csv_file_path)
                analyzer.analyse_data()
                logger.info("數據分析完成，儀表板已更新")
            else:
                logger.info("沒有新的新聞")
        else:
            logger.info("未獲取到新聞列表信息")
    except Exception as e:
        logger.error(f"運行過程中發生錯誤: {str(e)}")
    finally:
        log_end()

def main():
    parser = argparse.ArgumentParser(description="新聞爬蟲和數據分析工具")
    parser.add_argument("--analyze", action="store_true", help="僅運行數據分析")
    args = parser.parse_args()

    if args.analyze:
        analyzer = NewsAnalyzer()
        csv_file_path = os.path.join(project_root, 'cnyes_news.csv')
        analyzer.read_csv_file(csv_file_path)
        analyzer.analyse_data()
    else:
        run_spider_and_analyze()

if __name__ == "__main__":
    main()