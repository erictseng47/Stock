import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional
from matplotlib.font_manager import FontProperties
import platform
import os
import logging

class NewsAnalyzer:
    def __init__(self, file_path: str = 'cnyes_news.csv'):
        self.file_path = file_path
        self.df = None
        self.font = self.get_font()
        plt.rcParams['axes.unicode_minus'] = False
        sns.set(style="whitegrid")
        self.setup_logging()

    def setup_logging(self):
        log_dir = 'analysis_results'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        logging.basicConfig(filename=os.path.join(log_dir, 'analysis.log'),
                            level=logging.INFO,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_font():
        """獲取適合當前系統的中文字體"""
        system = platform.system()
        font_paths = {
            "Windows": r'C:\Windows\Fonts\msjh.ttc',
            "Darwin": '/System/Library/Fonts/PingFang.ttc',  # macOS
            "Linux": '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
        }
        try:
            return FontProperties(fname=font_paths.get(system, ''), size=10)
        except:
            logging.warning("無法加載指定字體，使用系統默認字體")
            return FontProperties(size=10)

    def read_csv_file(self) -> Optional[pd.DataFrame]:
        """讀取 CSV 文件並返回 DataFrame"""
        try:
            self.df = pd.read_csv(self.file_path)
            return self.df
        except FileNotFoundError:
            logging.error(f"錯誤: 找不到文件 '{self.file_path}'")
        except pd.errors.EmptyDataError:
            logging.error(f"錯誤: 文件 '{self.file_path}' 是空的")
        except pd.errors.ParserError:
            logging.error(f"錯誤: 無法解析文件 '{self.file_path}'")
        return None

    def preprocess_data(self):
        """預處理數據"""
        self.df['publishAt'] = pd.to_datetime(self.df['publishAt'])
        for col in ['title', 'content', 'summary']:
            self.df[f'{col}_length'] = self.df[col].str.len()

    def plot_category_distribution(self, ax):
        """繪製新聞類別分佈圖"""
        top_categories = self.df['categoryName'].value_counts().nlargest(10).index
        sns.countplot(y='categoryName', data=self.df[self.df['categoryName'].isin(top_categories)], 
                      order=top_categories, ax=ax)
        ax.set_title('前10新聞類別分佈', fontsize=12, fontproperties=self.font)
        ax.set_xlabel('數量', fontsize=10, fontproperties=self.font)
        ax.set_ylabel('類別名稱', fontsize=10, fontproperties=self.font)
        ax.tick_params(axis='y', labelsize=8)
        for label in ax.get_yticklabels():
            label.set_fontproperties(self.font)

    def plot_text_length_distribution(self, ax):
        """繪製文本長度分佈圖"""
        sns.histplot(self.df['title_length'], bins=20, kde=True, color='blue', label='標題長度', ax=ax)
        sns.histplot(self.df['summary_length'], bins=20, kde=True, color='red', label='摘要長度', ax=ax)
        ax.set_title('文本長度分佈', fontsize=12, fontproperties=self.font)
        ax.set_xlabel('文本長度', fontsize=10, fontproperties=self.font)
        ax.set_ylabel('頻率', fontsize=10, fontproperties=self.font)
        ax.legend(prop=self.font, fontsize=8)

    def plot_publish_date_distribution(self, ax):
        """繪製發布日期分佈圖"""
        self.df['publishAt'].hist(bins=20, color='purple', ax=ax)
        ax.set_title('發布日期分佈', fontsize=12, fontproperties=self.font)
        ax.set_xlabel('發布日期', fontsize=10, fontproperties=self.font)
        ax.set_ylabel('頻率', fontsize=10, fontproperties=self.font)
        ax.tick_params(axis='x', rotation=45, labelsize=8)

    def plot_content_length_distribution(self, ax):
        """繪製內容長度箱型圖"""
        top_categories = self.df['categoryName'].value_counts().nlargest(5).index
        sns.boxplot(x='categoryName', y='content_length', data=self.df[self.df['categoryName'].isin(top_categories)], ax=ax)
        ax.set_title('前5類別內容長度分佈', fontsize=12, fontproperties=self.font)
        ax.set_xlabel('類別名稱', fontsize=10, fontproperties=self.font)
        ax.set_ylabel('內容長度', fontsize=10, fontproperties=self.font)
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        for label in ax.get_xticklabels():
            label.set_fontproperties(self.font)

    def plot_all_distributions(self):
        """繪製所有分佈圖"""
        fig, axs = plt.subplots(2, 2, figsize=(16, 16))
        fig.suptitle('新聞數據分析', fontsize=16, fontproperties=self.font)

        self.plot_category_distribution(axs[0, 0])
        self.plot_text_length_distribution(axs[0, 1])
        self.plot_publish_date_distribution(axs[1, 0])
        self.plot_content_length_distribution(axs[1, 1])

        plt.tight_layout()
        
        save_path = 'analysis_results/news_analysis.png'
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logging.info(f"圖表已保存至 '{save_path}'")
        
        plt.show()

    def analyse_data(self):
        """分析數據並輸出結果"""
        if self.df is not None:
            logging.info("數據分析開始:")
            logging.info(f"總行數: {len(self.df)}")
            logging.info(f"列名: {', '.join(self.df.columns)}")
            logging.info("\n前5行數據:\n%s", self.df.head().to_string())
            logging.info("\n基本統計信息:\n%s", self.df.describe(include='all').to_string())
            
            self.preprocess_data()
            self.plot_all_distributions()
        else:
            logging.error("無法進行數據分析,因為 DataFrame 為空")

def main():
    analyzer = NewsAnalyzer()
    analyzer.read_csv_file()
    analyzer.analyse_data()

if __name__ == "__main__":
    main()