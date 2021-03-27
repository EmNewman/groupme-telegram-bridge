import datetime
import logging
# import secrets
import requests
from telegram import Bot, Update
from telegram.ext import MessageHandler, TypeHandler, Filters, Dispatcher
# for heroku only
import os
import json
# from groupy import Client

TG_BOT_USERNAME = os.environ.get('TG_BOT_USERNAME')
GROUPME_BOT_ID = os.environ.get('GROUPME_BOT_ID')
TG_CHAT_ID = os.environ.get('TG_CHAT_ID')
TG_BOT_API_TOKEN = os.environ.get('TG_BOT_API_TOKEN')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
GROUPME_BOT_NAME = os.environ.get('GROUPME_BOT_NAME')
GROUPME_ACCESS_TOKEN = os.environ.get('GROUPME_ACCESS_TOKEN')

# let's use flask
from flask import Flask, request 

app = Flask(__name__)

# set up groupme
# client = Client.from_token(secrets.GROUPME_API_TOKEN)

dispatcher = None
bot = None


@app.before_first_request
def setup():
    global bot, dispatcher
    # set up logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

    # # TODO until i figure out webhooks we will just use polling.
    # updater = Updater(token=TG_BOT_API_TOKEN, use_context=True)
    # dispatcher = updater.dispatcher
    # tg_text_handler = MessageHandler(Filters.text & (~Filters.command), tg_msg_handler)
    # dispatcher.add_handler(tg_text_handler)

    # Set up webhook for TG
    bot = Bot(TG_BOT_API_TOKEN)
    bot.set_webhook(WEBHOOK_URL+"/telegram")
    dispatcher = Dispatcher(bot, None, workers=0)


    # TODO add photo handling, see here: 
    # https://python-telegram-bot.readthedocs.io/en/latest/telegram.message.html#telegram.Message 

    # Add text handling
    tg_text_handler = MessageHandler(Filters.text & (~Filters.command), tg_msg_handler)
    dispatcher.add_handler(tg_text_handler)

    # Add TG photo handling
    tg_photo_handler = MessageHandler(Filters.photo, tg_pic_handler)
    dispatcher.add_handler(tg_photo_handler)

    # custom handler for receiving Groupme messages
    groupme_handler = TypeHandler(GroupmeMessage, groupme_msg_handler)
    dispatcher.add_handler(groupme_handler)


class GroupmeMessage():
    def __init__(self, msg):
        self.name = msg['name']
        self.text = msg['text']
        # images
        self.attachments = msg['attachments']
        # any other metadata?
        self.avatar_url = msg['avatar_url']
        self.created_at = msg['created_at']
        self.group_id = msg['group_id']
        self.id = msg['id']
        self.sender_id = msg['sender_id']
        self.sender_type = msg['sender_type']
        self.source_guid = msg['source_guid']
        self.system = msg['system']
        self.user_id = msg['user_id']


@app.route('/groupme', methods=['POST'])
def webhook_groupme():
    data = request.get_json()
    # TODO remove
    print('Received {} to Groupme webhook'.format(data))

    # add message to dispatch
    gm_msg = GroupmeMessage(data)
    dispatcher.process_update(gm_msg)
    return "Done"


@app.route('/telegram', methods=['POST'])
def webhook_tg():
    data = request.get_json()
    print('Received {} to TG webhook'.format(data))

    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return "Done"


# yoink send_to_groupme from tech server
def send_to_groupme(username, msg_text):
    print("sending to groupme")
    if username != TG_BOT_USERNAME:
        last_name = "" if username.last_name == None else username.last_name
        first_name = "" if username.first_name == None else username.first_name
        data = {
            'bot_id': GROUPME_BOT_ID,
            'text': first_name + " " + last_name + ": " + msg_text
        }
        to_str = json.dumps(data)
        result = requests.post("https://api.groupme.com/v3/bots/post", 
                      data=to_str)
        print(result.text)

# Message handler for Telegram messages
def tg_msg_handler(update, context):
    # receive message from TG
    message_content = update.message.text
    username = update.message.from_user
    print("Got message from TG!")
    print(update, context)
    # add date manual handling for now......
    if update.message.date.timestamp() < 1616223029: 
        return

    # send to groupme
    send_to_groupme(username, message_content)

def tg_pic_handler(update, context):
    # Receive pic from TG
    sent_pics = set()
    for photo in update.message.photo:
        if photo.file_unique_id in sent_pics:
            continue
        sent_pics.add(photo.file_unique_id)
        pic_id = photo.file_id
        # Get picture
        pic_file = photo.get_file()
        # download to /tmp?
        # just download to current working directory
        file_name = pic_file.download()
        # upload using post
        groupme_post_image(file_name)
        # remove image
        os.remove(file_name)

def groupme_post_image(file_path):
    # open image
    with open(file_path, 'rb') as f:
        data = f.read()

    # send POST request
    result = requests.post("https://api.groupme.com/v3/bots/post", 
                      data=data,
                      headers={'Content-Type': 'image/jpeg', 
                               'X-Access-Token': GROUPME_ACCESS_TOKEN})
    print(result)
    # TODO send to groupme

# Message handler for Groupme messages
def groupme_msg_handler(update, context):
    # create message
    print("Got message from Groupme!")
    msg = update.name + ": " + update.text 
    if update.name == GROUPME_BOT_NAME:
        return
    # send to TG
    context.bot.send_message(chat_id=TG_CHAT_ID, text=msg)

def main():
    app.run()

if __name__ == '__main__':
	main()
