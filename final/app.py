# app.py
import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from openai import AzureOpenAI
import tempfile
import logging
from datetime import datetime
import re  # 新增正則表達式庫
from pydub import AudioSegment # 導入 pydub 庫
from pydub.playback import play # 導入 play 函數
import subprocess # 導入 subprocess 庫
import google.generativeai as genai # 導入 Google Gemini 函式庫

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv() # 載入 .env 檔案中的環境變數

app = Flask(__name__, static_folder='public', static_url_path='/static') # 設定 Flask 應用程式，並指定靜態檔案資料夾為 'public' 和 URL 路徑為 /static

# 從環境變數中取得 Azure OpenAI 的設定
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_WHISPER_DEPLOYMENT_ID = os.getenv("AZURE_OPENAI_WHISPER_DEPLOYMENT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not all([AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_WHISPER_DEPLOYMENT_ID]):
    logging.error("錯誤：請確保 AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, 和 AZURE_OPENAI_WHISPER_DEPLOYMENT_ID 環境變數已設定。")
    exit(1)

# 初始化 Azure OpenAI 客戶端
try:
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version="2024-06-01" # 使用您提供的 API 版本
    )
    logging.info("Azure OpenAI 客戶端初始化成功。")
except Exception as e:
    logging.error(f"Azure OpenAI 客戶端初始化失敗: {e}")
    exit(1)

# 配置 Gemini API 金鑰
genai.configure(api_key=GEMINI_API_KEY)
logging.info("Google Gemini API 已配置。")

# 設定 ffmpeg 路徑
# 假設 ffmpeg.exe 在專案根目錄的 'ffmpeg/bin' 資料夾中
# 請確保您已將 ffmpeg.7z 解壓縮到此路徑
ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "bin")
if os.path.exists(ffmpeg_path):
    os.environ["PATH"] += os.pathsep + ffmpeg_path
    logging.info(f"FFmpeg 路徑已添加到 PATH: {ffmpeg_path}")
else:
    logging.warning(f"FFmpeg 路徑不存在: {ffmpeg_path}。請確保 ffmpeg 已安裝並在系統 PATH 中，或解壓縮 ffmpeg.7z 到專案根目錄下的 'ffmpeg' 資料夾。")

# 定義根路由，用於提供前端 HTML 檔案
@app.route('/')
def index():
    logging.info("請求根目錄，提供 index.html。")
    return send_from_directory(app.static_folder, 'index.html')

# 定義處理音訊轉錄的 API 端點
@app.route('/transcribe-audio', methods=['POST'])
def transcribe_audio():
    logging.info("收到音訊轉錄請求。")
    
    # 新增分頁類別驗證
    selected_tab = request.form.get('selected_tab', 'unknown_tab')
    if not selected_tab or selected_tab == 'unknown_tab':
        logging.warning("未收到有效分頁類別資訊")
        return jsonify({"error": "未選擇分頁類別"}), 400

    # 清理分頁名稱中的特殊字元
    safe_tab_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '', selected_tab)[:50]

    # 建立分類儲存目錄
    today_date = datetime.now().strftime("%Y-%m-%d")
    save_dir = os.path.join(
        "recordings",
        today_date,
        safe_tab_name
    )
    
    try:
        os.makedirs(save_dir, exist_ok=True)
    except Exception as e:
        logging.error(f"建立儲存目錄失敗: {e}")
        return jsonify({"error": "無法建立儲存目錄"}), 500

    # 生成帶時間戳的檔名 (原始檔案)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_filename = f"{timestamp}_{safe_tab_name}.webm" # 假設原始檔案為 webm
    original_save_path = os.path.join(save_dir, original_filename)

    if 'audio' not in request.files:
        logging.warning("請求中沒有收到音訊檔案。")
        return jsonify({"error": "沒有收到音訊檔案。"}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        logging.warning("音訊檔案名稱為空。")
        return jsonify({"error": "音訊檔案名稱為空。"}), 400

    temp_dir = tempfile.mkdtemp()
    temp_original_audio_path = os.path.join(temp_dir, original_filename)
    mp3_filename = f"{timestamp}_{safe_tab_name}.mp3"
    temp_mp3_audio_path = os.path.join(temp_dir, mp3_filename)

    try:
        # 保存原始音訊檔案到臨時目錄
        audio_file.save(temp_original_audio_path)
        logging.info(f"原始音訊檔案已臨時保存於: {temp_original_audio_path}")

        # 轉換為 MP3
        logging.info(f"開始轉換音訊檔案至 MP3: {temp_mp3_audio_path}")
        audio = AudioSegment.from_file(temp_original_audio_path)
        audio.export(temp_mp3_audio_path, format="mp3", bitrate="96k")
        logging.info(f"音訊檔案已成功轉換並保存為 MP3: {temp_mp3_audio_path}")

        # 將原始檔案保存到永久目錄 (可選，如果不需要保存原始格式，可以移除此行)
        # 如果原始檔案是 .webm，這裡還是保存 .webm
        audio_file.seek(0) # 重置檔案指針
        audio_file.save(original_save_path)
        logging.info(f"原始音訊檔案已永久保存於: {original_save_path}")

        # 將轉換後的 MP3 檔案保存到永久目錄
        mp3_save_path = os.path.join(save_dir, mp3_filename)
        subprocess.run(["copy", temp_mp3_audio_path, mp3_save_path], shell=True, check=True)
        logging.info(f"MP3 檔案已永久保存於: {mp3_save_path}")

    except Exception as e:
        logging.error(f"音訊處理失敗: {e}")
        # 清理臨時檔案
        if os.path.exists(temp_original_audio_path):
            os.remove(temp_original_audio_path)
        if os.path.exists(temp_mp3_audio_path):
            os.remove(temp_mp3_audio_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        return jsonify({"error": f"音訊處理失敗: {str(e)}"}), 500

    try:
        # 開啟轉換後的 MP3 檔案，並傳遞給 Whisper API
        with open(temp_mp3_audio_path, "rb") as audio_input:
            response = client.audio.transcriptions.create(
                model=AZURE_OPENAI_WHISPER_DEPLOYMENT_ID,
                file=audio_input,
                language="zh" # 指定語言為中文 (ISO-639-1)
            )

        transcribed_text = response.text
        logging.info(f"語音轉文字成功，結果: {transcribed_text[:50]}...") # 顯示部分結果

        # 使用 Gemini 進行總結
        try:
            gemini_model = genai.GenerativeModel('gemini-2.0-flash')
            summary_prompt = f"請總結以下會議記錄或音訊轉錄的內容：\n\n{transcribed_text}\n\n總結："
            gemini_response = gemini_model.generate_content(summary_prompt)
            summary_text = gemini_response.text
            logging.info(f"Gemini 總結成功，結果: {summary_text[:50]}...")
        except Exception as e:
            logging.error(f"Gemini 總結失敗: {e}")
            summary_text = "" # 如果總結失敗，則總結文字為空

        # 移除所有臨時檔案和資料夾
        if os.path.exists(temp_original_audio_path):
            os.remove(temp_original_audio_path)
            logging.info(f"已清理失敗後殘留的臨時原始檔案: {temp_original_audio_path}")
        if os.path.exists(temp_mp3_audio_path):
            os.remove(temp_mp3_audio_path)
            logging.info(f"已清理失敗後殘留的臨時 MP3 檔案: {temp_mp3_audio_path}")
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
            logging.info(f"已清理失敗後殘留的臨時資料夾: {temp_dir}")
        return jsonify({"text": transcribed_text, "summary": summary_text}) # 回傳轉錄文字和總結文字

    except Exception as e:
        logging.error(f"語音轉文字失敗: {e}")
        # 即使失敗，也要確保臨時檔案被清理
        if os.path.exists(temp_original_audio_path):
            os.remove(temp_original_audio_path)
            logging.info(f"已清理失敗後殘留的臨時原始檔案: {temp_original_audio_path}")
        if os.path.exists(temp_mp3_audio_path):
            os.remove(temp_mp3_audio_path)
            logging.info(f"已清理失敗後殘留的臨時 MP3 檔案: {temp_mp3_audio_path}")
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
            logging.info(f"已清理失敗後殘留的臨時資料夾: {temp_dir}")
        return jsonify({"error": f"語音轉文字失敗: {str(e)}"}), 500

if __name__ == '__main__':
    # 確保 'public' 資料夾存在，用於存放前端檔案
    if not os.path.exists('public'):
        os.makedirs('public')
        logging.info("已創建 'public' 資料夾。")
    app.run(debug=True, port=3000) # 在開發模式下運行，方便除錯