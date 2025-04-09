# AI-LINE-BOT

基於LINE平台的智能社區服務機器人，整合Azure AI Language服務，提供社區居民便捷的服務體驗。

## 專案介紹

本專案是一個智能社區服務LINE機器人，旨在為社區居民提供便捷的服務體驗。機器人利用Azure AI Language服務進行自然語言理解，能夠識別用戶意圖並提供相應的服務，包括訪客登記、公共維修申報、維修進度查詢、公告查詢、繳費相關和週邊優惠資訊等功能。

## 功能特點

- **自然語言理解**：整合Azure AI Language服務，能夠理解用戶的自然語言輸入，識別意圖和實體
- **訪客登記**：提供線上訪客登記功能，減輕管理人員負擔
- **公共維修申報**：居民可以報告公共設施問題，系統會自動分類並處理
- **維修進度查詢**：查詢已申報維修事項的處理進度
- **公告查詢**：查看社區最新公告
- **繳費相關**：提供繳費通道和相關資訊
- **週邊優惠資訊**：提供社區周邊商家的優惠資訊

## 教學資源
這份專案參考了以下教學資源：


- [LINE Developers官方文檔](https://developers.line.biz/en/docs/messaging-api/line-bot-sdk/#official-sdks) - LINE Messaging API SDKs
- [大數據與人工智慧教學頻道](https://www.youtube.com/@bigdatantue) - 提供AI相關技術教學與實作指南，這個老師的教學非常詳細，推薦給有興趣的人學習，這個項目很多是基於他的內容。

## 技術架構

- **後端框架**：Flask
- **LINE SDK**：line-bot-sdk 3.7
- **AI服務**：Azure AI Language Conversations
- **環境變數管理**：python-dotenv

## 安裝步驟

1. 克隆專案到本地

```bash
git clone <repository-url>
cd AI-LINE-BOT
```

2. 安裝依賴套件

```bash
pip install -r requirements.txt
```

3. 設置環境變數

創建一個 `.env`文件，包含以下內容：

```
CHANNEL_ACCESS_TOKEN = 'your-line-channel-access-token'
CHANNEL_SECRET = 'your-line-channel-secret'
AZURE_LANGUAGE_ENDPOINT = 'your-azure-language-endpoint'
AZURE_LANGUAGE_KEY = 'your-azure-language-key'
```

## 環境配置

### LINE Bot設置

1. 在[LINE Developers](https://developers.line.biz/)創建一個Provider和Channel

   - 登入LINE Developers平台
   - 點擊「Create a new provider」，輸入Provider名稱
   - 在Provider頁面中，點擊「Create a Messaging API channel」
   - 填寫頻道基本資訊，包括頻道名稱、頻道描述、頻道圖示等
   - 同意條款並創建頻道
2. 獲取Channel Access Token和Channel Secret

   - 在頻道基本設定頁面，可以找到Channel Secret
   - 在Messaging API設定頁面，點擊「Issue」按鈕獲取Channel Access Token
   - 將這些資訊保存到 `.env`文件中
3. 設置Webhook URL

   - 在Messaging API設定頁面，設置Webhook URL為 `https://your-domain/callback`
   - 啟用「Use webhook」選項
   - 可以使用ngrok等工具在本地開發時創建臨時的公開URL
   - 點擊「Verify」按鈕測試Webhook連接是否成功
4. 設置Rich Menu（選擇性）

   - 在Rich Menu設定頁面，可以創建自定義的Rich Menu
   - 上傳Rich Menu圖片，設置區域和動作
   - 啟用Rich Menu並設為默認

### Azure AI Language設置

1. 在[Azure Portal](https://portal.azure.com/)創建Azure AI Language資源

   - 登入Azure Portal
   - 點擊「Create a resource」，搜索「Language Service」
   - 選擇「Language Service」，點擊「Create」
   - 填寫必要資訊，包括訂閱、資源組、區域、名稱等
   - 選擇定價層（可以選擇免費F0層級開始）
   - 點擊「Review + create」，然後點擊「Create」
2. 創建對話式語言理解專案

   - 在Azure AI Language Studio (https://language.cognitive.azure.com/) 登入
   - 選擇剛才創建的資源
   - 在「Conversational language understanding」部分，點擊「Create new project」
   - 填寫專案名稱、描述和語言（繁體中文）
3. 設置意圖和實體

   - 在專案中，點擊「Build schema」
   - 添加意圖：點擊「Add」，輸入意圖名稱（如visitor_registration）
   - 添加實體：點擊「Entities」標籤，添加實體（如facility_type）
   - 參考 `4.json`中的訓練數據，添加對應的意圖和實體
   - 為每個意圖添加示例語句，並標記其中的實體

   ![1744093208724](image/README/1744093208724.png)

   ![1744093189796](image/README/1744093189796.png)
4. 訓練並部署模型

   - 完成意圖和實體設置後，點擊「Train」按鈕
   - 訓練完成後，點擊「Deploy」按鈕
   - 創建一個部署名稱，然後點擊「Deploy」
5. 獲取端點和API金鑰

   - 部署完成後，點擊「Get prediction URL」
   - 複製端點URL和API金鑰
   - 將這些資訊保存到 `.env`文件中

### 本地開發環境設置

1. 安裝Python（建議3.8或更高版本）

   - 從[Python官網](https://www.python.org/downloads/)下載並安裝Python
   - 確保將Python添加到PATH環境變數中
2. 虛擬環境配置（強烈推薦）

   #### Windows系統


   ```bash
   # 創建虛擬環境
   python -m venv libot

   # 切換到Scripts目錄
   cd libot\Scripts

   # 啟動虛擬環境
   activate
   ```

   #### macOS/Linux系統

   ```bash
   # 創建虛擬環境
   python -m venv venv

   # 啟動虛擬環境
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

   #### 虛擬環境使用說明

   - 啟動成功後，命令提示字元前會出現 (libot)
   - 在虛擬環境中安裝的套件不會影響全域Python環境
   - 退出虛擬環境請使用 `deactivate` 命令

   #### 常見問題解決

   - 如果無法執行activate，請確認Python是否已加入PATH
   - Windows執行權限問題可使用：Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   - 建議每個專案使用獨立的虛擬環境，避免套件版本衝突
3. 安裝依賴套件

   ```bash
   pip install -r requirements.txt
   ```
4. 設置環境變數

   - 創建 `.env`文件，填入所有必要的API金鑰和設置
   - 確保 `.gitignore`文件中包含 `.env`，避免敏感資訊被提交到版本控制系統

## 使用方法

### 本地開發

```bash
python app.py
```

### 部署到伺服器

本專案可以部署到支持Python的任何伺服器平台，如Heroku、Vercel等。

## 意圖和實體

當前機器人能夠識別以下意圖：

- **visitor_registration**：訪客登記相關
- **maintenance**：公共維修相關
- **maintenance_status**：維修進度查詢
- **announcement**：公告查詢
- **payment**：繳費相關
- **nearby_discount**：週邊優惠
- **help**：幫助
- **greeting**：問候

機器人能夠識別以下實體：

- **facility_type**：設施類型（如電梯、燈具等）
- **location**：位置（如A棟、地下停車場等）
- **issue_type**：問題類型（如故障、漏水等）
- **time_reference**：時間參考（如今天、明天等）
- **help_topic**：幫助主題
- **user_concern**：用戶關注點

## 功能示例

### 訪客登記

用戶輸入：「我想登記訪客」
機器人回應：提供訪客登記表單連結

### 公共維修

用戶輸入：「電梯壞了」
機器人回應：提供維修表單連結，並可能詢問更多細節

### 維修進度查詢

用戶輸入：「我想查詢上週報修的電梯進度」
機器人回應：提供維修進度查詢連結

## 注意事項

- 請確保 `.env`文件中的敏感資訊不被公開
- 在生產環境中，建議使用HTTPS確保通訊安全
- 定期更新Azure AI Language模型以提高識別準確率
