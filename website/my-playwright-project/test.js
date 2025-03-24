const { chromium } = require('playwright');

(async () => {
  // 啟動瀏覽器
  const browser = await chromium.launch({ headless: false }); 
  const page = await browser.newPage();
  
  try {
    // 導航到 NTNU Webmail 登入頁面
    await page.goto('https://webmail.ntnu.edu.tw/rcmail/?_task=mail&_mbox=INBOX');
    
    // 填寫登入表單
    await page.fill('input[name="_user"]', '40947060s'); // 替換為你的實際用戶名
    await page.fill('input[name="_pass"]', 'Ycps070025'); // 替換為你的實際密碼
    
    // 點擊登入按鈕
    await page.click('#custom-login-submit');
    
    // 等待登入完成並加載郵箱頁面
    await page.waitForNavigation({ timeout: 60000 });
    console.log('登入完成');
    
    // 保存登入後的截圖
    await page.screenshot({ path: 'after_login.png' });
    
    // 點擊撰寫郵件按鈕
    console.log('尋找並點擊撰寫郵件按鈕');
    await page.waitForSelector('a.button.compose', { timeout: 60000 });
    await page.click('a.button.compose');
    
    console.log('等待郵件編輯界面加載');
    // 等待郵件編輯界面加載
    await page.waitForTimeout(5000);
    await page.screenshot({ path: 'compose_screen.png' });
    
    // 填寫收件人、主題
    console.log('填寫郵件欄位');
    await page.fill('textarea[name="_to"]', '40947060s@ntnu.edu.tw');
    await page.fill('input[name="_subject"]', '自動化測試郵件');
    
    // 直接使用已知有效的 iframe 選擇器
    console.log('尋找郵件正文編輯器');
    const frameHandle = await page.waitForSelector('iframe[id*="compose"]', { timeout: 30000 });
    const frame = await frameHandle.contentFrame();
    
    // 嘗試在 iframe 中填寫內容
    try {
      await frame.fill('#tinymce', '這是一封由 Playwright 自動發送的測試郵件。\n\n祝好！');
      console.log('成功填寫郵件內容');
    } catch (e) {
      console.log('使用 #tinymce 填寫失敗，嘗試 body 選擇器');
      await frame.fill('body', '這是一封由 Playwright 自動發送的測試郵件。\n\n祝好！');
    }
    
    // 保存填寫後的截圖
    await page.screenshot({ path: 'after_compose.png' });
    
    // 嘗試點擊發送按鈕
    console.log('嘗試發送郵件');
    try {
      await page.click('#rcmbtn107');
    } catch (e) {
      console.log('使用 ID 點擊發送按鈕失敗，嘗試其他方法');
      try {
        await page.click('a.button.send', { force: true });
      } catch (e2) {
        console.log('使用類選擇器點擊失敗，嘗試 JavaScript 方法');
        await page.evaluate(() => {
          const buttons = Array.from(document.querySelectorAll('a.button')).filter(a => 
            a.textContent.includes('寄出') || a.title.includes('寄出'));
          if (buttons.length > 0) buttons[0].click();
        });
      }
    }
    
    // 等待發送完成
    await page.waitForTimeout(5000);
    await page.screenshot({ path: 'after_send.png' });
    
  } catch (error) {
    console.error('執行過程中出現錯誤:', error);
    await page.screenshot({ path: 'error_screen.png' });
  } finally {
    // 關閉瀏覽器
    await browser.close();
  }
})();
