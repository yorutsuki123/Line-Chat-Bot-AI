from flask import Flask, request, abort
from datetime import datetime
import sys

sys.path.append('../KEY')
from linebotkey import (
    LINE_ACCESS_TOKEN,
    LINE_WEBHOOK
)

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
import boto3
from chathandler import ChatHandler as CH

client = boto3.client('dynamodb')
app = Flask(__name__)

configuration = Configuration(access_token=LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_WEBHOOK)

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

@app.route("/")
def idx():
    return 'OKK'

def getChannelId(line_bot_api, event):
    if event.source.type == 'user':
        chId = 'user_' + event.source.user_id
        profile = line_bot_api.get_profile(event.source.user_id)
    if event.source.type == 'group':
        chId = 'group_' + event.source.group_id
        profile = line_bot_api.get_group_member_profile(event.source.group_id, event.source.user_id)
    if event.source.type == 'room':
        chId = 'room_' + event.source.room_id
        profile = line_bot_api.get_room_member_profile(event.source.room_id, event.source.user_id)
    return chId, profile

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        chId, profile = getChannelId(line_bot_api, event)
        msg_id = event.message.id
        now_time = datetime.fromtimestamp(event.timestamp // 1000).strftime('%Y/%m/%d %H:%M:%S')
        display_name = profile.display_name
        user_id = event.source.user_id
        msg_type = 'Text'
        message = event.message.text
        img_url = ''
        client.put_item(
            TableName='LineBot',
            Item={
                'ID': {'S': msg_id},
                'ChannelID': {'S': chId},
                'Time': {'S': now_time},
                'DisplayName': {'S': display_name},
                'UserID': {'S': user_id},
                'MessageType': {'S': msg_type},
                'Message': {'S': message},
                'ImageURL': {'S': img_url}
            }
        )
        if event.source.type == 'user':
            message = message.strip()
            if message[0] == '/':
                if message == '/clear':
                    CH.get_handler(chId).clear()
                    reply = '嗶嗶嗶~遺忘光線~'
                elif message == '/help':
                    reply = '/clear - 清除聊天紀錄\n/help - 顯示指令列表'
                else:
                    reply = '指令錯誤'
            else:
                reply = CH.get_handler(chId).send_message(message)

            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply)]
                )
            )
        
        

if __name__ == "__main__":
    app.run()