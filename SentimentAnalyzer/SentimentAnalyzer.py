import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup
from textblob import TextBlob
from tqdm import tqdm
import os
import matplotlib.font_manager as fm
import platform
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

class SentimentAnalyzer:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.df = None
        self.chinese_font = self.get_font()
        plt.rcParams['axes.unicode_minus'] = False

    @staticmethod
    def get_font():
        system = platform.system()
        font_paths = {
            "Windows": r"C:\Windows\Fonts\SimHei.ttf",
            "Darwin": "/System/Library/Fonts/PingFang.ttc",  # macOS
            "Linux": "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
        }
        try:
            return fm.FontProperties(fname=font_paths.get(system, ''))
        except:
            print("警告：无法加载指定字体，使用系统默认字体。")
            return fm.FontProperties()

    @staticmethod
    def clean_html(text):
        return BeautifulSoup(str(text), "html.parser").get_text()

    @staticmethod
    def analyze_sentiment(text):
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        if polarity > 0:
            return {"label": "正面", "score": polarity}
        elif polarity < 0:
            return {"label": "负面", "score": -polarity}
        else:
            return {"label": "中性", "score": 0}

    def process_chunk(self, chunk):
        return [self.analyze_sentiment(self.clean_html(text)) for text in chunk]

    def load_data(self):
        print("正在读取数据...")
        try:
            self.df = pd.read_csv(self.csv_path)
        except FileNotFoundError:
            print(f"错误: 找不到文件 '{self.csv_path}'")
            print("请确保 CSV 文件位于正确的位置")
            sys.exit(1)

    def perform_sentiment_analysis(self):
        print("正在进行情感分析...")
        chunk_size = 1000  # 调整此值以平衡内存使用和性能
        chunks = [self.df['content'].iloc[i:i+chunk_size] for i in range(0, len(self.df), chunk_size)]

        sentiments = []
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(self.process_chunk, chunk) for chunk in chunks]
            for future in tqdm(as_completed(futures), total=len(futures)):
                sentiments.extend(future.result())

        self.df['sentiment_label'] = [s['label'] for s in sentiments]
        self.df['sentiment_score'] = [s['score'] for s in sentiments]

    def display_results(self):
        print("\n情感分析结果的前几行:")
        print(self.df[['content', 'sentiment_label', 'sentiment_score']].head())

    def plot_sentiment_distribution(self, output_dir):
        plt.figure(figsize=(12, 6))
        sns.countplot(y='categoryName', hue='sentiment_label', data=self.df, order=self.df['categoryName'].value_counts().index)
        plt.title('新闻类别的情感分布', fontproperties=self.chinese_font)
        plt.xlabel('数量', fontproperties=self.chinese_font)
        plt.ylabel('类别名称', fontproperties=self.chinese_font)
        plt.legend(title='情感', prop=self.chinese_font)

        plt.gca().set_yticklabels(plt.gca().get_yticklabels(), fontproperties=self.chinese_font)

        plt.tight_layout()

        os.makedirs(output_dir, exist_ok=True)
        plot_path = os.path.join(output_dir, 'sentiment_distribution.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"情感分布图已保存为 '{plot_path}'")
        plt.close()

    def save_results(self, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'cnyes_news_with_sentiment.csv')
        self.df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"结果已保存到 '{output_path}'")

    def run_analysis(self, output_dir):
        self.load_data()
        self.perform_sentiment_analysis()
        self.display_results()
        self.plot_sentiment_distribution(output_dir)
        self.save_results(output_dir)

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(os.path.dirname(current_dir), 'cnyes_news.csv')
    output_dir = os.path.join(current_dir, 'output')

    analyzer = SentimentAnalyzer(csv_path)
    analyzer.run_analysis(output_dir)

if __name__ == "__main__":
    main()