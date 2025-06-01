// public/app.js

let mediaRecorder;
let audioChunks = [];
let mediaStream; // 這個 stream 會來自 getDisplayMedia
const startButton = document.getElementById('startButton');
const stopButton = document.getElementById('stopButton');
const statusDiv = document.getElementById('status');
const originalTranscriptionResultDiv = document.getElementById('originalTranscriptionResult');
const summaryResultDiv = document.getElementById('summaryResult');
const tabSelector = document.getElementById('tabSelector');

// 更新狀態訊息，並可選擇顯示載入 Spinner
function updateStatus(message, showSpinner = false) {
    statusDiv.innerHTML = message;
    if (showSpinner) {
        const spinner = document.createElement('span');
        spinner.className = 'spinner';
        statusDiv.appendChild(spinner);
    }
}

// 停止媒體串流軌道函式
function stopMediaStreamTracks() {
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => {
            track.stop();
            console.log(`Track ${track.kind} stopped`);
        });
        mediaStream = null;
        console.log('媒體串流已停止。');
        // 通常瀏覽器也會移除分享提示
    }
}

// 處理使用者停止分享的事件 (例如點擊瀏覽器原生的 "停止分享" 按鈕)
function handleStreamInactive() {
    console.log('媒體串流變為 inactive (可能使用者停止了分享)');
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop(); // 這會觸發 onstop
    } else {
        // 如果不在錄製中，但串流停止了，也重設按鈕狀態
        updateStatus('分頁音訊分享已停止。點擊 "開始錄音" 以重新選擇並錄製。');
        startButton.disabled = false;
        stopButton.disabled = true;
        tabSelector.disabled = false;
    }
}

startButton.onclick = async () => {
    try {
        // 新增分頁類別驗證
        const selectedTabCategory = tabSelector.value;
        if (!selectedTabCategory || selectedTabCategory === 'unknown_tab') {
            updateStatus('請先選擇分頁類別', false);
            return;
        }

        updateStatus('正在請求分頁選擇權限...', true);
        
        // 新增音訊約束
        mediaStream = await navigator.mediaDevices.getDisplayMedia({
            video: { width: 1, height: 1 }, // 最小化視訊解析度
            audio: {
                sampleRate: 48000,
                channelCount: 2,
                sampleSize: 16
            }
        });

        updateStatus('已獲取媒體串流，正在檢查音訊軌道...');
        stopButton.disabled = false;
        tabSelector.disabled = true;

        const audioTracks = mediaStream.getAudioTracks();
        if (audioTracks.length === 0) {
            stopMediaStreamTracks();
            updateStatus('錯誤：未從選擇的分頁獲取到音訊軌道。請確保在分享時勾選了 "分享分頁音訊" (或類似選項)。', false);
            startButton.disabled = false;
            tabSelector.disabled = false;
            return;
        }
        console.log('成功獲取到音訊軌道:', audioTracks);
        audioTracks.forEach(track => {
            console.log('音訊軌道設定:', track.getSettings());
            track.onended = () => { // 監聽個別音軌的結束事件
                console.log(`音訊軌道 ${track.id} 已結束 (可能使用者停止了分享或關閉分頁)`);
                // 觸發統一的處理
                handleStreamInactive();
            };
        });

        // 監聽整個串流的 inactive 事件 (當使用者透過瀏覽器UI停止分享時觸發)
        // mediaStream.oninactive = handleStreamInactive; // 可以保留這個，或者只依賴 track.onended

        // 修改 mimeType 選擇邏輯
        const supportedTypes = [
            'video/webm;codecs=vp9',
            'video/webm;codecs=vp8',
            'video/webm',
            'audio/webm'
        ];
        
        let mimeType = supportedTypes.find(type => 
            MediaRecorder.isTypeSupported(type)
        );
        
        if (!mimeType) {
            throw new Error('沒有支援的媒體類型');
        }

        console.log(`最終使用 mimeType: ${mimeType}`);

        mediaRecorder = new MediaRecorder(mediaStream, {
            mimeType: mimeType,
            audioBitsPerSecond: 128000
        });

        // 新增錯誤監聽
        mediaRecorder.onerror = (e) => {
            console.error('MediaRecorder 錯誤:', e);
            updateStatus(`錄音錯誤: ${e.error.name}`, false);
        };

        audioChunks = [];

        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: mimeType });
            console.log('當前選擇的分頁類別:', selectedTabCategory);  // 新增日誌

            console.log('Audio Blob type:', audioBlob.type);
            console.log('Audio Blob size:', audioBlob.size);

            if (audioBlob.size === 0) {
                updateStatus('錯誤：錄製到的音訊檔案大小為 0。請重試。', false);
                originalTranscriptionResultDiv.textContent = '錄音失敗，未獲取到音訊數據。';
                stopMediaStreamTracks();
                startButton.disabled = false;
                tabSelector.disabled = false;
                return;
            }

            updateStatus('錄音結束，正在傳送音訊並進行轉錄...', true);
            stopButton.disabled = true;
            // startButton.disabled = false; // 會在 finally 中處理

            originalTranscriptionResultDiv.textContent = '請稍候...';
            summaryResultDiv.textContent = '請稍候...';

            const formData = new FormData();
            formData.append('audio', audioBlob, 'tab_recording.webm');
            formData.append('selected_tab', selectedTabCategory);

            try {
                const response = await fetch('/transcribe-audio', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`HTTP 錯誤! 狀態: ${response.status}, 錯誤訊息: ${errorData.error || '未知錯誤'}`);
                }

                const data = await response.json();
                originalTranscriptionResultDiv.textContent = data.text;
                summaryResultDiv.textContent = data.summary;
                updateStatus('轉錄與總結完成。');

            } catch (error) {
                console.error('上傳或轉錄失敗:', error);
                updateStatus(`轉錄失敗: ${error.message}`, false);
                originalTranscriptionResultDiv.textContent = `轉錄失敗，請檢查控制台錯誤。`;
                summaryResultDiv.textContent = `總結失敗。`;
            } finally {
                // 即使 onstop 之後，getDisplayMedia 的串流也需要手動停止其所有軌道
                // 或者依賴使用者點擊瀏覽器的 "停止分享"
                stopMediaStreamTracks(); // 確保所有軌道都被停止
                startButton.disabled = false;
                tabSelector.disabled = false;
            }
        };

        // 加入啟動延遲
        setTimeout(() => {
            mediaRecorder.start(1000); // 指定時間切片
            console.log('錄音已成功啟動');
        }, 100);

        // 如果有視訊軌道且我們不需要它，可以考慮停止它以節省資源
        // 但 MediaRecorder 設定為 audio/webm 應該只會處理音訊
        // mediaStream.getVideoTracks().forEach(track => track.stop());

    } catch (err) {
        console.error('無法開始螢幕/分頁擷取或錄音:', err); // 修改了日誌訊息
        if (err.name === 'NotAllowedError' || err.name === 'NotFoundError') {
            updateStatus('您取消了分頁選擇、未授予權限，或找不到可分享的來源。', false);
        } else if (err.name === 'NotSupportedError') {
            updateStatus(`錄音啟動失敗：不支援的操作。請檢查控制台以獲取詳細錯誤。(${err.message})`, false);
        }
         else {
            updateStatus(`無法開始錄製分頁音訊: ${err.message}`, false);
        }
        startButton.disabled = false;
        stopButton.disabled = true;
        tabSelector.disabled = false;
        stopMediaStreamTracks();
    }
};

stopButton.onclick = () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop(); // 這會觸發 onstop 事件，並在 onstop 的 finally 中停止軌道
    }
    // stopMediaStreamTracks(); // onstop 的 finally 會處理，或者讓使用者點瀏覽器的停止分享
    // 瀏覽器通常會有自己的 "停止分享" UI，點擊它也會觸發 track.onended 或 stream.oninactive
};

window.onload = () => {
    updateStatus('點擊 "開始錄音" 鈕來選擇一個分頁並錄製其聲音。');
    // 檢查 getDisplayMedia 是否受支援
    if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
        updateStatus('您的瀏覽器不支援錄製分頁音訊功能。請嘗試更新瀏覽器或使用其他瀏覽器。', false);
        startButton.disabled = true;
        tabSelector.disabled = true;
    }
};