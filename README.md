# 股票新闻ETL和数据分析工具

这是一个用于股票新闻数据的ETL(提取、转换、加载)和分析的Python项目。该工具可以处理原始新闻数据,进行情感分析,并生成可视化仪表板。

### 运行程序

1. 完整ETL和分析流程:
   
   这将执行数据提取、转换、加载,然后进行分析并更新仪表板。
   ```
   python Main.py
   ```

2. 仅运行数据分析:
   
   如果您已经有了转换后的数据(`Transformed_data.csv`在`Store`目录中),可以使用此选项只进行分析。
   ```
   python Main.py --analyze
   ```

### 查看结果

- ETL处理后的数据将保存为 `Store/Transformed_data.csv`
- 分析结果和可视化输出将保存在 `output` 目录中

### 日志

- 程序运行日志将被记录,您可以查看日志文件了解详细的执行过程和可能的错误信息

### 自定义配置

- 如需修改数据处理或分析参数,请编辑相应的Python文件:
  - `ETL.py`: 调整ETL流程
  - `analyze.py`: 修改分析方法
  - `SentimentAnalyzer/SentimentAnalyzer.py`: 自定义情感分析算法