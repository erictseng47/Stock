import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os


current_dir = os.path.dirname(os.path.abspath(__file__))

# Load the data
df = pd.read_csv('Store/Transformed_data.csv')

# Select numeric columns for correlation
numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns

# Calculate the correlation matrix
correlation_matrix = df[numeric_columns].corr()

print("Correlation matrix calculated.")
print("Shape of the correlation matrix:", correlation_matrix.shape)
print("\
First few rows of the correlation matrix:")
print(correlation_matrix.head())

# Create a heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0)
plt.title('Correlation Heatmap')
plt.tight_layout()

# Save the heatmap
output_path = os.path.join(current_dir, 'time_series_trend.png')
plt.savefig(output_path)
print("Correlation heatmap has been saved as 'correlation_heatmap.png'")

# Display the heatmap
plt.show()