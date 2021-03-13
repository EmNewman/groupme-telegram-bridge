import logging
import secrets
import requests
from telegram import Bot
from telegram.ext import MessageHandler, TypeHandler, Filters, Dispatcher
# from groupy import Client

# let's use flask
from flask import Flask, request 

app = Flask(__name__)

# set up groupme
# client = Client.from_token(secrets.GROUPME_API_TOKEN)

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


@app.route('/telegram', methods=['POST'])
def webhook_tg():
    data = request.get_json()
    print('Received {} to TG webhook'.format(data))

    Update.de_json(json.loads(data), bot)
    dispatcher.process_update(update)



# yoink send_to_groupme from tech server
def send_to_groupme(username, msg_text):
    if username != secrets.TG_BOT_USERNAME:
        requests.post("https://api.groupme.com/v3/bots/post", 
                      data={'bot_id': secrets.GROUPME_BOT_ID,
                            'text': username + ": " + msg_text
        })

# Message handler for Telegram messages
def tg_msg_handler(update, context):
    # receive message from TG
    message_content = update.message.text
    username = update.message.from_user
    # send to groupme
    send_to_groupme(username, msg_text)

# Message handler for Groupme messages
def groupme_msg_handler(update, context):
    # create message
    msg = update.name + ": " + update.text 
    if update.user_id == secrets.GROUPME_BOT_ID:
        return
    # send to TG
    context.bot.send_message(chat_id=secrets.TG_CHAT_ID, text=msg)



def setup_tg(token):
    bot = Bot(token)
    dispatcher = Dispatcher(bot, None, workers=0)
    return dispatcher

# set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                 level=logging.INFO)
# setup tg
dispatcher = setup_tg(secrets.TG_BOT_API_TOKEN)
# TODO add photo handling, see here: 
# https://python-telegram-bot.readthedocs.io/en/latest/telegram.message.html#telegram.Message 
tg_text_handler = MessageHandler(Filters.text & (~Filters.command), tg_msg_handler)
dispatcher.add_handler(tg_text_handler)

# custom handler for receiving Groupme messages
groupme_handler = TypeHandler(GroupmeMessage, groupme_msg_handler)
dispatcher.add_handler(groupme_handler)





def main():
    app.run()


if __name__ == '__main__':
	main()