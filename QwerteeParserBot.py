#!/usr/bin/python
# -*- coding: utf-8 -*-

import telegram
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from bs4 import BeautifulSoup
import logging
import configparser
import urllib.request, urllib.error, urllib.parse
from datetime import datetime, time

#Class for Qwertee Shirt element
class Qwertee_Tee:
	name = "Unknown name"
	price = 0
	picture_link = ""

#/start command
def start(update, context):

	#send personalized welcome message to user (if user got a username), else send default welcome message
	if update.message.from_user.username is not None:
		context.bot.sendMessage(chat_id=update.message.chat_id, text="Hi "+str(update.message.from_user.username)+", i am a bot for parsing qwertee.com for daily offers.\nTo get a list of my commands please send me  a /help message.")
	else:
		context.bot.sendMessage(chat_id=update.message.chat_id, text="Hi, i am a bot for parsing qwertee.com for daily offers.\nTo get a list of my commands please send me  a /help message.")

	#out user details
	logging.info("User: %s - chat_id: %s", str(update.message.from_user.username), update.message.chat_id)


#/get command; get current offers from website
def get(update, context):
	context.bot.sendMessage(chat_id=update.message.chat_id, text="Parsing qwertee.com ...")
	
	qwertee_tees = parse_qwertee()

	if qwertee_tees is not None:
		for s in qwertee_tees:
			logging.info("Got %s for %s€ (%s)", s.name, s.price, s.picture_link)
			context.bot.send_photo(chat_id=update.message.chat_id, photo=s.picture_link)
			context.bot.send_message(chat_id=update.message.chat_id, text=s.name+" - "+s.price+" Euro.")
	else:
		context.bot.sendMessage(chat_id=update.message.chat_id, text="Error parsing qwertee.com. Sorry :(")
	
#/register command; register a user for daily notifications
def register(update, context):
	context.bot.sendMessage(chat_id=update.message.chat_id, text="Registering...")

	# get set of chat_id from registered users in file \"notification_user\"
	notification_set = set(line.strip() for line in open('notification_user', 'r'))

	if notification_set is not None:

		# test if chat_id is already in set
		if str(update.message.chat_id) in notification_set:
			# notify user that he is already registered
			context.bot.sendMessage(chat_id=update.message.chat_id, text="You are already registered for the daily notifications.\nIf you'd like to unregister, please send me the /unregister command.")
		else:
			# new chat_id, add to set
			notification_set.add(update.message.chat_id)

			logging.info("Adding user %s (ID %s) to file", str(update.message.from_user), str(update.message.chat_id))

			# overwrite file
			notification_file = open('notification_user', 'w')
			if notification_file is not None:
				# write to file
				for chat_id in notification_set:
					notification_file.write("%s\n" % chat_id)
				notification_file.close()
				
				#notify user about successfully registering
				context.bot.sendMessage(chat_id=update.message.chat_id, text="You are now registered for the daily notification.")
				
			else:
				# notify user about internal error
				context.bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, but there was an internal error while registering...")
	else:
		context.bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, but there was an internal error while registering...")


#/unregister command; unregister a user for daily notifications
def unregister(update, context):
	context.bot.sendMessage(chat_id=update.message.chat_id, text="Unregistering...")

	# get set of chat_id from registered users in file \"notification_user\"
	notification_set = set(line.strip() for line in open('notification_user', 'r'))

	if notification_set is not None:

		# test if chat_id is already in set
		if str(update.message.chat_id) in notification_set:
			# delete chat_id from set
			notification_set.remove(str(update.message.chat_id))

			logging.info("Deleting user %s (ID %s) from file", str(update.message.from_user), str(update.message.chat_id))

			# write updated set back to file
			notification_file = open('notification_user', 'w')
			if notification_file is not None:
				# write to file
				for chat_id in notification_set:
					notification_file.write("%s\n" % chat_id)
				notification_file.close()
				
				#notify user about successfully registering
				context.bot.sendMessage(chat_id=update.message.chat_id, text="You are not longer registered for the daily notification.")
				
			else:
				# notify user about internal error
				context.bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, but there was an internal error while unregistering...")
		else:
			# notify user that he is not registered
			context.bot.sendMessage(chat_id=update.message.chat_id, text="It seems that you are not registered for the daily notification yet.\nIf you'd like to register, please send me the /register command.")			
	else:
		context.bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, but there was an internal error while unregistering...")


#unknown command
def unknown(update, context):
	context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, i don't know this command :(")
	help(update, context)

#help command; print list of commands
def help(update, context):
	context.bot.send_message(chat_id=update.message.chat_id, text="Here's a list of my current known commands.")
	context.bot.send_message(chat_id=update.message.chat_id, text="/get - Get current offers from qwertee.com")
	context.bot.send_message(chat_id=update.message.chat_id, text="/register - Register yourself for the daily Qwertee notification")
	context.bot.send_message(chat_id=update.message.chat_id, text="/unregister - Unregister yourself from the daily Qwertee notification")	
	

def parse_qwertee():
	#Start parsing qwertee.com

	logging.info("QwerteeBot - Polling for https://www.qwertee.com...")

	return_list_Qwertee_Tees = []

	#Open file
	file = open('qwertee.html', 'r')
	soup = BeautifulSoup(file, 'html.parser')
	
	#get div with class "big-slides-wrap"
	big_slides_wrap = soup.find("div", class_="big-slides-wrap")
	
	if big_slides_wrap is None:
		logging.warning("Could not find a div of class \"big-slide-wrap\"")
		return None
		
	# Get div with id "big-slide tee tee-last-chance"
	find = big_slides_wrap.find_all("div", class_="big-slide tee tee-last-chance")
	if find is None:
		logging.warning("Could not find a element of class \"big-slide tee tee-last-chance\"")
		return None

	for limited_tee_wrap in find:
	
		index_tee = limited_tee_wrap.find("div", class_="index-tee")
	
		if index_tee is None:
			logging.warning("Could not find a element of class \"index-tee\"")
			return None
	
		#Save name and price of tee
		tee_name = index_tee["data-name"]
		tee_price = index_tee["data-tee-price-eur"]
	
		# Get children-div with class "buy-wrap"
		find2 = limited_tee_wrap.find("div", class_="buy-wrap")
		
		if find2 is None:
			logging.warning("Could not find a element of class \"buy-wrap\"")
			return None
		# Get children-div with class "buy"
		find3 = find2.find("div", class_="buy")

		if find3 is None:
			logging.warning("Could not find a element of class \"buy\"")
			return None

		# Get children-div with class "design-dynamic-image-wrap"
		find4 = find3.find("div", class_="design-dynamic-image-wrap")

		if find4 is None:
			logging.warning("Could not find a element of class \"design-dynamic-image-wrap\"")
			return None

		# Get children-div with class "mens-dynamic-image design-dynamic-image"
		find5 = find4.find("div", class_="mens-dynamic-image design-dynamic-image")

		if find5 is None:
			logging.warning("Could not find a element of class \"mens-dynamic-image design-dynamic-image\"")
			return None
	
		# Get children with tag "picture"
		find6 = find5.find("picture")

		if find6 is None:
			logging.warning("Could not find a element of tag \"picture\"")
			return None
	
		# Get children with tag "img"
		find6 = find5.find("img")

		if find6 is None:
			logging.warning("Could not find a element of tag \"img\"")
			return None

		tee_picture_link = find6["src"]
		if tee_picture_link is None:
			logging.warning("Could not find the link to the picture of tee %s", str(tee_name))
			return None

		#Got all i need, print the infos and add it to the return list 
		logging.info("Limitiertes Tee: %s fuer %s€", tee_name, tee_price)
		
		#Create Tee object
		tmp_tee_obj = Qwertee_Tee()
		tmp_tee_obj.name = tee_name
		tmp_tee_obj.price = tee_price
		tmp_tee_obj.picture_link = tee_picture_link

		return_list_Qwertee_Tees.append(tmp_tee_obj)



	#Return list of Tee objects
	return return_list_Qwertee_Tees

def fetch_website():
	url = 'http://www.qwertee.com'

	user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
	headers={'User-Agent':user_agent,} 

	req = urllib.request.Request(url, headers=headers)
	response = urllib.request.urlopen(req)
	webContent = response.read()

	f = open('qwertee.html', 'wb')
	f.write(webContent)
	f.close


#routine to send notification to all registered users
def send_notification(context):

	fetch_website()

	logging.info("Sending notifications")

	qwertee_tees = parse_qwertee()

	if qwertee_tees is not None:
		# get set of chat_id from registered users in file \"notification_user\"
		notification_set = set(line.strip() for line in open('notification_user', 'r'))
		
		for chat_id in notification_set:
			# notify user
			logging.info("Notify user with ID %s", chat_id)
			context.bot.send_message(chat_id=chat_id, text="New offers from qwertee.com")

			for s in qwertee_tees:
				context.bot.send_photo(chat_id=chat_id, photo=s.picture_link[2:])
				context.bot.send_message(chat_id=chat_id, text=s.name+" - "+s.price+" Euro.")

def main():

	#Logging-stuff
	logging.basicConfig(filename="QwerteeParserBot.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

	logging.info("QwerteeParserBot started.")

	# Create file for user list if not exist
	tmp_file = open('notification_user', 'a')
	tmp_file.close()

	# Get telegram API token and chat_id of bot owner from file ".bot_credentials"
	telegram_config = configparser.ConfigParser()
	telegram_config.read("./.bot_credentials")
	telegram_bot_token = telegram_config.get("configuration", "bot_token")
	telegram_bot_owner_chat_id = telegram_config.get("configuration", "bot_owner_chat_id")

 	#
	# Set up connection to Telegram-API
	#
	QwerteeBotUpdater = Updater(token=telegram_bot_token, use_context=True)
	QwerteeBotDispatcher = QwerteeBotUpdater.dispatcher
	QwerteeBot = QwerteeBotUpdater.bot

	# Notify bot owner that bot has started
	QwerteeBot.send_message(chat_id=telegram_bot_owner_chat_id, text="QwerteeParserBot was started at " + datetime.now().strftime('%d.%m.%y (%a) at %H:%M:%S'))

	#
	#register commands
	#

	#/start
	startHandler = CommandHandler('start', start)
	QwerteeBotDispatcher.add_handler(startHandler)

	#/help
	helpHandler = CommandHandler('help', help)
	QwerteeBotDispatcher.add_handler(helpHandler)
	
	#/get
	getHandler = CommandHandler('get', get)
	QwerteeBotDispatcher.add_handler(getHandler)
	
	#register
	registerHandler = CommandHandler('register', register)
	QwerteeBotDispatcher.add_handler(registerHandler)

	#unregister
	unregisterHandler = CommandHandler('unregister', unregister)
	QwerteeBotDispatcher.add_handler(unregisterHandler)

	#unknown command, must be added last!
	unknownHandler = MessageHandler(Filters.command, unknown)
	QwerteeBotDispatcher.add_handler(unknownHandler)

	logging.info("Commands registered.")
	
	#initial download of page
	fetch_website()
	
	#call function every day at 09:00
	job_queue = QwerteeBotUpdater.job_queue
	job_queue.run_daily(send_notification, time(9, 00, 00))

	#Run bot	
	QwerteeBotUpdater.start_polling()
	QwerteeBotUpdater.idle()

if __name__ == '__main__':
	main()
