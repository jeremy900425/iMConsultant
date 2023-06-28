
from flask import Flask, request, abort,send_from_directory,render_template

from linebot import (
    LineBotApi, WebhookHandler
)

from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import *

import os

from linebot.exceptions import InvalidSignatureError

import openai

import json

from linebot.models import FlexSendMessage

import threading

app = Flask(__name__)

#載入secrets
token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
secret= os.environ.get('LINE_CHANNEL_SECRET')
department_prompt = os.environ['department']
doctor_prompt = os.environ['doctor_prompt']
drug_prompt = os.environ['drug']
line_bot_api = LineBotApi(token)
handler = WebhookHandler(secret)

#載入flex message
FlexMessage = json.load(open('doctor.json','r',encoding='utf-8'))   
FlexMessage_age = json.load(open('age.json','r',encoding='utf-8'))   
FlexMessage_symptom = json.load(open('symptom.json','r',encoding='utf-8'))  
FlexMessage_drug = json.load(open('drug.json','r',encoding='utf-8'))  
doctor_data = json.load(open('doctor_data.json','r',encoding='utf-8'))  

#每次回應的進入點
@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

# 紀錄使用者的回答
user_answers = {}
openai.api_key = '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'

# 當 handler.handle(body, signature) 呼叫時，處理程序（handler）將根據註冊的規則來判斷如何處理接收到的回呼請求。如果回呼請求的事件類型為 MessageEvent 且訊息類型為 TextMessage，則將執行相對應的處理函式，這些註冊在 @handler.add(MessageEvent, message=TextMessage) 下方定義的處理函式。
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
#--------------------------------------------以下：藥物查詢--------------------------------------------
    print(user_answers)
    user_id = event.source.user_id 
    if event.message.text == '藥物查詢':
      #使用者點選藥物查詢後，回傳FlexMessage_drug訊息模板，並將drug的value設為1
        user_answers[user_id] = {'drug': 1} 
        line_bot_api.reply_message(
          event.reply_token,
          FlexSendMessage(
            alt_text = '藥物查詢',
            contents = FlexMessage_drug
          )
        )
    elif user_id in user_answers and 'drug' in user_answers[user_id] and user_answers[user_id]['drug'] == 1 :
      #因為FlexMessage_drug要求使用者輸入藥物的英文，所以當使用者輸入訊息後來到後台會滿足有user_id且drug==1，所以執行下方的程式
      #送入GPT-3.5-turbo
      line_bot_api.reply_message(event.reply_token,TextSendMessage(text='產生回應中，請稍後...'))
      input = event.message.text #讀取使用者輸入
      response = openai.ChatCompletion.create( #使用OpenAI api
        model="gpt-3.5-turbo",#設定模型
        max_tokens=1024,
        temperature=0.5,
        messages=[
              {"role": "system", "content": drug_prompt}, #輸入Prompt
              {"role": "user", "content": input}#使用者輸入
        ]
      )      
      answer = response.choices[0].message.content 
      #下方會使用Push而不使用reply是因為reply是一問一答制，且不吃token，所以說在上方已經回覆『產生回應中，請稍後...』接著要再回覆GPT的結果，所以這種連續性的回覆必須要使用Push完成
      reply_message = "欲查詢藥物："+input
      reply_arr=[]
      reply_arr.append( TextSendMessage(text=reply_message) )
      reply_arr.append( TextSendMessage(text=answer) )
      line_bot_api.push_message(user_id, reply_arr )
      user_answers[user_id] = {'drug': 0}
      # user_answers.pop(user_id, None)

#----------------------------------------以下：醫師推薦-------------------------------------------
      #先問 科別->症狀...所以下方都是採用 「若使用者 有紀錄到A資訊但沒有Ｂ資訊 則詢問B資訊」的方式撰寫
    elif event.message.text == '醫師推薦':
      line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(
              alt_text = '醫師推薦',
              contents = FlexMessage
            )
      )
    elif event.message.text in ['消化內科', '神經內科', '內分泌新陳代謝科', '風濕免疫科', '血液腫瘤科', '腎臟內科', '感染科', '呼吸胸腔科', '細胞學科', '一般外科', '神經外科', '骨科', '整形外科', '大腸直腸外科', '泌尿科', '外科重症暨外傷科', '胸腔外科', '心血管中心', '婦產科', '小兒科', '耳鼻喉科', '眼科', '口腔醫學科', '復健科', '家庭暨社區醫學科', '核子醫學科', '放射腫瘤科', '皮膚科', '精神科', '急診醫學部', '放射線科', '麻醉科', '職業醫學科', '一般醫學科', '病理科', '臨床病理科', '老人醫學科'] :
      user_answers[user_id] = {'department': event.message.text} #回覆訊息有以上字，就將這個科別記錄在department
      line_bot_api.reply_message(
          event.reply_token,
          FlexSendMessage(
            alt_text = '醫師推薦',
            contents = FlexMessage_symptom
        )
      )
    elif user_id in user_answers and 'department' in user_answers[user_id] and 'symptom' not in user_answers[user_id]:
      user_answers[user_id]['symptom'] = event.message.text 
      reply_message = f'您的資料如下\n欲查詢科別：{user_answers[user_id]["department"]}\n症狀：{user_answers[user_id]["symptom"]}'

      #醫師查詢演算法：先讓使用者輸入想要查詢的科別，之後透過資料處理將該科別的醫師以及醫師專業逐一列出並存於doctor_data_GPT變數中，之後透過設計好的Prompt將整理好的醫師資訊一起交給GPT（所以會有兩個role：system）
      
      # 尋找與使用者輸入相符的科別
      doctor_data_GPT=""
      for category in doctor_data:
          if category["category_name"] == user_answers[user_id]['department']:
              # 輸出該科別下的所有醫生名字及專長
              for doctor in category["doctors"]:
                  doctor_name = doctor["doctor_name"]
                  doctor_expertise = ', '.join(doctor["doctor_expertise"]) 
                  doctor_data_GPT = doctor_data_GPT + f"醫師姓名: {doctor_name}\n" + f"醫師專業: {doctor_expertise}\n\n"

      line_bot_api.reply_message(event.reply_token,TextSendMessage(text='產生回應中，請稍後...')）
      
      #送入GPT-3.5-turbo
      input = reply_message[7:].strip()
      response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens=1024,
        temperature=0.5,
        messages=[
              {"role": "system", "content": doctor_data_GPT},
              {"role": "system", "content": doctor_prompt},
              {"role": "user", "content": input}
        ]
      )      
      
      #從OpenAI的回應中獲取生成的回答
      answer = response.choices[0].message.content
      reply_arr=[]
      reply_arr.append( TextSendMessage(text=reply_message) )
      reply_arr.append( TextSendMessage(text=answer) )
      line_bot_api.push_message(user_id, reply_arr )
      # 清除使用者回答
      user_answers.pop(user_id, None)

#---------------------------------------------------------以下：科別查詢------------------------------------------
    #先問 性別->年齡...所以下方都是採用 「若使用者 有紀錄到A資訊但沒有Ｂ資訊 則詢問B資訊」的方式撰寫
    elif event.message.text == '科別查詢':
        gender_message = TemplateSendMessage(
            alt_text='請選擇性別',
            template=ConfirmTemplate(
                text='請選擇性別',
                actions=[
                    MessageTemplateAction(
                        label='男性',
                        text='男性'
                    ),
                    MessageTemplateAction(
                        label='女性',
                        text='女性'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, gender_message)
    elif event.message.text in ['男性', '女性']:
        user_answers[user_id] = {'gender': event.message.text}
        line_bot_api.reply_message(
          event.reply_token,
          FlexSendMessage(
            alt_text = '科別查詢',
            contents = FlexMessage_age
          )
        )
    elif user_id in user_answers and 'gender' in user_answers[user_id] and 'age' not in user_answers[user_id]:
        try:
            age = int(event.message.text)
            if age < 0 or age > 120:
                raise ValueError
            user_answers[user_id]['age'] = age
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                  alt_text = '科別查詢',
                  contents = FlexMessage_symptom
                )
            )
        except ValueError:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='請輸入有效的年齡'))
    elif user_id in user_answers and 'age' in user_answers[user_id] and 'symptom' not in user_answers[user_id]:
        user_answers[user_id]['symptom'] = event.message.text
        symptom_message = TemplateSendMessage(
            alt_text='症狀持續時間？',
            template=ButtonsTemplate(
                text='症狀持續時間？',
                actions=[
                    MessageTemplateAction(
                        label='1週以內',
                        text='1週以內'
                    ),
                    MessageTemplateAction(
                        label='1~3週',
                        text='1~3週'
                    ),
                    MessageTemplateAction(
                        label='3週以上',
                        text='3週以上'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, symptom_message)
    elif event.message.text in ['1週以內', '1~3週', '3週以上']:
        user_answers[user_id]['duration'] = event.message.text
        lifestyle_message = TemplateSendMessage(
            alt_text='日常生活習慣？\n（飲食、睡眠..等）',
            template=ButtonsTemplate(
                text='日常生活習慣？\n(飲食、睡眠..等)',
                actions=[
                    MessageTemplateAction(
                        label='良好',
                        text='良好'
                    ),
                    MessageTemplateAction(
                        label='時好時壞',
                        text='時好時壞'
                    ),
                    MessageTemplateAction(
                        label='較差',
                        text='較差'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, lifestyle_message)
    elif event.message.text in ['良好', '時好時壞', '較差']:
        user_answers[user_id]['lifestyle'] = event.message.text
        lifestyle_message = TemplateSendMessage(
            alt_text='心理狀態？\n(是否情緒低落、壓力大...等)',
            template=ButtonsTemplate(
                text='心理狀態？',
                actions=[
                    MessageTemplateAction(
                        label='穩定',
                        text='穩定'
                    ),
                    MessageTemplateAction(
                        label='起伏不定',
                        text='起伏不定'
                    ),
                    MessageTemplateAction(
                        label='異常',
                        text='異常'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, lifestyle_message)
    elif event.message.text in ['穩定', '起伏不定', '異常']:
        user_answers[user_id]['mental'] = event.message.text
        reply_message = f'您的資料如下\n性別：{user_answers[user_id]["gender"]}\n年齡：{user_answers[user_id]["age"]}\n症狀：{user_answers[user_id]["symptom"]}\n症狀持續時間：{user_answers[user_id]["duration"]}\n生活習慣：{user_answers[user_id]["lifestyle"]}\n心理狀態：{user_answers[user_id]["mental"]}'

        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='產生回應中，請稍後...'))

      # 送入ChatGPT
        input = reply_message[7:].strip()
        response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          max_tokens=1024,
          temperature=0.5,
          messages=[
                {"role": "system", "content": department_prompt},
                {"role": "user", "content": input}
          ]
        )
      
      # 從OpenAI的回應中獲取生成的回答
        answer = response.choices[0].message.content
      # 回應給使用者
        reply_arr=[]
        reply_arr.append( TextSendMessage(text=reply_message) )
        reply_arr.append( TextSendMessage(text=answer) )
        line_bot_api.push_message( user_id, reply_arr )

        # 清除使用者回答
        user_answers.pop(user_id, None)
    else: line_bot_api.reply_message(event.reply_token,TextSendMessage(text='請輸入指定的資料或者重新選擇您要使用的功能'))

@app.route("/", methods=['GET'])
def home():
    return render_template('index.html')

app.run(host='0.0.0.0', port=8080)


