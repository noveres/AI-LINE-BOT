from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    MessagingApiBlob,
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    ButtonsTemplate,
    PostbackAction,
    TemplateMessage,
    StickerMessage,  
    ImageMessage,     
    VideoMessage,     
    AudioMessage,     
    LocationMessage,  
    Emoji,
  
    TemplateMessage,
  
    ButtonsTemplate,
    CarouselTemplate,
    CarouselColumn,

    URIAction,

        Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TemplateMessage,
  
    ButtonsTemplate,
    CarouselTemplate,
    CarouselColumn,

    URIAction,
    PostbackAction,

            

  
  
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent,
    )
from datetime import datetime

# 新增 Azure AI Language 庫
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

import requests
import json
import os
import re

# 載入環境變數 (.env 文件)
load_dotenv()

app = Flask(__name__)


configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 初始化 Azure AI Language 客戶端
azure_language_endpoint = os.getenv('AZURE_LANGUAGE_ENDPOINT')
azure_language_key = os.getenv('AZURE_LANGUAGE_KEY')

# 提取實體函數
def extract_entities(result):
    """
    從 Azure AI Language 分析結果中提取實體
    
    參數：
        result: Azure AI Language 服務返回的分析結果
        
    返回：
        提取的實體字典，格式為 {實體類型: 實體值}
    """
    # 實體提取的字典
    entities = {}
    
    # 檢查結果是否包含實體
    prediction = result["result"].get("prediction", {})
    if prediction and "entities" in prediction and prediction["entities"]:
        print("找到以下實體:")
        # 迭代所有找到的實體
        for entity in prediction["entities"]:
            category = entity.get("category", "")
            text = entity.get("text", "")
            
            # 將實體添加到字典中
            if category:
                entities[category] = text
                print(f"  - {category}: {text}")
    else:
        print("未找到任何實體")
    
    return entities

# 處理維修實體函數
def process_maintenance_entities(entities):
    """
    根據提取的實體，生成更具體的維修相關回應
    
    參數：
        entities: 提取的實體字典
        
    返回：
        基於實體信息的個性化回應
    """
    # 獲取各種實體值
    facility = entities.get("facility_type", "")
    location = entities.get("location", "")
    issue = entities.get("issue_type", "")
    
    # 構建更具體的回應
    response = "您報告的是"
    
    if location:
        response += f"{location}的"
    
    if facility:
        response += f"{facility}"
    else:
        response += "設施"
    
    if issue:
        response += f"{issue}問題"
    else:
        response += "問題"
    
    return response + "，請點擊下方按鈕填寫詳細的維修表單，我們會盡快處理。"

# 處理問候實體函數
def process_greeting_entities(entities):
    """
    根據提取的實體，生成更具體的問候相關回應
    
    參數：
        entities: 提取的實體字典
        
    返回：
        基於實體信息的個性化回應
    """
    # 獲取用戶關注點
    help_topic = entities.get("help_topic", "")
    user_concern = entities.get("user_concern", "")
    time_reference = entities.get("time_reference", "")
    
    # 簡化的問候處理邏輯
    greeting = "您好！"
    
    # 檢查是否是私人請求 - 放寬判斷條件，只要有user_concern就視為私人請求
    if user_concern:
        return f"{greeting}{_handle_private_request(user_concern)}"
    
    # 如果是其他主題的請求
    if help_topic:
        return f"{greeting}有什麼我可以幫您的嗎？{_get_help_topic_response(help_topic)}"
    else:
        return f"{greeting}有什麼我可以幫您的嗎？您可以詢問有關訪客登記、公共維修、公告查詢等服務。"

# 處理幫助實體函數
def process_help_entities(entities):
    """
    根據提取的實體，生成更具體的幫助相關回應
    
    參數：
        entities: 提取的實體字典
        
    返回：
        基於實體信息的個性化回應
    """
    # 獲取幫助主題和用戶需求
    help_topic = entities.get("help_topic", "")
    user_need = entities.get("user_need", "")
    
    # 根據不同的幫助主題提供相應引導
    if help_topic == "訪客登記" or help_topic == "訪客":
        return "關於訪客登記，您可以:\n1. 點擊選單中的「訪客登記」\n2. 填寫訪客資料\n3. 系統會自動通知相關人員\n\n需要更多幫助嗎？"
    elif help_topic == "維修" or help_topic == "公共維修":
        return "關於公共維修，您可以:\n1. 點擊選單中的「公共維修填報」\n2. 填寫維修內容和位置\n3. 追蹤「維修進度查看」\n\n有其他問題嗎？"
    elif help_topic == "公告" or help_topic == "查詢公告":
        return "關於公告查詢，您可以:\n1. 點擊選單中的「公告查詢」\n2. 查看最新社區公告\n\n需要了解其他功能嗎？"
    elif help_topic == "繳費" or help_topic == "繳費相關":
        return "關於繳費相關，您可以:\n1. 點擊選單中的「繳費相關」\n2. 查看費用明細和繳費方式\n\n還有其他問題嗎？"
    elif help_topic == "優惠" or help_topic == "週邊優惠":
        return "關於週邊優惠，您可以:\n1. 點擊選單中的「週邊店家的合作折扣」\n2. 瀏覽合作商家的折扣信息\n\n需要其他協助嗎？"
    else:
        return "您好！我是社區服務機器人，可以協助您:\n• 訪客登記\n• 公共維修申報與進度查詢\n• 公告查詢\n• 繳費相關\n• 週邊優惠資訊\n\n請問您需要什麼幫助？"

# 輔助函數：根據幫助主題生成回應
def _get_help_topic_response(help_topic):
    """根據幫助主題生成引導性回應"""
    if help_topic == "維修":
        return "需要申報公共維修嗎？可以告訴我詳細情況或直接點擊選單中的「公共維修填報」。"
    elif help_topic == "訪客":
        return "要進行訪客登記嗎？可以直接點擊選單中的「訪客登記」或告訴我詳細情況。"
    elif help_topic == "公告":
        return "想查看最新公告嗎？可以直接點擊選單中的「公告查詢」。"
    elif help_topic == "繳費":
        return "關於繳費的問題，可以點擊選單中的「繳費相關」了解詳情。"
    elif help_topic == "優惠":
        return "想了解週邊優惠嗎？可以點擊選單中的「週邊店家的合作折扣」查看詳情。"
    else:
        return "您可以詢問有關訪客登記、公共維修、公告查詢等服務。"

# 輔助函數：處理私人請求
def _handle_private_request(user_concern):
    """處理私人請求，提供適當的回應"""
    if "廁所" in user_concern or "洗手台" in user_concern or "馬桶" in user_concern:
        return "很抱歉，我們只能處理公共區域的維修請求，住宅內部的衛浴設備請聯繫專業水電工或物業管理處。"
    elif "冷氣" in user_concern or "空調" in user_concern:
        return "很抱歉，住宅內的冷氣或空調問題屬於私人維修範圍，建議您聯繫物業推薦的空調維修服務。"
    elif "房間" in user_concern or "客廳" in user_concern or "臥室" in user_concern:
        return "很抱歉，我們只能處理公共區域的維修請求，住宅內部的問題請聯繫物業管理處尋求協助。"
    else:
        return "很抱歉，若是私人住宅內的維修需求，請直接聯繫物業管理處。我們的服務範圍僅限於社區公共區域。"

# 創建 Azure AI Language 分析函數
def analyze_text(text):
    """
    使用 Azure AI Language 服務分析文本內容，識別用戶意圖和實體
    
    參數：
        text: 用戶輸入的文本
        
    返回：
        (分析結果, 回應文本, [可選命令])
    """
    # 檢查是否設置了 Azure 憑證
    if not azure_language_endpoint or not azure_language_key:
        return {"error": "Azure AI Language 服務尚未設置正確"}, "我們的AI服務目前無法使用，請嘗試使用選單選項或稍後再試。"
    
    try:
        # 建立 Azure AI Language 客戶端
        client = ConversationAnalysisClient(
            endpoint=azure_language_endpoint, 
            credential=AzureKeyCredential(azure_language_key)
        )
        
        # 設置分析參數 - 發送到 Azure 的請求結構
        task = {
            "kind": "Conversation",  # 指定為對話分析任務
            "analysisInput": {
                "conversationItem": {
                    "id": "1",  # 對話項目ID
                    "text": text,  # 用戶輸入的文字
                    "participantId": "user"  # 對話參與者標識
                }
            },
            "parameters": {
                "projectName": "WuyeGuanli",  # Azure 專案名稱
                "deploymentName": "Line-CLU",  # 部署名稱
                "verbose": True  # 返回詳細結果
            }
        }
        
        # 呼叫 Azure 服務進行分析
        result = client.analyze_conversation(task=task)
        
        # 從結果中提取頂部意圖和置信度分數
        top_intent = result["result"]["prediction"]["topIntent"]
        confidence = result["result"]["prediction"]["intents"][0]["confidenceScore"] if result["result"]["prediction"]["intents"] else 0
        
        # 提取實體信息
        entities = extract_entities(result)
        app.logger.info(f"提取的實體: {entities}")
        
        # 根據意圖提供對應的回覆 - 意圖和回應映射表
        intent_mapping = {
            "visitor_registration": {  # 訪客登記意圖
                "text": "您似乎想了解訪客登記的相關資訊，請點擊下方選單進行訪客登記。(尚未實裝)",
                "command": "訪客登記",
                "url": "https://noveres.github.io/fgbd",
                "image_url": request.url_root + 'static/FK.png'
            },
            "maintenance": {  # 公共維修意圖
                "text": "您需要報修公共設施嗎？請點擊下方填寫維修表單。",
                "command": "公共維修填報",
                "url": "https://noveres.github.io/fgbd/maintenance",
                "image_url": request.url_root + 'static/WS.png'
            },
            "maintenance_status": {  # 維修進度查詢意圖
                "text": "您想查詢維修進度，請點擊下方選單查看。",
                "command": "維修進度查看",
                "url": "https://noveres.github.io/fgbd/progress",
                "image_url": request.url_root +'static/CK.png'
            },
            "announcement": {  # 公告查詢意圖
                "text": "您可以通過下方選單查詢最新的公告資訊。",
                "command": "公告查詢",
                "url": "https://noveres.github.io/fgbd/announcement",
                "image_url": request.url_root +'static/CK.png'
            },
            "payment": {  # 繳費相關意圖
                "text": "您可以使用下方選單快速繳費。",
                "command": "快速繳費通道"
            },
            "nearby_discount": {  # 週邊優惠意圖
                "text": "您可以使用下方選單查看週邊店家的合作折扣信息。",
                "command": "週邊店家的合作折扣",
                "template": {
                    "type": "carousel",
                    "columns": [
                        {
                            "thumbnail_image_url": request.url_root + 'static/01.png',
                            "title": "餐飲優惠",
                            "text": "附近餐廳的特別優惠",
                            "actions": [{"type": "uri", "label": "查看詳情", "uri": "https://noveres.github.io/fgbd/UnderConstruction"}]
                        },
                        {
                            "thumbnail_image_url": request.url_root + 'static/02.png',
                            "title": "生活服務",
                            "text": "日常生活相關優惠",
                            "actions": [{"type": "uri", "label": "查看詳情", "uri": "https://noveres.github.io/fgbd/UnderConstruction"}]
                        },
                        {
                            "thumbnail_image_url": request.url_root + 'static/03.png',
                            "title": "娛樂休閒",
                            "text": "休閒娛樂特別優惠",
                            "actions": [{"type": "uri", "label": "查看詳情", "uri": "https://noveres.github.io/fgbd/UnderConstruction"}]
                        }
                    ]
                }
            },
            "help": {  # 幫助意圖
                "text": "您好！我是社區服務機器人，可以幫您處理訪客登記、公共維修、查詢公告、繳費以及提供周邊優惠信息。請告訴我您需要什麼幫助？",
                "command": None
            },
            "greeting": {  # 問候意圖
                "text": "您好！有什麼我可以幫您的嗎？您可以詢問有關訪客登記、公共維修、公告查詢等服務。",
                "command": None
            }
        }
        
        # 中文意圖映射到英文意圖（兼容性）
        chinese_to_english_intent = {
            "查詢訪客登記": "visitor_registration",
            "公共維修": "maintenance",
            "維修進度": "maintenance_status",
            "查詢公告": "announcement",
            "繳費相關": "payment",
            "週邊優惠": "nearby_discount",
            "幫助": "help",
            "問候": "greeting"
        }
        
        # 兼容中文和英文意圖名稱
        if top_intent in chinese_to_english_intent:
            top_intent = chinese_to_english_intent[top_intent]
        
        # 如果是已知意圖且信心度足夠
        if top_intent in intent_mapping and confidence >= 0.5:
            response = intent_mapping[top_intent]["text"]
            command = intent_mapping[top_intent]["command"]
            
            # 如果有實體且是維修意圖，可以生成更個性化的回應
            if entities:
                if top_intent == "maintenance":
                    # 檢查是否為私人請求
                    if "user_concern" in entities:
                        user_concern = entities["user_concern"]
                        greeting = "您好！"
                        response = f"{greeting}{_handle_private_request(user_concern)}"
                        # 為私人請求設置一個特殊命令，而不是None
                        command = "私人維修"
                    else:
                        response = process_maintenance_entities(entities)
                elif top_intent == "greeting":
                    response = process_greeting_entities(entities)
                elif top_intent == "help":
                    response = process_help_entities(entities)
            
            return result, response, command if command else None
        
        # 如果信心度不夠或沒有匹配的意圖，提供通用回覆
        return result, "抱歉，我不確定您想要什麼信息。您可以嘗試使用下方的選單，或更清楚地描述您的需求，例如「訪客登記」、「公共維修」或「查詢公告」等。", None
    
    except Exception as e:
        # 記錄錯誤並返回友好提示
        print(f"Azure AI Language 服務出錯: {str(e)}")
        return {"error": str(e)}, "抱歉，AI服務暫時遇到問題。請嘗試使用選單選項，或稍後再試。", None

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK',200

    
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_text = event.message.text  # 抓取使用者輸入的文字
        
        print(f"\n====== 用戶輸入: {user_text} ======")
        
        if user_text == '吉娃娃':
            buttons_template = ButtonsTemplate(
                title='超可愛的吉哇哇',
                text='(๑•̀ㅂ•́)و✧',
                actions=[
                    PostbackAction(label='輕輕按下去', text='(被咬了)', data='postback'),
                ]
            )
            template_message = TemplateMessage(
                alt_text='吉娃娃',
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )
        elif user_text == '(被咬了)':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='吉度憤怒')]
                )
            )

        elif user_text == '訪客登記':
            url = request.url_root + 'static/FK.jpg'
            url = url.replace("http", "https")
            app.logger.info("url=" + url)
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title='訪客登記',
                text='減輕工作人員的負擔，可讓業主決定是否接受需要由管理員登記。',
                actions=[
                    URIAction(label='點我填寫登記表單', uri='https://noveres.github.io/fgbd/'),

                ]
            )
            template_message = TemplateMessage(
                alt_text="訪客登記",
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )

        elif user_text == '公共維修填報':
            url = request.url_root + 'static/WS.png'
            url = url.replace("http", "https")
            app.logger.info("url=" + url)
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title='公共維修填報',
                text='資料登錄於公開資料庫，可讓所有使用者快速查詢，節省時間。',
                actions=[
                    URIAction(label='點我填寫維修表單', uri='https://noveres.github.io/fgbd/maintenance'),
                ]
            )
            template_message = TemplateMessage(
                alt_text="公共維修填報",
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )
        elif user_text == '維修進度查看':
            url = request.url_root + 'static/CK.png'
            url = url.replace("http", "https")
            app.logger.info("url=" + url)
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title='維修進度查看',
                text='快速查看公共維修的進度，避免錯過重要的維修事件。',
                actions=[
                    URIAction(label='連結', uri='https://noveres.github.io/fgbd/progress'),
                ]
            )
            template_message = TemplateMessage(
                alt_text="維修進度查看",
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )
        elif user_text == '公告查詢':
            url = request.url_root + 'static/GK.png'
            url = url.replace("http", "https")
            app.logger.info("url=" + url)
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title='公告查詢',
                text='快速查詢最新公告，避免錯過重要的活動。',
                actions=[
                    URIAction(label='連結', uri='https://noveres.github.io/fgbd/announcements'),
                ]
            )
            template_message = TemplateMessage(
                alt_text="公告查詢",
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )

        

        # Carousel Template
        elif user_text == '週邊店家的合作折扣':
            base_url = request.url_root + 'static/'
            image_urls = [
                base_url + '01.png',
                base_url + '02.png',
                base_url + '03.png'
            ]
            image_urls = [url.replace("http", "https") for url in image_urls]

            app.logger.info(f"Image URLs: {image_urls}")

            carousel_template = CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=image_urls[0],
                        title='第一項',
                        text='這是第一項的描述',
                        actions=[
                            URIAction(
                                label='按我前往',
                                uri='https://noveres.github.io/fgbd/UnderConstruction'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=image_urls[1],
                        title='第二項',
                        text='這是第二項的描述',
                        actions=[
                            URIAction(
                                label='按我前往',
                                uri='https://noveres.github.io/fgbd/UnderConstruction'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=image_urls[2],
                        title='第三項',
                        text='這是第三項的描述',
                        actions=[
                            URIAction(
                                label='按我前往',
                                uri='https://noveres.github.io/fgbd/UnderConstruction'
                            )
                        ]
                    ),
                ]
            )

            carousel_message = TemplateMessage(
                alt_text="週邊店家優惠",
                template=carousel_template
            )

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[carousel_message]
                )
            )
        elif user_text == '快速繳費通道':
            url = request.url_root + 'static/qr.png'
            url = url.replace("http", "https")
            app.logger.info("url=" + url)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[ImageMessage(original_content_url=url, preview_image_url=url)]
                )
            )


        elif user_text == '文字':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="這是文字訊息")]
                )
            )

        elif user_text == '表情符號':
            emojis = [
                Emoji(index=0, product_id="5ac1bfd5040ab15980c9b435", emoji_id="001"),
                Emoji(index=12, product_id="5ac1bfd5040ab15980c9b435", emoji_id="002")
            ]
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='$ LINE 表情符號 $', emojis=emojis)]
                )
            )

        elif user_text == '貼圖':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[StickerMessage(package_id="446", sticker_id="1988")]
                )
            )

        elif user_text == '圖片':
            url = request.url_root + 'static/Logo.jpg'
            url = url.replace("http", "https")
            app.logger.info("url=" + url)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[ImageMessage(original_content_url=url, preview_image_url=url)]
                )
            )

        elif user_text == '影片':
            url = request.url_root + 'static/video.mp4'
            url = url.replace("http", "https")
            app.logger.info("url=" + url)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[VideoMessage(original_content_url=url, preview_image_url=url)]
                )
            )

        elif user_text == '音訊':
            url = request.url_root + 'static/music.mp3'
            url = url.replace("http", "https")
            app.logger.info("url=" + url)
            duration = 60000  # in milliseconds
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[AudioMessage(original_content_url=url, duration=duration)]
                )
            )

        elif user_text == '位置':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        LocationMessage(title='Location', address="Taipei", latitude=25.0475, longitude=121.5173)
                    ]
                )
            )
        else:
            # 使用 Azure AI Language 服務分析用戶意圖
            try:
                # 調用 analyze_text 函數分析用戶輸入
                result, response_text, command = analyze_text(user_text)
                
                # 如果返回的是模板消息
                if isinstance(command, TemplateMessage):
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[command]
                        )
                    )
                    return
                print(f"分析結果: 意圖={result.get('result', {}).get('prediction', {}).get('topIntent', '未知')}")
                print(f"回應內容: {response_text}")
                
                # 判斷是否返回了有效命令
                valid_commands = ['訪客登記', '公共維修填報', '維修進度查看', '公告查詢', '快速繳費通道', '週邊店家的合作折扣']
                
                # 獲取意圖名稱，用於檢查是否有URL
                intent = result.get('result', {}).get('prediction', {}).get('topIntent', '')
                
                # 獲取意圖映射
                intent_mapping = {
            "visitor_registration": {  # 訪客登記意圖
                "text": "您似乎想了解訪客登記的相關資訊，請點擊下方選單進行訪客登記。",
                "command": "訪客登記",
                "url": "https://noveres.github.io/fgbd/maintenance",
                "image_url": request.url_root + 'static/FK.png'
            },
            "maintenance": {  # 公共維修意圖
                "text": "您需要報修公共設施嗎？請點擊下方填寫維修表單。",
                "command": "公共維修填報",
                "url": "https://noveres.github.io/fgbd/maintenance",
                "image_url": request.url_root + 'static/WS.png'
            },
            "maintenance_status": {  # 維修進度查詢意圖
                "text": "您想查詢維修進度，請點擊下方選單查看。",
                "command": "維修進度查看",
                "url": "https://noveres.github.io/fgbd/progress",
                "image_url": request.url_root +'static/CK.png'
            },
            "announcement": {  # 公告查詢意圖
                "text": "您可以通過下方選單查詢最新的公告資訊。",
                "command": "公告查詢",
                "url": "https://noveres.github.io/fgbd/announcements",
                "image_url": request.url_root +'static/CK.png'
            },
            "payment": {  # 繳費相關意圖
                "text": "您可以使用下方選單快速繳費。",
                "command": "快速繳費通道"
            },
            "nearby_discount": {  # 週邊優惠意圖
                "text": "您可以使用下方選單查看週邊店家的合作折扣信息。",
                "command": "週邊店家的合作折扣",
                "template": {
                    "type": "carousel",
                    "columns": [
                        {
                            "thumbnail_image_url": request.url_root + 'static/01.png',
                            "title": "餐飲優惠",
                            "text": "附近餐廳的特別優惠",
                            "actions": [{"type": "uri", "label": "查看詳情", "uri": "https://noveres.github.io/fgbd/UnderConstruction"}]
                        },
                        {
                            "thumbnail_image_url": request.url_root + 'static/02.png',
                            "title": "生活服務",
                            "text": "日常生活相關優惠",
                            "actions": [{"type": "uri", "label": "查看詳情", "uri": "https://noveres.github.io/fgbd/UnderConstruction"}]
                        },
                        {
                            "thumbnail_image_url": request.url_root + 'static/03.png',
                            "title": "娛樂休閒",
                            "text": "休閒娛樂特別優惠",
                            "actions": [{"type": "uri", "label": "查看詳情", "uri": "https://noveres.github.io/fgbd/UnderConstruction"}]
                        }
                    ]
                }
            },
            "help": {  # 幫助意圖
                "text": "您好！我是社區服務機器人，可以幫您處理訪客登記、公共維修、查詢公告、繳費以及提供周邊優惠信息。請告訴我您需要什麼幫助？",
                "command": None
            },
            "greeting": {  # 問候意圖
                "text": "您好！有什麼我可以幫您的嗎？您可以詢問有關訪客登記、公共維修、公告查詢等服務。",
                "command": None
            }
        }
                
                # 特殊處理：如果命令是"私人維修"，添加物業管理處連絡信息
                if command == "私人維修":
                    # 可以為私人維修請求添加物業管理處的聯繫方式
                    buttons_template = ButtonsTemplate(
                        title='物業管理處聯繫方式',
                        text=response_text,
                        actions=[
                            URIAction(label='撥打電話', uri='tel:079638706')
                        ]
                    )
                    template_message = TemplateMessage(
                        alt_text='物業管理處聯繫方式',
                        template=buttons_template
                    )
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[template_message]
                        )
                    )
                    return
                
                # 檢查該意圖是否有URL
                has_url = False
                url = None
                image_url = None
                
                if intent in intent_mapping:
                    if "url" in intent_mapping[intent]:
                        has_url = True
                        url = intent_mapping[intent]["url"]
                    if "image_url" in intent_mapping[intent]:
                        image_url = intent_mapping[intent]["image_url"]
                
                # 如果意圖有URL
                if has_url and url:
                    # 如果有圖片URL，使用帶圖片的按鈕模板
                    if image_url:
                        image_url = image_url.replace("http", "https")
                        buttons_template = ButtonsTemplate(
                            thumbnail_image_url=image_url,
                            title=command if command else '查看連結',
                            text=response_text,
                            actions=[
                                URIAction(label='點擊這裡', uri=url)
                            ]
                        )
                    else:
                        # 沒有圖片，使用普通按鈕模板
                        buttons_template = ButtonsTemplate(
                            title=command if command else '查看連結',
                            text=response_text,
                            actions=[
                                URIAction(label='點擊這裡', uri=url)
                            ]
                        )
                    
                    template_message = TemplateMessage(
                        alt_text=command if command else '查看連結',
                        template=buttons_template
                    )
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[template_message]
                        )
                    )
                else:
                    # 沒有URL，直接返回文字回應
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text=response_text)]
                        )
                    )
            except Exception as e:
                # 出錯時返回友好的錯誤信息，並記錄詳細錯誤便於調試
                app.logger.error(f"處理用戶訊息時出錯: {str(e)}")
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="抱歉，我暫時無法處理您的請求。請稍後再試或使用選單選項。")]
                    )
                )

@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'postback':
        print('Postback event is triggered')

# 創建圖文選單
def create_rich_menu_2():
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_blob_api = MessagingApiBlob(api_client)
        # Create rich menu
        headers = {
            'Authorization': 'Bearer ' + os.getenv('CHANNEL_ACCESS_TOKEN'),
            'Content-Type': 'application/json'
        }
        body = {
            "size": {
                "width": 2500,
                "height": 1686
            },
            "selected": True,
            "name": "圖文選單 1",
            "chatBarText": "查看更多資訊",
            "areas": [
                {
                    "bounds": {
                        "x": 0,
                        "y": 0,
                        "width": 833,
                        "height": 843
                    },
                    "action": {
                        "type": "message",
                        "text": "訪客登記"
                    }
                },
                {
                    "bounds": {
                        "x": 834,
                        "y": 0,
                        "width": 833,
                        "height": 843
                    },
                    "action": {
                        "type": "message",
                        "text": "公共維修填報"
                    }
                },
                {
                    "bounds": {
                        "x": 1663,
                        "y": 0,
                        "width": 834,
                        "height": 843
                    },
                    "action": {
                        "type": "message",
                        "text": "維修進度查看"
                    }
                },
                {
                    "bounds": {
                        "x": 0,
                        "y": 843,
                        "width": 833,
                        "height": 843
                    },
                    "action": {
                        "type": "message",
                        "text": "公告查詢"
                    }
                },
                {
                    "bounds": {
                        "x": 834,
                        "y": 843,
                        "width": 833,
                        "height": 843
                    },
                    "action": {
                        "type": "message",
                        "text": "週邊店家的合作折扣"
                    }
                },
                {
                    "bounds": {
                        "x": 1662,
                        "y": 843,
                        "width": 838,
                        "height": 843
                    },
                    "action": {
                        "type": "message",
                        "text": "快速繳費通道"
                    }
                }
            ]
        }

        response = requests.post('https://api.line.me/v2/bot/richmenu', headers=headers, data=json.dumps(body).encode('utf-8'))
        response = response.json()
        print(response)
        rich_menu_id = response["richMenuId"]
        
        # Upload rich menu image
        with open('static/richmenu-1.jpg', 'rb') as image:
            line_bot_blob_api.set_rich_menu_image(
                rich_menu_id=rich_menu_id,
                body=bytearray(image.read()),
                _headers={'Content-Type': 'image/jpeg'}
            )

        line_bot_api.set_default_rich_menu(rich_menu_id)

create_rich_menu_2()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))