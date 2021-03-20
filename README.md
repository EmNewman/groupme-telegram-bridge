# groupme-telegram-bridge
Bridge between Groupme and Telegram.

Simple Flask app that uses webhooks to connect Groupme to Telegram and vice versa.
Currently supports bridging only one chat on TG to one chat on Groupme. Multi-chat support may be added in the future. For now, if you want to bridge multiple chats you will need multiple deployments. 
Currently only supports text communication. Images, stickers TBD.

# Installation
Your milage may vary based on where you are hosting the app. It's been successfully hosted on Heroku and on an Apache server. Wherever you host it, you should follow instructions for hosting a Flask app (since that's what this is). 
Guidelines for these may be written at some point. 

## Requirements
Python 3 is required.
The three external packages used are: 
* [Flask](https://flask.palletsprojects.com/en/1.1.x/)
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
* [requests](https://pypi.org/project/requests/). 

## Dev Setup
`pyvenv` is the preferred environment for development. 

Clone the repository using `git clone`, then

```
$ cd groupme_telegram_bridge
$ python -m venv pyvenv # You may have to replace python with python3 depending on your setup
$ source pyvenv/bin/activate
$ pip install -r requirements.txt
```

You will also need to update the .env file:
```
$ cp dotenv_template .env
```
Then use the editor of your choice to update the .env file with your settings. 
Once that's done, run
```
$ source .env
```
to get all the environment variables set up. 

To run the development server, make sure the pyvenv is activated, then run: 
```
$ python app.py
```

Of course, it will not bridge your group chats if it is running on localhost. 
I've found it easiest to test using Heroku. 

## Heroku Setup 
TBD





