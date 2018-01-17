# QwerteeParser
A telegram bot for parsing http://www.qwertee.com for daily offers. 

Using:
-[Telegram python wrapper](https://github.com/python-telegram-bot/python-telegram-bot) 
-[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

The telegram API-Token is read from the file .bot_credentials.
This file should have the following syntax

```
[configuration]
bot_token = <your-API-token>
bot_owner_chat_id = <chat_id_of_bot_owner>
```


