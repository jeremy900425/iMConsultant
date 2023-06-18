# ChatGPT Line Bot-醫療顧問機器人

中文 | 

## 模型
- `gpt-3.5-turbo`


## 介紹
將line與GPT-3.5-turbo做串接，透過設計好的Prompt實現「科別查詢」「醫師推薦」「藥物查詢」三大功能，均採用點擊式的輸入方式，讓使用操作簡單化，進而收集Prompt中所需要的資訊，以下說明功能內容

- 科別查詢：取得性別,年齡,症狀,日常習慣,心理狀態,症狀持續時間來推薦使用者可以掛哪一科,其中症狀的部分可以多重輸入。eg.症狀為頭痛,肚子痛 => 推薦「神經內科」
- 醫師推薦：選擇要掛的科別,並且告知症狀,GPT會透過醫師的專業領域來推薦適合的醫師給使用者
- 藥物查詢：輸入藥物學名（英文尤佳），即可知道藥物的「藥物名稱」「適應症」「用途」「劑量」「副作用」「外觀」

## LineBot註冊並創建
1. Google搜尋`Line developers` &rarr; Start Console &rarr; 使用Line帳號登入 &rarr; 點擊Providers旁邊的Create &rarr; 輸入Provider name(類似一個專案名稱而不是LineBot的名字) &rarr; ==Create a Messaging API channel==
2. Channel開頭的欄位都是LineBot得資料
    - Channel icon：LineBot的大頭照
    - Channel name：LineBot顯示的名稱
    - Channel description：LineBot用途描述
3. 剩下必填的請按照需求填寫，==URL的可以不必理會==，完成後點擊Create，會進入`LineBot設定頁面`

## LineBot設定頁面需要操作的事情以及功能介紹
- Basic settings：預覽Icon,查看==Channel secret(請複製起來,稍晚會用到)== 
- Messaging API：加入好友的QR code,Webhook URL,LINE Official Account features有`Edit`可以跳轉到LineBot後台設定（可設定加入好友之類的預設訊息）,==issue一串Channel access token(請複製起來,稍晚會用到)==
- Roles：授權LineBot操作設定,透過Email新增管理員


## 安裝步驟
### Token 取得
1. 取得 OpenAI 給的 API Token：
    1. [OpenAI](https://beta.openai.com/) 平台中註冊/登入帳號
    2. 右上方有一個頭像，點入後選擇 `View API keys`
    3. 點選中間的 `Create new secret key` -> 生成後即為 `OPENAI_API` （稍晚會用到）
    - 注意：每隻 API 有免費額度，也有其限制，詳情請看 [OpenAI Pricing](https://openai.com/api/pricing/)
2. 取得 Line Token：
    1. 登入 [Line Developer](https://developers.line.biz/zh-hant/)
    2. 創建機器人：
        1. 創建 `Provider` -> 按下 `Create`
        2. 創建 `Channel` -> 選擇 `Create a Messaging API channel`
        3. 輸入完必填的基本資料
        4. 輸入完成後，在 `Basic Settings` 下方，有一個 `Channel Secret` -> 按下 `Issue`，生成後即為 `LINE_CHANNEL_SECRET` （稍晚會用到）
        5. 在 `Messaging API` 下方，有一個 `Channel access token` -> 按下 `Issue`，生成後即為 `LINE_CHANNEL_ACCESS_TOKEN` （稍晚會用到）

### 專案設置
1. Fork Github 專案：
    1. 註冊/登入 [GitHub](https://github.com/)
    2. 進入 [ChatGPT-Line-Bot](https://github.com/TheExplainthis/ChatGPT-Line-Bot)
    3. 點選 `Star` 支持開發者
    4. 點選 `Fork` 複製全部的程式碼到自己的倉庫
2. 部署（免費空間）：
    1. 進入 [replit](https://replit.com/)
    2. 點選 `Sign Up` 直接用 `Github` 帳號登入並授權 -> 按下 `Skip` 跳過初始化設定
    3. 進入後中間主頁的部分點選 `Create` -> 跳出框，點選右上角 `Import from Github`
    4. 若尚未加入 Github 倉庫，則點選連結 `Connect GitHub to import your private repos.` -> 勾選 `Only select repositories` -> 選擇 `ChatGPT-Line-Bot`
    5. 回到第四步，此時 `Github URL` 可以選擇 `ChatGPT-Line-Bot` 專案 -> 點擊 `Import from Github`。

### 專案執行
1. 環境變數設定
    1. 接續上一步 `Import` 完成後在 `Replit` 的專案管理頁面左下方 `Tools` 點擊 `Secrets`。
    2. 右方按下 `Got it` 後，即可新增環境變數，需新增：
        1. 欲選擇的模型：
            - key: `OPENAI_MODEL_ENGINE`
            - value: `gpt-3.5-turbo`  
        2. ChatGPT 要讓助理扮演的角色詞（目前官方無釋出更多的使用方法，由玩家自行測試）
            - key: `SYSTEM_MESSAGE`
            - value: `You are a helpful assistant.`
        3. Line Channel Secret:
            - key: `LINE_CHANNEL_SECRET`
            - value: `[由步驟一取得]`
        4. Line Channel Access Token:
            - key: `LINE_CHANNEL_ACCESS_TOKEN`
            - value: `[由步驟一取得]`
2. 開始執行
    1. 點擊上方的 `Run`
    2. 成功後右邊畫面會顯示 `Hello World`，並將畫面中上方的**網址複製**下來
    3. 回到 Line Developer，在 `Messaging API` 下方的 `Webhook URL` 江上方網址貼過來，並加上 `/callback` 例如：`https://ChatGPT-Line-Bot.explainthis.repl.co/callback`
    4. 打開下方的 `Use webhook`
    5. 將下方 `Auto-reply messages` 關閉
    - 注意：若一小時內沒有任何請求，則程式會中斷，因此需要下步驟
3. CronJob 定時發送請求
    1. 註冊/登入 [cron-job.org](https://cron-job.org/en/)
    2. 進入後面板右上方選擇 `CREATE CRONJOB`
    3. `Title` 輸入 `ChatGPT-Line-Bot`，網址輸入上一步驟的網址，例如：`https://ChatGPT-Line-Bot.explainthis.repl.co/`
    4. 下方則每 `5 分鐘` 打一次
    5. 按下 `CREATE`

## 指令
在文字輸入框中直接輸入文字，即可與 ChatGPT 開始對話，而其他指令如下：

| 指令 | 說明 |
| --- | ----- |
| `/註冊` | 在輸入框輸入 `/註冊 ` + OpenAI API Token，就可以註冊 Token|
| `/系統訊息` | 在輸入框輸入 `/系統訊息 ` + 可以設定希望 ChatGPT 扮演什麼角色|
| `/清除` | 在輸入框輸入 `/清除 `，就可以清除歷史訊息|
| `/圖像` | 在輸入框輸入 `/圖像` + 指令，就會調用 DALL·E 2 模型，即可生成圖像。|
| 語音輸入 | 利用語音輸入，系統會自動將語音翻譯成文字，並且 ChatGPT 以文字回應| 
| 其他文字輸入 | 直接輸入文字，則會進入一般的 ChatGPT 對話模式|

