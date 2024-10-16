# 股票新聞ETL和數據分析工具

這是一個用於股票新聞數據的ETL（提取、轉換、加載）和分析的Python項目。該工具可以處理原始新聞數據，進行情感分析，並生成可視化儀表板。

### 運行程序


1. 完整ETL和分析流程：
   
   這將執行數據提取、轉換、加載，然後進行分析並更新儀表板。
   ```
   python Main.py
   ```

2. 僅運行數據分析：

   如果您已經有了轉換後的數據（`Transformed_data.csv`在`Store`目錄中），可以使用此選項只進行分析。
   ```
   python Main.py --analyze
   ```

### 查看結果

- ETL處理後的數據將保存為 `Store/Transformed_data.csv`
- 分析結果和可視化輸出將保存在 `output` 目錄中

### 日誌

- 程序運行日誌將被記錄，您可以查看日誌文件了解詳細的執行過程和可能的錯誤信息

### 自定義配置

- 如需修改數據處理或分析參數，請編輯相應的Python文件：
- `ETL.py`: 調整ETL流程
- `analyze.py`: 修改分析方法
- `SentimentAnalyzer/SentimentAnalyzer.py`: 自定義情感分析算法