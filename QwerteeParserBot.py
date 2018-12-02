#!/usr/bin/python
# -*- coding: utf-8 -*-

import telegram
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from bs4 import BeautifulSoup
import subprocess
import logging
import sys
import ConfigParser
import sched
import time
from datetime import datetime as dt
import datetime

#Class for Qwertee Shirt element
class Qwertee_Tee:
	name = "Unknown name"
	price = 0
	picture_link = ""

#Logging-stuff
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

#/start command
def start(bot, update):

	#send personalized welcome message to user (if user got a username), else send default welcome message
	if update.message.from_user.username is not None:
		bot.sendMessage(chat_id=update.message.chat_id, text="Hi "+str(update.message.from_user.username)+", i am a bot for parsing qwertee.com for daily offers.\nTo get a list of my commands please send me  a /help message.")
	else:
		bot.sendMessage(chat_id=update.message.chat_id, text="Hi, i am a bot for parsing qwertee.com for daily offers.\nTo get a list of my commands please send me  a /help message.")

	#print out user details
	print "User: ",str(update.message.from_user.username)," - chat_id: ",update.message.chat_id


#/get command; get current offers from website
def get(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="Parsing qwertee.com ...")
	
	qwertee_tees = parse_qwertee()

	if qwertee_tees is not None:
		for s in qwertee_tees:
			print "Got ", s.name, ", ", s.price, ", and ", s.picture_link
			bot.send_photo(chat_id=update.message.chat_id, photo=s.picture_link[2:])
			bot.send_message(chat_id=update.message.chat_id, text=s.name+" - "+s.price+" Euro.")
	else:
		bot.sendMessage(chat_id=update.message.chat_id, text="Error parsing qwertee.com. Sorry :(")
	
#/register command; register a user for daily notifications
def register(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="Registering...")

	# get set of chat_id from registered users in file \"notification_user\"
	notification_set = set(line.strip() for line in open('notification_user', 'r'))

	if notification_set is not None:

		# test if chat_id is already in set
		if str(update.message.chat_id) in notification_set:
			# notify user that he is already registered
			bot.sendMessage(chat_id=update.message.chat_id, text="You are already registered for the daily notifications.\nIf you'd like to unregister, please send me the /unregister command.")
		else:
			# new chat_id, add to set
			notification_set.add(update.message.chat_id)

			print "Adding user ",update.message.chat_id, " to file."

			# overwrite file
			notification_file = open('notification_user', 'w')
			if notification_file is not None:
				# write to file
				for chat_id in notification_set:
					print "Write chat_id ",chat_id," to file."
					notification_file.write("%s\n" % chat_id)
				notification_file.close()
				
				#notify user about successfully registering
				bot.sendMessage(chat_id=update.message.chat_id, text="You are now registered for the daily notification.")
				
			else:
				# notify user about internal error
				bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, but there was an internal error while registering...")
	else:
		bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, but there was an internal error while registering...")


#/unregister command; unregister a user for daily notifications
def unregister(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="Unregistering...")

	# get set of chat_id from registered users in file \"notification_user\"
	notification_set = set(line.strip() for line in open('notification_user', 'r'))

	if notification_set is not None:

		# test if chat_id is already in set
		if str(update.message.chat_id) in notification_set:
			# delete chat_id from set
			notification_set.remove(str(update.message.chat_id))

			print "Deleting user ",update.message.chat_id," from file."

			# write updated set back to file
			notification_file = open('notification_user', 'w')
			if notification_file is not None:
				# write to file
				for chat_id in notification_set:
					print "Write chat_id ",chat_id," to file."
					notification_file.write("%s\n" % chat_id)
				notification_file.close()
				
				#notify user about successfully registering
				bot.sendMessage(chat_id=update.message.chat_id, text="You are not longer registered for the daily notification.")
				
			else:
				# notify user about internal error
				bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, but there was an internal error while unregistering...")
		else:
			# notify user that he is not registered
			bot.sendMessage(chat_id=update.message.chat_id, text="It seems that you are not registered for the daily notification yet.\nIf you'd like to register, please send me the /register command.")			
	else:
		bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, but there was an internal error while unregistering...")


#unknown command
def unknown(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Sorry, i don't know this command :(\nHere's a list of my current known commands.")
	bot.send_message(chat_id=update.message.chat_id, text="/get - Get current offers from qwertee.com")
	bot.send_message(chat_id=update.message.chat_id, text="/register - Register yourself for the daily Qwertee notification")
	bot.send_message(chat_id=update.message.chat_id, text="/unregister - Unregister yourself from the daily Qwertee notification")	

#help command; print list of commands
def help(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Here's a list of my current known commands.")
	bot.send_message(chat_id=update.message.chat_id, text="/get - Get current offers from qwertee.com")
	bot.send_message(chat_id=update.message.chat_id, text="/register - Register yourself for the daily Qwertee notification")
	bot.send_message(chat_id=update.message.chat_id, text="/unregister - Unregister yourself from the daily Qwertee notification")	
	

def parse_qwertee():
	#Start parsing qwertee.com

	print "QwerteeBot - Polling for https://www.qwertee.com..."

	return_list_Qwertee_Tees = []

	#Open file
	file = open('qwertee.html', 'r')
	soup = BeautifulSoup(file, 'html.parser')
	
	#get div with class "big-slides-wrap"
	big_slides_wrap = soup.find("div", class_="big-slides-wrap")
	
	if big_slides_wrap is None:
		print "Could not find a div of class \"big-slide-wrap\""
		#Remove file
		subprocess.call(['./rmSite.sh'])
		sys.exit(1)
	
	#print "Found a div of class \"big-slide-wrap\""
	
	# Get div with id "big-slide tee tee-last-chance"
	find = big_slides_wrap.find_all("div", class_="big-slide tee tee-last-chance")
	if find is None:
		print "Could not find a element of class \"big-slide tee tee-last-chance\""
		#Remove file
		subprocess.call(['./rmSite.sh'])
		sys.exit(1)
	
	#print "Found a div of class \"big-slide tee tee-last-chance\""
	
	#Iterate through all items of this class and get the picture source link
	#print "Got ",len(find)," elements"

	for limited_tee_wrap in find:
	
		index_tee = limited_tee_wrap.find("div", class_="index-tee")
	
		if index_tee is None:
			print "Could not find a element of class \"index-tee\""
			#Remove file
			subprocess.call(['./rmSite.sh'])
			sys.exit(1)
	
		#print "Found a div of class \"index-tee\""
	
		#Save name and price of tee
		tee_name = index_tee["data-name"]
		tee_price = index_tee["data-tee-price-eur"]
	
		# Get children-div with class "buy-wrap"
		find2 = limited_tee_wrap.find("div", class_="buy-wrap")
		
		if find2 is None:
			print "Could not find a element of class \"buy-wrap\""
			#Remove file
			subprocess.call(['./rmSite.sh'])
			sys.exit(1)
	
		#print "Found a div of class \"buy-wrap\""

		# Get children-div with class "buy"
		find3 = find2.find("div", class_="buy")

		if find3 is None:
			print "Could not find a element of class \"buy\""
			#Remove file
			subprocess.call(['./rmSite.sh'])
			sys.exit(1)

		#print "Found a div of class \"buy\""

		# Get children-div with class "design-dynamic-image-wrap"
		find4 = find3.find("div", class_="design-dynamic-image-wrap")

		if find4 is None:
			print "Could not find a element of class \"design-dynamic-image-wrap\""
			#Remove file
			subprocess.call(['./rmSite.sh'])
			sys.exit(1)
	
		#print "Found a div of class \"design-dynamic-image-wrap\""

		# Get children-div with class "mens-dynamic-image design-dynamic-image"
		find5 = find4.find("div", class_="mens-dynamic-image design-dynamic-image")

		if find5 is None:
			print "Could not find a element of class \"mens-dynamic-image design-dynamic-image\""
			#Remove file
			subprocess.call(['./rmSite.sh'])
			sys.exit(1)
	
		#print "Found a div of class \"mens-dynamic-image design-dynamic-image\""

		# Get children with tag "picture"
		find6 = find5.find("picture")

		if find6 is None:
			print "Could not find a element of tag \"picture\""
			#Remove file
			subprocess.call(['./rmSite.sh'])
			sys.exit(1)
	
		#print "Found a element of tag \"picture\""

		# Get children with tag "img"
		find6 = find5.find("img")

		if find6 is None:
			print "Could not find a element of tag \"img\""
			#Remove file
			subprocess.call(['./rmSite.sh'])
			sys.exit(1)
	
		#print "Found a element of tag \"img\""

		tee_picture_link = find6["src"]
		if tee_picture_link is None:
			print "Could not find the link to the picture of tee ", tee_name
			#Remove file
			subprocess.call(['./rmSite.sh'])
			sys.exit(1)
		
		tmp_tee_picture_link_name = tee_picture_link.split("/")
		tee_picture_link_name = tmp_tee_picture_link_name[len(tmp_tee_picture_link_name)-1]

		#Got all i need, print the infos and add it to the return list 
		print "Limitiertes Tee: ", tee_name, " fuer ", tee_price, "Euro."
		
		#Create Tee object
		tmp_tee_obj = Qwertee_Tee()
		tmp_tee_obj.name = tee_name
		tmp_tee_obj.price = tee_price
		tmp_tee_obj.picture_link = tee_picture_link

		return_list_Qwertee_Tees.append(tmp_tee_obj)



	#Return list of Tee objects
	return return_list_Qwertee_Tees

def main():

	#routine to send notification to all registered users
	def send_notification(bot, job):
	
		#Delete old html file
		print "Deleting old .html file"
		subprocess.call(['./rmSite.sh'])

		print "Loading qwertee.com"

		#Get website to file
		print "Loading new .html file"
		subprocess.call(['./getSite.sh'])
	
		print "Sending notification..."
	
		qwertee_tees = parse_qwertee()

		if qwertee_tees is not None:
			# get set of chat_id from registered users in file \"notification_user\"
			notification_set = set(line.strip() for line in open('notification_user', 'r'))
			
			for chat_id in notification_set:
				# notify user
				bot.send_message(chat_id=chat_id, text="New offers from qwertee.com")

				for s in qwertee_tees:
					print "Got ", s.name, ", ", s.price, ", and ", s.picture_link
					bot.send_photo(chat_id=chat_id, photo=s.picture_link[2:])
					bot.send_message(chat_id=chat_id, text=s.name+" - "+s.price+" Euro.")

	#
	# Get Bot credentials from external file  ".bot_credentials"
	#

	telegram_config = ConfigParser.ConfigParser()
	telegram_config.read("./.bot_credentials")
	telegram_bot_token = telegram_config.get("configuration", "bot_token")

	#
	# Get chat_id of owner of the bot from external file ".bot_credentials"
	#

	telegram_bot_owner_chat_id = telegram_config.get("configuration", "bot_owner_chat_id")

 	#
	# Set up connection to Telegram-API
	#

	QwerteeBotUpdater = Updater(token=telegram_bot_token)
	QwerteeBotDispatcher = QwerteeBotUpdater.dispatcher
	QwerteeBot = QwerteeBotUpdater.bot

	#
	# Notify bot owner that bot has started
	#

	QwerteeBot.send_message(chat_id=telegram_bot_owner_chat_id, text="QwerteeParserBot was started.")
	
		
	#	
	#Get .html file from qwertee.com
	#

	subprocess.call(['./getSite.sh'])

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
	
	#
	#set up timer for cyclic parsing
	#
	job_queue = QwerteeBotUpdater.job_queue
	#call function every day at 09:00
	job_daily_notification = job_queue.run_daily(send_notification, datetime.time(hour=9, minute=0, second=0))

	#
	#Run bot
	#
	
	QwerteeBotUpdater.start_polling()

	QwerteeBotUpdater.idle()


if __name__ == '__main__':
	main()
