
***

# 問卷開放題文字分析—Google Sheet + Gemini AI自動化

## 功能簡介

本腳本可：
- 讀取 Google Sheet 問卷表單的開放題（心得回饋等欄位）
- 自動進行詞頻統計、熱詞排行
- 調用 Gemini AI 產生 5 句洞察摘要及 120 字結論
- 統計及結論自動回寫至 Google Sheet 新分頁
- 結果可於 Colab 輸出、Sheet 查閱，方便自動批次分析

***

## 使用步驟

1. **準備 Google Sheet：**
   - 第一列填入欄名（如「心得回饋」「其他欄位1」…）
   - 第二列起填問卷開放式作答內容

2. **Colab 運行設定：**
   - 安裝 `gspread`、`pandas`、`google-generativeai`
   - 授權 Google 帳號，可用 Colab 互動窗口登入
   - 填入 SHEET_URL（Google Sheet 連結）
   - 填入 GEMINI_API_KEY（用個人測試金鑰）

3. **分析欄位設定：**
   - 修改程式中的 `OPEN_TEXT_COLUMN` 為你要分析的欄名
   - 執行程式即可自動分析/回寫

4. **結果查閱：**
   - 「統計表」分頁：排名、關鍵詞、出現次數、AI洞察摘要
   - Colab 視窗可直接 print AI 結論

***

## 範例欄位

| 心得回饋      | 其他欄位1 | 其他欄位2 |
|---------------|----------|----------|
| 這次課程讓我學到了很多… | …        | …        |

***

## 主要依賴套件

- gspread
- pandas
- google-generativeai

***

## 進階功能建議

- 可自訂停用詞列表，針對主題最佳化熱詞
- 可同時分析多個欄位，統合或分頁顯示不同欄位詞頻排行
- 可把 Geminin AI 分析 prompt 整合多面向洞察

***

