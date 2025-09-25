
***

# 課表查詢與 Gemini AI 行前提醒系統

智慧化課表管理，結合 Google Sheets 與 Gemini AI，自動查詢當日課程＋產生本週提醒，一句話掌握本週行前要點！

***

## 🚦 需求

- Python3 (Colab、Jupyter 或本機均可)
- Google 帳號（授權用於存取 Google Sheet 課表）
- 已建立 Google Sheet 並分頁命名：「課表」、「本週重點」
- Gemini API Key（預設本程式已內嵌）

***

## 📋 安裝

Colab/Python/Jupyter 通用：

```bash
pip install gspread pandas google-auth google-generativeai
```

***

## 🗂️ Google Sheet 分頁格式

- 課表分頁（「課表」）：  
  | 星期 | 時段 | 課程 | 地點 |
  |------|------|------|------|
  | 1    | 第一節 | 數學 | A101 |
  | ...  | ...   | ...  | ...  |

- 行前提醒分頁（「本週重點」）：  
  A1 位置輸出提醒文字

***

## 🔑 設定 Gemini API Key & Sheet 網址

程式預設已內嵌：
- Gemini API Key：`AIzaSyCkvmEhKLKRQl4EnfkjL7kCcGL_mH0YP4s`
- Sheet 網址例：`https://docs.google.com/spreadsheets/d/xxxx/edit?usp=sharing`

如需更換，直接編輯程式碼區段即可。

***

## 🚀 使用方式

### 1. 啟動程式

Colab/ Jupyter 直接執行。  
本機請先授權 Google Colab（自動跳出驗證流程）。

### 2. 功能選單

- `1. 查詢指定星期的課程`：輸入 1~7 查詢對應天課表與地點。
- `2. 產生本週 AI 行前提醒並回寫`：AI 自動歸納本週課表，產生一句備忘提醒，寫入「本週重點」分頁。
- `3. 離開`：結束程式。

### 3. 自動建立分頁

首次使用，如 Sheet 裡還沒分頁「課表」或「本週重點」，程式會自動新建分頁並補上表頭。

***

## 🧑‍🎓 功能說明

| 功能                          | 說明                                                     |
|------------------------------|---------------------------------------------------------|
| Google Sheet 程式連線         | 支援自動建立/補上課表分頁標題                           |
| 課表每日查詢                  | 支持依指定星期查詢所有課程、地點                         |
| Gemini AI 智慧行前提醒        | 本週所有課表自動生成一句行前提醒，貼心提醒攜帶物/先讀章節 |
| AI提醒自動回寫                | 將提醒內容自動回寫至「本週重點」分頁第一格               |

***

