import pandas as pd
import matplotlib.pyplot as plt
import os
from tqdm import tqdm

# 获取当前脚本的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# Load the CSV file (if not already loaded)
df = pd.read_csv('Store/Transformed_data.csv')

# Convert the 'publishAt' column to datetime format (if not already done)
df['publishAt'] = pd.to_datetime(df['publishAt'], errors='coerce')

# Sort the dataframe by date
df = df.sort_values('publishAt')

# Count the number of articles per hour
df['hour'] = df['publishAt'].dt.floor('H')
article_counts = df.groupby('hour').size().reset_index(name='count')

# Create the time series plot
plt.figure(figsize=(12, 6))
plt.plot(article_counts['hour'], article_counts['count'], marker='o')
plt.title('Number of Articles Published Over Time')
plt.xlabel('Date and Time')
plt.ylabel('Number of Articles')
plt.xticks(rotation=45)
plt.tight_layout()

# Save the plot as a PNG file
output_path = os.path.join(current_dir, 'time_series_trend.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"时间序列趋势图已保存为 '{output_path}'")

# Display some statistics
print("\
Total number of articles:", len(df))
print("Average number of articles per hour:", article_counts['count'].mean())
print("Maximum number of articles in an hour:", article_counts['count'].max())
print("Minimum number of articles in an hour:", article_counts['count'].min())