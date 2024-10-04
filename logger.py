import logging
import os

def setup_logger(log_file_name='spider.log'):
    # 獲取當前腳本的目錄
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 設置日誌文件路徑
    log_file_path = os.path.join(current_dir, log_file_name)
    
    # 配置日誌
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler(log_file_path),
                            logging.StreamHandler()
                        ])
    
    return logging.getLogger()

# 創建全局日誌對象
logger = setup_logger()

def log_start():
    logger.info("開始執行爬蟲程序<START>")

def log_end():
    logger.info("爬蟲程序執行完成<END>")