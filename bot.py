import requests
import os
import logging
import json
from datetime import datetime
from bottle import Bottle, request as bottle_request, response
from .db import create_connection, insert

BOT_TOKEN = os.getenv('token')
log_path = os.getenv("LOG_PATH")
logging.basicConfig(level = logging.INFO, filename=os.path.join(log_path, "logs.log"))


class BotHandler:
	BOT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

	@staticmethod
	def get_chat_id(data):
		"""
		Extracts the chat_id from telegram request
		"""
		chat_id = data['message']['chat']['id']
		return chat_id

	def send_message(self, data):
		"""Sends a message response to the requesting chat_id"""
		url = f"{self.BOT_URL}sendMessage"
		res = requests.post(url, json = data)
		logging.info(f"Request to {url} returned status {res.status_code}")


class TelegramBot(BotHandler, Bottle):
	BOT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

	def __init__(self, *args, **kwargs):
		super().__init__()
		self.route('/', callback = self.post_handler, method = "POST")
		self.route('/test', callback = self.hello_world, method = "GET")
		self.PREVIOUS_COMMAND = ""

	@staticmethod
	def hello_world():
		response.content_type = 'text/html; charset=UTF8'
		return u"<h1>Hello, World</h1>"

	def start_command(self, chat_id):
		json_response = {
			"chat_id": chat_id,
			"text": "Welcome to data expiry notification bot.\nTo setup data and get instructions reply with /options"
		}
		self.send_message(json_response)

	def settings_command(self, chat_id):
		reply_keyboard_markup = {
			"keyboard": [["set purchase date"], ["turn off notifications"]],
			"one_time_keyboard": True
		}
		url = f"{self.BOT_URL}sendMessage"
		data = {
			"chat_id": chat_id,
			"text": "Select one of the following options",
			"reply_markup": json.dumps(reply_keyboard_markup)
		}
		res = requests.post(url, data)
		logging.info(f"Request to {url} returned status {res.status_code}")
		if res.status_code != 200:
			logging.error(f"Request to {url} returned {res.text}")

	def set_purchase_date(self, time_str, chat_id):
		"""Sets new purchase datetime"""
		data = {}
		try:
			now = datetime.now()
			time = datetime.strptime(time_str, "%H:%M")
			purchase_date = datetime(now.year, now.month, now.day, time.hour, time.minute, 0, 0)
		except Exception as ex:
			logging.error(f"Failed to parse time string {time_str}")
			logging.error(str(ex))
		else:
			data = {
				"chat_id": chat_id,
				"text": f"Successfully saved new purchase {purchase_date}"
			}
			try:
				conn = create_connection()
				insert(conn, purchase_date = purchase_date)
				conn.close()
			except Exception as ex:
				logging.error(str(ex))
		if not data:
			data = {
				"chat_id": chat_id,
				"text": f"Failed to parse {time_str}"
			}
		self.PREVIOUS_COMMAND = ""
		self.send_message(data)
		# conn = create_connection()

	def post_handler(self):
		data = bottle_request.json
		print(data)
		chat_id = self.get_chat_id(data)
		entities = data.get("message", {}).get("entities", "")
		if entities and entities[0]["type"] == "bot_command":
			command = data.get("message", {}).get("text", "")
			if command == "/start":
				self.start_command(chat_id)
			elif command == "/options":
				self.settings_command(chat_id)
		else:
			message = data.get("message", {}).get("text", "")
			if message == "set purchase date":
				self.PREVIOUS_COMMAND = "set_purchase_date"
			elif self.PREVIOUS_COMMAND == "set_purchase_date":
				self.set_purchase_date(message, chat_id)
			else:
				data = {
					"chat_id": chat_id,
					"text": "Unrecognized chatter.\nRespond with /settings."
				}
				self.send_message(data)

		return response


"""
Uncomment to run on localhost or on WSGIRefServer. 
Application is exported to enable it to run on a mod_wsgi server instead.
"""

# if __name__ == "__main__":
# 	app = TelegramBot()
# 	app.run(host="localhost", port=8080, debug=True)


def app():
	return TelegramBot()

