import google.generativeai as genai
import sys

sys.path.append('../KEY')
from linebotkey import (
    GOOGLE_API_KEY
)
genai.configure(api_key=GOOGLE_API_KEY)

class ChatHandler:

    handlers = {}

    def __init__(self, id):
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])
        ChatHandler.handlers[id] = self

    def clear(self):
        self.chat = self.model.start_chat(history=[])

    def send_message(self, msg):
        try:
            response = self.chat.send_message(msg)
            return response.text
        except Exception as e:
            print(e)
            return "...(???)"
    
    def get_handler(id):
        if id in ChatHandler.handlers:
            return ChatHandler.handlers[id]
        return ChatHandler(id)
        