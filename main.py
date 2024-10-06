from spider import CnyesNewsSpider
from logger import logger, log_start, log_end
import time
from analyze import NewsAnalyzer
import argparse

def run_spider():
    log_start()
    spider = CnyesNewsSpider()
    
    try:
        while True:
            newslist_info = spider.get_newslist_info()
            if newslist_info:
                new_news = [news for news in newslist_info if not spider.is_news_exists(news['newsId'])]
                if new_news:
                    spider.save_news_to_csv(new_news)
                    spider.save_news_to_sqlite(new_news)
                    logger.info(f"已添加 {len(new_news)} 条新闻")
                else:
                    logger.info("没有新的新闻")
            
            # 等待一段时间再次获取新闻，例如每小时获取一次
            time.sleep(3600)
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    finally:
        log_end()

def run_analysis():
    analyzer = NewsAnalyzer()
    analyzer.read_csv_file()
    analyzer.analyse_data()

def main():
    parser = argparse.ArgumentParser(description="新闻爬虫和数据分析工具")
    parser.add_argument("--analyze", action="store_true", help="运行数据分析")
    args = parser.parse_args()

    if args.analyze:
        run_analysis()
    else:
        run_spider()

if __name__ == "__main__":
    main()