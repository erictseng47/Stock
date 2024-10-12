from ETL import CnyesNewsETL
from Logger import setup_logger, log_start, log_end
from analyze import NewsAnalyzer
import argparse
import os

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))

# 设置logger
logger = setup_logger()

def ensure_directories():
    etl = CnyesNewsETL()
    etl.ensure_store_directory()
    os.makedirs(os.path.join(project_root, 'output'), exist_ok=True)

def run_etl_and_analyze():
    log_start()
    ensure_directories()
    etl = CnyesNewsETL()
    analyzer = NewsAnalyzer()
    
    try:
        csv_file_path = os.path.join(project_root, 'Store', 'cnyes_news.csv')
        etl.run_etl(csv_filename='cnyes_news.csv')
        
        # 执行数据分析并更新仪表板
        analyzer.read_csv_file(csv_file_path)
        analyzer.analyse_data()
        logger.info("数据分析完成，仪表板已更新")
    except Exception as e:
        logger.error(f"运行过程中发生错误: {str(e)}")
    finally:
        log_end()

def main():
    parser = argparse.ArgumentParser(description="新闻ETL和数据分析工具")
    parser.add_argument("--analyze", action="store_true", help="仅运行数据分析")
    args = parser.parse_args()

    if args.analyze:
        analyzer = NewsAnalyzer()
        csv_file_path = os.path.join(project_root, 'Store', 'cnyes_news.csv')
        analyzer.read_csv_file(csv_file_path)
        analyzer.analyse_data()
    else:
        run_etl_and_analyze()

if __name__ == "__main__":
    main()
