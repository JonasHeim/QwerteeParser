# QwerteeParser
A telegram bot for parsing [http://www.qwertee.com](http://www.qwertee.com) for daily offers. 

Using:
- [Telegram python wrapper](https://github.com/python-telegram-bot/python-telegram-bot) 
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

The telegram API-Token is read from the file .bot_credentials.
This file should have the following syntax

```
[configuration]
bot_token = <your-API-token>
bot_owner_chat_id = <chat_id_of_bot_owner>
```

The bot can notify all registered user automatically (default once per day at 09:00 AM) about the offers.

When registering, the chat_id of the user is saved to a set (unique); and when unregistering the chat_id will be deleted.

Current implemented commands:
- /start
  Welcome the user and send a list of current available commands.
- /help
  Response with a list of current available commands.
- /get
  Response with the current offers from [Qwertee](http://www.qwertee.com)
- /register
  Register a new user for the daily notification about the offers
- /unregister
  Unregister a new user from the daily notification about the offers

Planned:
/



