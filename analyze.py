import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional
from matplotlib.font_manager import FontProperties
import platform
import os
from bs4 import BeautifulSoup
from Logger import setup_logger, log_start, log_end

class NewsAnalyzer:
    def __init__(self):
        self.data = None
        self.logger = setup_logger('NewsAnalyzer')
        self.font = self.get_font()

    def read_csv_file(self, file_path):
        try:
            self.data = pd.read_csv(file_path)
            self.logger.info(f"成功读取 CSV 文件：{file_path}")
        except Exception as e:
            self.logger.error(f"读取 CSV 文件时出错：{str(e)}")
            raise

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
            return FontProperties(size=10)

    def preprocess_data(self):
        """预处理数据"""
        self.data['publishAt'] = pd.to_datetime(self.data['publishAt'])
        for col in ['title', 'content', 'summary']:
            self.data[f'{col}_length'] = self.data[col].str.len()
        
        # Clean the content column
        self.data['cleaned_content'] = self.data['content'].apply(lambda x: BeautifulSoup(x, "html.parser").get_text())

    def plot_category_distribution(self, ax):
        """绘制新闻类别分布图"""
        top_categories = self.data['categoryName'].value_counts().nlargest(10).index
        sns.countplot(y='categoryName', data=self.data[self.data['categoryName'].isin(top_categories)], 
                      order=top_categories, ax=ax)
        ax.set_title('前10新闻类别分布', fontsize=12, fontproperties=self.font)
        ax.set_xlabel('数量', fontsize=10, fontproperties=self.font)
        ax.set_ylabel('类别名称', fontsize=10, fontproperties=self.font)
        ax.tick_params(axis='y', labelsize=8)
        for label in ax.get_yticklabels():
            label.set_fontproperties(self.font)

    def plot_text_length_distribution(self, ax):
        """绘制文本长度分布图"""
        sns.histplot(self.data['title_length'], bins=20, kde=True, color='blue', label='标题长度', ax=ax)
        sns.histplot(self.data['summary_length'], bins=20, kde=True, color='red', label='摘要长度', ax=ax)
        ax.set_title('文本长度分布', fontsize=12, fontproperties=self.font)
        ax.set_xlabel('文本长度', fontsize=10, fontproperties=self.font)
        ax.set_ylabel('频率', fontsize=10, fontproperties=self.font)
        ax.legend(prop=self.font, fontsize=8)

    def plot_publish_date_distribution(self, ax):
        """绘制发布日期分布图"""
        self.data['publishAt'].hist(bins=20, color='purple', ax=ax)
        ax.set_title('发布日期分布', fontsize=12, fontproperties=self.font)
        ax.set_xlabel('发布日期', fontsize=10, fontproperties=self.font)
        ax.set_ylabel('频率', fontsize=10, fontproperties=self.font)
        ax.tick_params(axis='x', rotation=45, labelsize=8)

    def plot_content_length_distribution(self, ax):
        """绘制内容长度箱型图"""
        top_categories = self.data['categoryName'].value_counts().nlargest(5).index
        sns.boxplot(x='categoryName', y='content_length', data=self.data[self.data['categoryName'].isin(top_categories)], ax=ax)
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
        
        save_path = 'output/DashBoard.png'
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        self.logger.info(f"图表已保存至 '{save_path}'")
        
        plt.show()

    def analyse_data(self):
        """分析数据并输出结果"""
        if self.data is not None:
            self.logger.info("数据分析开始:")
            self.logger.info(f"总行数: {len(self.data)}")
            self.logger.info(f"列名: {', '.join(self.data.columns)}")
            self.logger.info(f"前5行数据:\n{self.data.head().to_string()}")
            self.logger.info(f"基本统计信息:\n{self.data.describe(include='all').to_string()}")
            
            self.preprocess_data()
            self.plot_all_distributions()
        else:
            self.logger.error("无法进行数据分析,因为 DataFrame 为空")

def main():
    analyzer = NewsAnalyzer()
    analyzer.read_csv_file('Store/Transformed_data.csv')
    analyzer.analyse_data()

if __name__ == "__main__":
    main()