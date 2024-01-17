'''
You have to create a file:
# file name: linebotkey.py
#------------------------------
# for line bot api
LINE_ACCESS_TOKEN='YOUR_CHANNEL_ACCESS_TOKEN'
LINE_WEBHOOK='YOUR_CHANNEL_SECRET'
# for gemini
GOOGLE_API_KEY='YOUR_GOOGLE_API_KEY'

'''
# the location of "linebotkey.py"
KEY_PATH = '../KEY' 
# AWS DynamoDB table name, the PK has to be "ID"
MSG_TABLE_NAME = 'LineBot'
