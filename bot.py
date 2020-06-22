import requests
import os
import logging
from bottle import Bottle, request as bottle_request, response

BOT_TOKEN = os.getenv('token')

logging.basicConfig(level = logging.INFO)


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

	@staticmethod
	def hello_world():
		response.content_type = 'text/html; charset=UTF8'
		return u"<h1>Hello, World</h1>"

	def start_command(self, chat_id):
		json_response = {
			"chat_id": chat_id,
			"text": "Welcome to Data expiry bot.\nTo setup data and get instructions reply with /settings"
		}
		self.send_message(json_response)

	def settings_command(self, chat_id):
		keyboard = ["set purchase date", "turn off notifications"]
		url = f"{self.BOT_URL}replyKeyboardMarkup?keyboard={keyboard}&resize_keyboard=true&on_time_keyboard=true"
		data = {
			"chat_id": chat_id,
			"text": "Select one of the following options",
		}
		res = requests.post(url, data)
		logging.info(f"Request to {url} returned status {res.status_code}")

	def post_handler(self):
		data = bottle_request.json
		print(data)
		chat_id = self.get_chat_id(data)
		entities = data.get("message", {}).get("entities", "")
		if entities and entities[0]["type"] == "bot_command":
			command = data.get("message", {}).get("text", "")
			if command == "/start":
				self.start_command(chat_id)
		else:
			data = {
				"chat_id": chat_id,
				"text": "Unrecognized chatter buddy.\nRespond with /settings."
			}
			self.send_message(data)

		return response


if __name__ == "__main__":
	app = TelegramBot()
	app.run(host="localhost", port=8080, debug=True)

# application = TelegramBot()
