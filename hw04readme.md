
```markdown
# 🎯 PTT 爬蟲與文本分析系統

一套完整的自動化文本分析系統，整合 PTT 爬蟲、中文斷詞、TF-IDF 分析與 Gemini AI 智能摘要功能。

## 📋 目錄

- [專案簡介](#專案簡介)
- [系統架構](#系統架構)
- [主要功能](#主要功能)
- [環境需求](#環境需求)
- [安裝步驟](#安裝步驟)
- [快速開始](#快速開始)
- [使用說明](#使用說明)
- [API 配置](#api-配置)
- [常見問題](#常見問題)
- [技術棧](#技術棧)
- [專案結構](#專案結構)
- [更新日誌](#更新日誌)
- [授權資訊](#授權資訊)

## 專案簡介

本系統提供一站式的 PTT 論壇文本分析解決方案，適用於學術研究、市場分析、輿情監測等應用場景。透過自動化流程，使用者只需點擊一次按鈕，即可完成從資料爬取到 AI 洞察的完整分析。

### 🎯 核心價值

- **零程式經驗也能使用**：透過 Gradio 介面，提供視覺化操作環境
- **完整自動化流程**：從爬蟲到分析一鍵完成，無需手動干預
- **智能 AI 摘要**：整合 Gemini 2.0 Flash 提供專業洞察
- **資料永久保存**：自動同步至 Google Sheet，方便後續分析


### 資料流程圖

| 階段 | 輸入 | 處理 | 輸出 |
|-----|------|------|------|
| **1. 爬蟲** | 看板名稱、頁數 | BeautifulSoup 解析 | 文章 DataFrame |
| **2. 儲存** | DataFrame | gspread 寫入 | Google Sheet URL |
| **3. 讀取** | Sheet URL | gspread 讀取 | 原始資料 |
| **4. 斷詞** | 文章標題 | jieba 分詞 | 詞彙列表 |
| **5. 分析** | 詞彙列表 | TF-IDF 計算 | 關鍵詞排名 |
| **6. AI** | 關鍵詞 + 樣本 | Gemini API | 洞察摘要 |
| **7. 回寫** | 分析結果 | Sheet 更新 | 統計工作表 |

## 主要功能

### ✨ 核心功能

| 功能模組 | 說明 | 技術實現 |
|---------|------|---------|
| **PTT 爬蟲** | 批次爬取指定看板文章 | requests + BeautifulSoup |
| **反爬蟲處理** | 自動設定 User-Agent 與延遲 | 請求間隔 1 秒 |
| **雲端儲存** | 自動同步至 Google Sheet | gspread API |
| **中文斷詞** | 精確、全模式、搜尋模式 | jieba 3 種模式 |
| **詞頻統計** | 統計關鍵詞出現次數 | collections.Counter |
| **TF-IDF 分析** | 提取文檔重要詞彙 | sklearn TfidfVectorizer |
| **AI 智能摘要** | 生成專業分析報告 | Gemini 2.0 Flash API |
| **結果回寫** | 統計資料寫回試算表 | gspread 分頁管理 |
| **互動介面** | 視覺化操作環境 | Gradio UI |

### 🎨 介面特色

- **參數化設定**：可自訂看板名稱、爬取頁數、關鍵詞數量
- **即時進度顯示**：每個步驟都有清晰的狀態提示
- **結果預覽**：分析完成後直接在介面上顯示完整報告
- **一鍵複製**：支援將分析結果複製到剪貼簿

## 環境需求

### 系統需求

- **Python 版本**：3.8 或以上
- **執行環境**：Google Colab（建議） 或本機 Python 環境
- **網路連線**：需連接網際網路以存取 PTT 與 API

### 必要帳號

| 服務 | 用途 | 申請連結 |
|-----|------|---------|
| **Google 帳號** | Google Sheet 存取 | [註冊](https://accounts.google.com/) |
| **Gemini API Key** | AI 摘要生成 | [申請](https://makersuite.google.com/app/apikey) |

## 安裝步驟

### 方法一：Google Colab（推薦）

```
# 1. 安裝新版 Gemini SDK
!pip install -U google-genai

# 2. 安裝其他依賴套件
!pip install requests beautifulsoup4 pandas jieba scikit-learn gradio gspread

# 3. 下載程式碼
!git clone https://github.com/你的帳號/ptt-analyzer.git
cd ptt-analyzer
```

### 方法二：本機環境

```
# 1. 建立虛擬環境（建議）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安裝所有依賴
pip install -r requirements.txt

# 3. 克隆專案
git clone https://github.com/你的帳號/ptt-analyzer.git
cd ptt-analyzer
```

### 依賴套件清單（requirements.txt）

```
requests>=2.31.0
beautifulsoup4>=4.12.0
pandas>=2.0.0
jieba>=0.42.1
scikit-learn>=1.3.0
gradio>=4.0.0
gspread>=5.12.0
google-genai>=1.0.0
google-auth>=2.23.0
```

## 快速開始

### Step 1：取得 Gemini API Key

1. 前往 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 登入 Google 帳號
3. 點擊「Create API Key」
4. 複製生成的 API Key

### Step 2：配置程式碼

在程式碼的第 37 行填入您的 API Key：

```
GEMINI_API_KEY = "你的_API_KEY_請填在這裡"
```

### Step 3：執行程式

```
# 在 Google Colab 或 Jupyter Notebook 中執行
python ptt_analyzer.py

# 或直接執行整個 notebook
```

### Step 4：開始使用

執行後會自動開啟 Gradio 介面，您將看到：

```
✅ Gradio 介面已啟動
📱 可透過產生的連結在任何裝置上使用

Running on local URL:  http://127.0.0.1:7860
Running on public URL: https://xxxxx.gradio.live
```

點擊 public URL 即可在瀏覽器中使用！

## 使用說明

### 基本操作流程

#### 1️⃣ 設定參數

| 參數 | 說明 | 建議值 |
|-----|------|-------|
| **看板名稱** | PTT 看板英文代號 | movie, Gossiping, Stock |
| **爬取頁數** | 要爬取的頁面數量 | 5-10 頁（避免過多） |
| **關鍵詞數量** | 顯示前 N 名熱詞 | 10 個 |
| **Sheet URL** | 現有試算表網址（選填） | 留空自動建立 |

#### 2️⃣ 執行分析

點擊「🚀 開始執行完整分析」按鈕，系統將自動：

```
📍 步驟 1/5：爬取 PTT 資料
⏳ 正在爬取第 1/5 頁...
✅ 成功爬取 100 篇文章

📍 步驟 2/5：寫入 Google Sheet
✅ 資料已寫入：https://docs.google.com/...

📍 步驟 3/5：文本分析（詞頻 + TF-IDF）
✅ 分析完成，發現 10 個熱門詞彙

📍 步驟 4/5：Gemini AI 生成洞察摘要
✅ AI 摘要生成完成

📍 步驟 5/5：回寫分析統計
✅ 統計結果已回寫至試算表

🎉 所有流程執行完成！
```

#### 3️⃣ 查看結果

分析完成後，您將獲得：

**A. 介面顯示**
- 熱門關鍵詞統計（前 10 名）
- TF-IDF 重要詞彙（前 10 名）
- Gemini AI 深度洞察（5 句話 + 120 字摘要）
- 資料概覽（文章數量、時間等）

**B. Google Sheet**
- 「爬蟲資料」工作表：原始文章資料
- 「分析統計」工作表：完整統計報告

### 進階使用

#### 自訂看板爬取

```
# 爬取八卦版
board_name = "Gossiping"

# 爬取科技版
board_name = "Tech_Job"

# 爬取股票版
board_name = "Stock"
```

#### 批次分析多個看板

```
boards = ["movie", "Gossiping", "Stock"]
for board in boards:
    result = full_automation_pipeline(
        board_name=board,
        pages=5,
        topN=10,
        sheet_url=None
    )
    print(result)
```

## API 配置

### Gemini API 版本對照

| 項目 | 舊版（已棄用） | 新版（2025年10月） |
|-----|--------------|------------------|
| **套件名稱** | `google-generativeai` | `google-genai` |
| **匯入方式** | `import google.generativeai as genai` | `from google import genai` |
| **客戶端初始化** | `genai.configure(api_key=KEY)`<br>`model = genai.GenerativeModel()` | `client = genai.Client(api_key=KEY)` |
| **模型名稱** | `gemini-1.5-flash` | `gemini-2.0-flash` |
| **內容生成** | `model.generate_content(prompt)` | `client.models.generate_content()` |

### 可用模型列表

| 模型 | 特性 | 適用場景 |
|-----|------|---------|
| `gemini-2.5-flash` | 最新實驗版，速度最快 | 快速原型開發 |
| `gemini-2.5-pro` | 最強推理能力 | 複雜分析任務 |
| `gemini-2.0-flash` | 穩定版本（**建議**） | 生產環境 |
| `gemini-2.0-flash-001` | 版本鎖定 | 需要版本一致性 |

### API 配額管理

| 計畫 | 每分鐘請求數 | 每日請求數 |
|-----|------------|-----------|
| **免費版** | 60 次 | 1,500 次 |
| **付費版** | 1,000 次 | 無限制 |

## 常見問題

### Q1：出現 404 錯誤怎麼辦？

**錯誤訊息：**
```
404 POST https://generativelanguage.googleapis.com/...
models/gemini-1.5-flash is not found
```

**解決方案：**
```
# 1. 移除舊版套件
!pip uninstall -y google-generativeai

# 2. 安裝新版
!pip install -U google-genai

# 3. 重啟 Runtime（Colab：Runtime > Restart runtime）
```

### Q2：爬蟲被封鎖怎麼辦？

**症狀：** 無法取得 PTT 資料或回傳 403 錯誤

**解決方案：**
1. 增加請求間隔：修改 `delay=2`（預設為 1 秒）
2. 更換 User-Agent：修改 `HEADERS` 字典
3. 減少爬取頁數：建議 5-10 頁即可

### Q3：Google Sheet 權限問題

**症狀：** 無法寫入試算表

**解決方案：**
```
# 在 Colab 中重新執行認證
from google.colab import auth
auth.authenticate_user()

# 確認權限設定
from google.auth import default
creds, _ = default()
```

### Q4：中文斷詞不準確

**解決方案：**
```
# 載入自訂詞典
jieba.load_userdict("custom_dict.txt")

# 新增單個詞彙
jieba.add_word("某個專有名詞")

# 調整詞彙權重
jieba.suggest_freq("某詞", True)
```

### Q5：記憶體不足錯誤

**解決方案：**
- 減少爬取頁數（< 10 頁）
- 分批處理資料
- 使用 Colab Pro（更大記憶體）

## 技術棧

### 核心技術對照

| 分類 | 技術 | 版本 | 用途 |
|-----|------|------|------|
| **爬蟲** | requests | 2.31+ | HTTP 請求 |
| | BeautifulSoup4 | 4.12+ | HTML 解析 |
| **資料處理** | pandas | 2.0+ | 資料結構 |
| | NumPy | 1.24+ | 數值計算 |
| **中文 NLP** | jieba | 0.42+ | 中文斷詞 |
| | scikit-learn | 1.3+ | TF-IDF 分析 |
| **AI 整合** | google-genai | 1.0+ | Gemini API |
| **雲端服務** | gspread | 5.12+ | Google Sheet API |
| | google-auth | 2.23+ | OAuth 認證 |
| **使用者介面** | Gradio | 4.0+ | Web UI |
