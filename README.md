# ChatGPT Line Bot-醫療顧問機器人

中文 | 

## 模型
- `gpt-3.5-turbo`


## 介紹
將line與GPT-3.5-turbo做串接，透過設計好的Prompt實現「科別查詢」「醫師推薦」「藥物查詢」三大功能，均採用點擊式的輸入方式，讓使用操作簡單化，進而收集Prompt中所需要的資訊，以下說明功能內容

- 科別查詢：取得性別,年齡,症狀,日常習慣,心理狀態,症狀持續時間來推薦使用者可以掛哪一科,其中症狀的部分可以多重輸入。eg.症狀為頭痛,肚子痛 &rarr; 推薦「神經內科」
- 醫師推薦：選擇要掛的科別,並且告知症狀,GPT會透過醫師的專業領域來推薦適合的醫師給使用者
- 藥物查詢：輸入藥物學名（英文尤佳），即可知道藥物的「藥物名稱」「適應症」「用途」「劑量」「副作用」「外觀」

## LineBot註冊並創建
1. Google搜尋`Line developers` &rarr; Start Console &rarr; 使用Line帳號登入 &rarr; 點擊Providers旁邊的Create &rarr; 輸入Provider name(類似一個專案名稱而不是LineBot的名字) &rarr; `Create a Messaging API channel`
2. Channel開頭的欄位都是LineBot的資料
    - Channel icon：LineBot的大頭照
    - Channel name：LineBot顯示的名稱
    - Channel description：LineBot用途描述
3. 剩下必填的請按照需求填寫，URL的可以不必理會，完成後點擊Create，會進入`LineBot設定頁面`

## LineBot設定頁面需要操作的事情以及功能介紹
- Basic settings：預覽Icon,查看`Channel secret(請複製起來,稍晚會用到)`
- Messaging API：加入好友的QR code,Webhook URL,LINE Official Account features有`Edit`可以跳轉到LineBot後台設定（可設定加入好友之類的預設訊息）,`issue一串Channel access token(請複製起來,稍晚會用到)`
- Roles：授權LineBot操作設定,透過Email新增管理員


## 安裝步驟
### OpenAI API KEY 取得
1. 取得 OpenAI 給的 API Token：
    1. [OpenAI](https://beta.openai.com/) 平台中註冊/登入帳號
    2. 右上方有一個頭像，點入後選擇 `View API keys`
    3. 點選中間的 `Create new secret key` -> 生成後即為 `OPENAI_API` （稍晚會用到）
    - 注意：每隻 API 有免費額度，也有其限制，詳情請看 [OpenAI Pricing](https://openai.com/api/pricing/)


### 專案設置
1. 部署（免費空間）：
    1. 進入 [replit](https://replit.com/)
    2. 直接 `Sign Up` 或`Log in`
    3. 進入後點選 `Create` &rarr; Template選擇Python,Title自行輸入,完成後點擊Create repl 
    4. 進入開發環境後，左側應該會看到3個檔案，請將預設的「main.py」刪除
    5. 下載GitHub中的所有檔案(共10個)，將10個檔案拖拉至開發環境中
2. 設定Secrets
    1.左側下方會看到Tools，裡面點選一個名為`Secrets`的工具
    2.點擊後，畫面會要新增一個New secret，每個secret都會有key和value
    3.接下來需要新增五個secrets，以下輸入key,value
    - **key**=LINE_CHANNEL_ACCESS_TOKEN,**value**=(先前有複製過)
    - **key**=LINE_CHANNEL_SECRET,      **value**=(先前有複製過)
    - **key**=department,               **value**=（請參考Github中的prompt.txt文件）
    - **key**=doctor_prompt,            **value**=（請參考Github中的prompt.txt文件）
    - **key**=drug,                     **value**=（請參考Github中的prompt.txt文件）
3. 設定OpenAI API KEY
    在main.py中搜尋「openai.api_key」，並將您先前複製的金鑰assign給該變數中(即把sk-xxxx..換掉) 
### 專案執行
1. 開始執行
    1. 點擊上方的 `Run`
    2. 成功後右邊畫面會顯示成功連線，並將畫面中上方的**網址複製**下來
    3. 回到 Line Developer，在 `Messaging API` 下方的 `Webhook URL` 將上方網址貼過來，並加上 `/callback` 例如：`https://ChatGPT-Line-Bot.explainthis.repl.co/callback`
    4. 打開下方的 `Use webhook`
    5. 將下方 `Auto-reply messages` 關閉
    - 注意：若一小時內沒有任何請求，則程式會中斷，需要重新啟動

## 測試LineBot
請在你先前創建的LineBot聊天室中，隨便回覆訊息，系統應當回覆`請輸入指定的資料或者重新選擇您要使用的功能`
- 若輸入「科別查詢」 ->啟動科別查詢功能
- 若輸入「醫師推薦」 ->啟動醫師推薦功能
- 若輸入「藥物查詢」 ->啟動藥物查詢功能

