import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional
from matplotlib.font_manager import FontProperties
import platform
import os
import logging
from bs4 import BeautifulSoup

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
        """获取适合当前系统的中文字体"""
        system = platform.system()
        font_paths = {
            "Windows": r'C:\Windows\Fonts\msjh.ttc',
            "Darwin": '/System/Library/Fonts/PingFang.ttc',  # macOS
            "Linux": '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
        }
        try:
            return FontProperties(fname=font_paths.get(system, ''), size=10)
        except:
            logging.warning("无法加载指定字体，使用系统默认字体")
            return FontProperties(size=10)

    def read_csv_file(self) -> Optional[pd.DataFrame]:
        """读取 CSV 文件并返回 DataFrame"""
        try:
            self.df = pd.read_csv(self.file_path)
            return self.df
        except FileNotFoundError:
            logging.error(f"错误: 找不到文件 '{self.file_path}'")
        except pd.errors.EmptyDataError:
            logging.error(f"错误: 文件 '{self.file_path}' 是空的")
        except pd.errors.ParserError:
            logging.error(f"错误: 无法解析文件 '{self.file_path}'")
        return None

    def preprocess_data(self):
        """预处理数据"""
        self.df['publishAt'] = pd.to_datetime(self.df['publishAt'])
        for col in ['title', 'content', 'summary']:
            self.df[f'{col}_length'] = self.df[col].str.len()
        
        # Clean the content column
        self.df['cleaned_content'] = self.df['content'].apply(lambda x: BeautifulSoup(x, "html.parser").get_text())

    def plot_category_distribution(self, ax):
        """绘制新闻类别分布图"""
        top_categories = self.df['categoryName'].value_counts().nlargest(10).index
        sns.countplot(y='categoryName', data=self.df[self.df['categoryName'].isin(top_categories)], 
                      order=top_categories, ax=ax)
        ax.set_title('前10新闻类别分布', fontsize=12, fontproperties=self.font)
        ax.set_xlabel('数量', fontsize=10, fontproperties=self.font)
        ax.set_ylabel('类别名称', fontsize=10, fontproperties=self.font)
        ax.tick_params(axis='y', labelsize=8)
        for label in ax.get_yticklabels():
            label.set_fontproperties(self.font)

    def plot_text_length_distribution(self, ax):
        """绘制文本长度分布图"""
        sns.histplot(self.df['title_length'], bins=20, kde=True, color='blue', label='标题长度', ax=ax)
        sns.histplot(self.df['summary_length'], bins=20, kde=True, color='red', label='摘要长度', ax=ax)
        ax.set_title('文本长度分布', fontsize=12, fontproperties=self.font)
        ax.set_xlabel('文本长度', fontsize=10, fontproperties=self.font)
        ax.set_ylabel('频率', fontsize=10, fontproperties=self.font)
        ax.legend(prop=self.font, fontsize=8)

    def plot_publish_date_distribution(self, ax):
        """绘制发布日期分布图"""
        self.df['publishAt'].hist(bins=20, color='purple', ax=ax)
        ax.set_title('发布日期分布', fontsize=12, fontproperties=self.font)
        ax.set_xlabel('发布日期', fontsize=10, fontproperties=self.font)
        ax.set_ylabel('频率', fontsize=10, fontproperties=self.font)
        ax.tick_params(axis='x', rotation=45, labelsize=8)

    def plot_content_length_distribution(self, ax):
        """绘制内容长度箱型图"""
        top_categories = self.df['categoryName'].value_counts().nlargest(5).index
        sns.boxplot(x='categoryName', y='content_length', data=self.df[self.df['categoryName'].isin(top_categories)], ax=ax)
        ax.set_title('前5类别内容长度分布', fontsize=12, fontproperties=self.font)
        ax.set_xlabel('类别名称', fontsize=10, fontproperties=self.font)
        ax.set_ylabel('内容长度', fontsize=10, fontproperties=self.font)
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        for label in ax.get_xticklabels():
            label.set_fontproperties(self.font)

    def plot_all_distributions(self):
        """绘制所有分布图"""
        fig, axs = plt.subplots(2, 2, figsize=(16, 16))
        fig.suptitle('新闻数据分析', fontsize=16, fontproperties=self.font)

        self.plot_category_distribution(axs[0, 0])
        self.plot_text_length_distribution(axs[0, 1])
        self.plot_publish_date_distribution(axs[1, 0])
        self.plot_content_length_distribution(axs[1, 1])

        plt.tight_layout()
        
        save_path = 'analysis_results/news_analysis.png'
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logging.info(f"图表已保存至 '{save_path}'")
        
        plt.show()

    def analyse_data(self):
        """分析数据并输出结果"""
        if self.df is not None:
            logging.info("数据分析开始:")
            logging.info(f"总行数: {len(self.df)}")
            logging.info(f"列名: {', '.join(self.df.columns)}")
            logging.info("\n前5行数据:\n%s", self.df.head().to_string())
            logging.info("\n基本统计信息:\n%s", self.df.describe(include='all').to_string())
            
            self.preprocess_data()
            self.plot_all_distributions()
        else:
            logging.error("无法进行数据分析,因为 DataFrame 为空")

def main():
    analyzer = NewsAnalyzer()
    analyzer.read_csv_file()
    analyzer.analyse_data()

if __name__ == "__main__":
    main()