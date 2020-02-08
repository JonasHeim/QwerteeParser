# QwerteeParser
A telegram bot for parsing [http://www.qwertee.com](http://www.qwertee.com) for daily offers. 

## Installation
Python 3 required.
Run pip on the requirements.txt file
```
pip install -r requirements.txt
```

Run the bot via
```
python QwerteeParserBot.py
```
## Description
Using:
- [Telegram python wrapper](https://github.com/python-telegram-bot/python-telegram-bot) 
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

The telegram API-Token is read from the file *.bot_credentials*.\
Edit *.bot_credentials_template* to match your credentials and rename to *.bot_credentials*.
```
[configuration]
bot_token = <your-API-token>
bot_owner_chat_id = <chat_id_of_bot_owner>
```

The bot will notify all registered user automatically (default once per day at 09:00 AM) about the offers.\
When registering, the unique chat_id of the user is saved to a file and deleted when unregistering.

Current implemented commands:
| Command | Description |
| ------- | ----------- |
| /start | Welcome the user and send a list of current available commands |
| /help | Response with a list of current available commands |
| /get | Response with the current offers from [Qwertee](http://www.qwertee.com) |
| /register | Register a new user for the daily notification about the offers |
| /unregister | Unregister a new user from the daily notification about the offers |
