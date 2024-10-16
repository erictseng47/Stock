from collections import Counter
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
import re
import jieba
import os
from wordcloud import WordCloud
from matplotlib.font_manager import FontProperties

# 获取当前脚本的路径
current_dir = os.path.dirname(os.path.abspath(__file__))



# Load the CSV file
df = pd.read_csv('Store/Transformed_data.csv')

# Function to process text
def process_text(text): 
    # Remove punctuation and convert to lowercase
    text = re.sub(r'[^\w\s]', '', str(text).lower())
    # Tokenize the text using jieba for Chinese text
    words = jieba.cut(text)
    return [word for word in words if len(word) > 1]

# Process all content and count word frequencies
word_freq = Counter()
for content in tqdm(df['content'], desc="Processing text"):
    words = process_text(content)
    word_freq.update(words)

# Get the top 20 most common words
top_words = word_freq.most_common(20)

# Create lists for words and their frequencies
words, frequencies = zip(*top_words)

# Create a bar chart
fig, ax = plt.subplots(figsize=(15, 8))
bars = ax.bar(words, frequencies)

# 添加数值标签到柱状图顶部
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:,}',
            ha='center', va='bottom')

plt.title('前20个最常见词汇', fontsize=16)
plt.xlabel('词语', fontsize=12)
plt.ylabel('频率', fontsize=12)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.tight_layout()

# 保存柱状图到当前脚本所在的文件夹
bar_chart_path = os.path.join(current_dir, 'word_frequency_chart.png')
plt.savefig(bar_chart_path, dpi=300, bbox_inches='tight')
print(f"词频统计图表已保存为 '{bar_chart_path}'")

# 创建文字云
wordcloud = WordCloud(
    width=800, 
    height=400, 
    background_color='white'
).generate_from_frequencies(word_freq)

# 显示文字云
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('词频文字云', fontsize=16, fontproperties=font_prop)

# 保存文字云到当前脚本所在的文件夹
wordcloud_path = os.path.join(current_dir, 'word_cloud.png')
plt.savefig(wordcloud_path, dpi=300, bbox_inches='tight')
print(f"词频文字云已保存为 '{wordcloud_path}'")

# Display the top 20 words and their frequencies
print("\n词频统计结果:")
for word, freq in top_words:
    print(f"{word}: {freq:,}")