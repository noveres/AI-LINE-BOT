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
    MulticastRequest,
    StickerMessage,  
    ImageMessage,     
    VideoMessage,     
    AudioMessage,     
    LocationMessage,  
    Emoji,
    FlexMessage,  
    TemplateMessage,
    ConfirmTemplate,
    ButtonsTemplate,
    CarouselTemplate,
    CarouselColumn,
    ImageCarouselTemplate,
    ImageCarouselColumn,
    RichMenuArea, RichMenuBounds, RichMenuSize, RichMenuRequest, MessageAction        

  
  
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    FollowEvent,
    PostbackEvent,
    )
from datetime import datetime


import requests
import json
import os

app = Flask(__name__)


configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
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

    return 'OK'

    

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_text = event.message.text  # 抓取使用者輸入的文字
        
        if user_text == 'A':
            buttons_template = ButtonsTemplate(
                title='超可愛的吉哇哇',
                text='(๑•̀ㅂ•́)و✧',
                actions=[
                    PostbackAction(label='輕輕按下去', text='被咬了', data='postback'),
                ])
            template_message = TemplateMessage(
                alt_text='Postback Sample',
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
            
        elif user_text == '按鈕':
            confirm_template = ConfirmTemplate(
                title='超可愛的吉哇哇',
                text='你確定要按下按鈕嗎？',
                actions=[
                    PostbackAction(label='是', text='是', data='postback'),
                    PostbackAction(label='否', text='否', data='postback')

                ]

            )
            template_message = TemplateMessage(
                alt_text='Confirm alt text',
                template=confirm_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
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
                    messages=[
                        ImageMessage(original_content_url=url, preview_image_url=url)
                    ]
                )
            )

        elif user_text == '影片':
            url = request.url_root + 'static/video.mp4'
            url = url.replace("http", "https")
            app.logger.info("url=" + url)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        VideoMessage(original_content_url=url, preview_image_url=url)
                    ]
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
                    messages=[
                        AudioMessage(original_content_url=url, duration=duration)
                    ]
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
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=user_text)]
                )
            )




@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'postback':
        print('Postback event is triggered')




def create_rich_menu_1():
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_blob_api = MessagingApiBlob(api_client)

        areas = [
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=0,
                    y=0,
                    width=833,
                    height=843
                ),
                action=MessageAction(text='A')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=834,
                    y=0,
                    width=833,
                    height=843
                ),
                action=MessageAction(text='B')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=1663,
                    y=0,
                    width=834,
                    height=843
                ),
                action=MessageAction(text='C')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=0,
                    y=843,
                    width=833,
                    height=843
                ),
                action=MessageAction(text='D')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=834,
                    y=843,
                    width=833,
                    height=843
                ),
                action=MessageAction(text='E')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=1662,
                    y=843,
                    width=834,
                    height=843
                ),
                action=MessageAction(text='F')
            )
        ]

        rich_menu_to_create = RichMenuRequest(
            size=RichMenuSize(
                width=2500,
                height=1686,
            ),
            selected=True,
            name="圖文選單1",
            chat_bar_text="查看更多資訊",
            areas=areas
        )

        rich_menu_id = line_bot_api.create_rich_menu(
            rich_menu_request=rich_menu_to_create
        ).rich_menu_id

        with open('./public/richmenu-a.png', 'rb') as image:
            line_bot_blob_api.set_rich_menu_image(
                rich_menu_id=rich_menu_id,
                body=bytearray(image.read()),
                _headers={'Content-Type': 'image/png'}
            )

        line_bot_api.set_default_rich_menu(rich_menu_id)


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
                        "text": "A"
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
                        "text": "B"
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
                        "text": "C"
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
                        "text": "D"
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
                        "text": "E"
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
                        "text": "F"
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
    app.run()