import os
import json
import time
import pandas as pd
import sys
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

# 載入 .env 中的 GEMINI_API_KEY
load_dotenv()

# 定義評分項目（依據原始 xlsx 編碼規則）
ITEMS = [
    "引導",
    "評估(口語、跟讀的內容有關)",
    "評估(非口語、寶寶自發性動作、跟讀的內容有關)",
    "延伸討論",
    "複述",
    "開放式問題",
    "填空",
    "回想",
    "人事時地物問句",
    "連結生活經驗",
    "備註"
]

def parse_response(response_text):
    """
    嘗試解析 Gemini API 回傳的 JSON 格式結果。
    如果回傳內容被 markdown 的反引號包圍，則先移除這些標記。
    若解析失敗，則回傳所有項目皆為空的字典。
    """
    cleaned = response_text.strip()
    # 如果回傳內容以三個反引號開始，則移除第一行和最後一行
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    
    try:
        result = json.loads(cleaned)
        for item in ITEMS:
            if item not in result:
                result[item] = ""
        return result
    except Exception as e:
        print(f"解析 JSON 失敗：{e}")
        print("原始回傳內容：", response_text)
        return {item: "" for item in ITEMS}

def select_dialogue_column(chunk: pd.DataFrame) -> str:
    """
    根據 CSV 欄位內容自動選取存放逐字稿的欄位。
    優先檢查常見欄位名稱："text", "utterance", "content", "dialogue"
    若都不存在，則回傳第一個欄位。
    """
    preferred = ["text", "utterance", "content", "dialogue", "Dialogue"]
    for col in preferred:
        if col in chunk.columns:
            return col
    print("CSV 欄位：", list(chunk.columns))
    return chunk.columns[0]

def call_api_with_retry(client, content, max_retries=3, base_wait=2):
    """
    使用重試機制呼叫 API
    """
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=content
            )
            return response
        except Exception as e:
            wait_time = base_wait * (2 ** attempt)  # 指數退避
            if "RESOURCE_EXHAUSTED" in str(e):
                print(f"API 配額已用盡，等待 {wait_time} 秒後重試...")
            else:
                print(f"API 呼叫失敗：{e}，等待 {wait_time} 秒後重試...")
            
            if attempt < max_retries - 1:
                time.sleep(wait_time)
            else:
                raise e
    return None

def process_batch_dialogue(client, dialogues: list, delimiter="-----"):
    """
    將多筆逐字稿合併成一個批次請求。

    並以指定的 delimiter 分隔各筆結果。
    """
    prompt = (
        "你是一位親子對話分析專家，請根據以下編碼規則評估家長唸故事書時的每一句話，\n"
        + "\n".join(ITEMS) +
        "\n\n請依據評估結果，對每個項目：若觸及則標記為 1，否則留空。"
        " 請對每筆逐字稿產生 JSON 格式回覆，並在各筆結果間用下列分隔線隔開：\n"
        f"{delimiter}\n"
        "例如：\n"
        "```json\n"
        "{\n  \"引導\": \"1\",\n  \"評估(口語、跟讀的內容有關)\": \"\",\n  ...\n}\n"
        f"{delimiter}\n"
        "{{...}}\n```"
    )
    batch_text = f"\n{delimiter}\n".join(dialogues)
    content = prompt + "\n\n" + batch_text

    try:
        response = call_api_with_retry(client, content)
        if not response:
            return [{item: "" for item in ITEMS} for _ in dialogues]
        
        print("批次 API 回傳內容：", response.text)
        parts = response.text.split(delimiter)
        results = []
        for part in parts:
            part = part.strip()
            if part:
                results.append(parse_response(part))
        # 若結果數量多於原始筆數，僅取前面對應筆數；若不足則補足空結果
        if len(results) > len(dialogues):
            results = results[:len(dialogues)]
        elif len(results) < len(dialogues):
            results.extend([{item: "" for item in ITEMS}] * (len(dialogues) - len(results)))
        return results
    except ServerError as e:
        print(f"API 呼叫失敗：{e}")
        return [{item: "" for item in ITEMS} for _ in dialogues]
    
def analyze_dialogue_features(client, dialogue: str) -> dict:
    """
    使用 Gemini AI 分析對話特徵
    """
    prompt = (
        "你是一位親子對話分析專家，請根據以下逐字稿內容進行分析。\n"
        "請提供以下三個面向的分析，並以 JSON 格式回傳：\n"
        "1. dialogue_features: 這段對話中的主要特徵\n"
        "2. teaching_strategies: 家長使用的教學策略\n"
        "3. development_impact: 這些互動對幼兒語言發展的影響\n\n"
        "逐字稿內容：\n" + dialogue
    )

    try:
        response = call_api_with_retry(client, prompt)
        if not response:
            return {
                "dialogue_features": "API 呼叫失敗",
                "teaching_strategies": "API 呼叫失敗",
                "development_impact": "API 呼叫失敗"
            }
        
        # 嘗試解析 JSON 回應
        cleaned = response.text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:-3]  # 移除 ```json 和 ```
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:-3]
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "dialogue_features": response.text,
                "teaching_strategies": "",
                "development_impact": ""
            }
            
    except Exception as e:
        print(f"特徵分析失敗：{e}")
        return {
            "dialogue_features": "分析失敗",
            "teaching_strategies": "分析失敗",
            "development_impact": "分析失敗"
        }

def main():
    if len(sys.argv) < 2:
        print("使用方式：")
        print("python DRai.py <輸入CSV檔案路徑>")
        print("例如：python DRai.py ./input_data.csv")
        print("\n將會產生兩個輸出檔案：")
        print("1. 113_batch.csv - 編碼結果")
        print("2. dialogue_analysis.csv - 特徵分析結果")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    if not os.path.exists(input_csv):
        print(f"錯誤：找不到輸入檔案 '{input_csv}'")
        sys.exit(1)
    
    output_csv = "113_batch.csv"
    analysis_csv = "dialogue_analysis.csv"
    if os.path.exists(output_csv):
        os.remove(output_csv)
    if os.path.exists(analysis_csv):
        os.remove(analysis_csv)
    
    df = pd.read_csv(input_csv)
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("請設定環境變數 GEMINI_API_KEY")
    client = genai.Client(api_key=gemini_api_key)
    
    dialogue_col = select_dialogue_column(df)
    print(f"使用欄位作為逐字稿：{dialogue_col}")
    
    # 新增特徵分析的 DataFrame
    analysis_results = []
    
    batch_size = 20
    total = len(df)
    for start_idx in range(0, total, batch_size):
        end_idx = min(start_idx + batch_size, total)
        batch = df.iloc[start_idx:end_idx]
        dialogues = batch[dialogue_col].tolist()
        dialogues = [str(d).strip() for d in dialogues]
        
        # 原有的編碼處理
        batch_results = process_batch_dialogue(client, dialogues)
        batch_df = batch.copy()
        for item in ITEMS:
            batch_df[item] = [res.get(item, "") for res in batch_results]
        
        # 新增的特徵分析處理
        for dialogue in dialogues:
            analysis = analyze_dialogue_features(client, dialogue)
            analysis_results.append(analysis)
            time.sleep(2)
        
        # 儲存編碼結果
        if start_idx == 0:
            batch_df.to_csv(output_csv, index=False, encoding="utf-8-sig")
        else:
            batch_df.to_csv(output_csv, mode='a', index=False, header=False, encoding="utf-8-sig")
        
        print(f"已處理 {end_idx} 筆 / {total}")
        time.sleep(3)
    
    # 儲存特徵分析結果
    analysis_df = pd.DataFrame(analysis_results)
    analysis_df.to_csv(analysis_csv, index=False, encoding="utf-8-sig")
    
    print("全部處理完成。")
    print(f"編碼結果已寫入：{output_csv}")
    print(f"特徵分析結果已寫入：{analysis_csv}")

if __name__ == "__main__":
    main()
