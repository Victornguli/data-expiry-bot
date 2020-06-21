import requests
import os
from bottle import Bottle, request as bottle_request, response

BOT_TOKEN = os.environ.get('token')


class BotHandler:
	BOT_URL = None

	@staticmethod
	def get_chat_id(data):
		"""
		Extracts the chat_id from telegram request
		"""
		chat_id = data['message']['chat']['id']
		return chat_id

	@staticmethod
	def get_message(data):
		"""Extract the message from telegram request"""
		message = data['message']['text']
		return message

	def send_message(self, data):
		"""Sends a message response to the requesting chat_id"""
		url = f"{self.BOT_URL}sendMessage"
		requests.post(url, json = data)

	def send_photo(self, data):
		url = f"{self.BOT_URL}sendPhoto"
		contents = requests.get("http://aws.random.cat/meow").json()
		photo = contents["file"]
		chat_id = data.get("message", {}).get("chat", {}).get("id", "")
		if not chat_id:
			chat_id = data.get("edited_message", {}).get("chat", {}).get("id", "")
		payload = {
			'chat_id': chat_id,
			'photo': photo
		}
		requests.post(url, json = payload)


class TelegramBot(BotHandler, Bottle):
	BOT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

	def __init__(self, *args, **kwargs):
		super().__init__()
		self.route('/', callback = self.post_handler, method = "POST")
		self.route('/hello', callback = self.hello_world, method = "GET")

	@staticmethod
	def hello_world():
		return response("Hello, World!")

	@staticmethod
	def transform_message(text):
		return text[::-1]

	def prepare_response(self, data):
		message = self.get_message(data)
		chat_id = self.get_chat_id(data)
		answer = self.transform_message(message)
		json_response = {
			"chat_id": chat_id,
			"text": answer
		}
		return json_response

	def post_handler(self):
		data = bottle_request.json
		print(data)
		entities = data.get("message", {}).get("entities", "")
		if not entities:
			entities = data.get("edited_message", {}).get("entities", "")
		if entities and entities[0]["type"] == "bot_command":
			command = data.get("message", {}).get("text", "")
			if not command:
				command = data.get("edited_message", {}).get("text", "")
			if command == "/bop":
				self.send_photo(data)
		else:
			data = self.prepare_response(bottle_request.json)
			self.send_message(data)

		return response


if __name__ == "__main__":
	app = TelegramBot()
	app.run(host="localhost", port=8080, debug=True)
