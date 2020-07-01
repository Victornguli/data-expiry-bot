import requests
import os
import logging
import json
from datetime import datetime
from bottle import Bottle, request as bottle_request, response
from notify.db import create_connection, insert, get_status
from notify.scripts.cron import update_call_time

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
		self.settings_command(chat_id)

	def settings_command(self, chat_id, text = "Use the following commands to interact with me"):
		conn = create_connection()
		status = get_status(conn)
		notifications = "turnoff" if status[1] else "turnon"
		reply_keyboard_markup = {
			"keyboard": [
				["set purchase date"], [f"{notifications} notifications"], ["/status"],
				["set notification time"]],
			"one_time_keyboard": True
		}
		url = f"{self.BOT_URL}sendMessage"
		data = {
			"chat_id": chat_id,
			"text": text,
			"reply_markup": json.dumps(reply_keyboard_markup)
		}
		res = requests.post(url, data)
		logging.info(f"Request to {url} returned status {res.status_code}")
		if res.status_code != 200:
			logging.error(f"Request to {url} returned {res.text}")

	def set_purchase_date(self, time_str, chat_id):
		"""Sets new purchase datetime"""
		data = {}
		purchase_date = None
		try:
			now = datetime.now()
			time = datetime.strptime(time_str, "%H:%M")
			purchase_date = datetime(now.year, now.month, now.day, time.hour, time.minute, 0, 0)
		except Exception as ex:
			try:
				purchase_date = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
			except Exception:
				pass
			logging.error(f"Failed to parse time string {time_str}")
			logging.error(str(ex))
		if purchase_date:
			try:
				conn = create_connection()
				insert(conn, purchase_date = purchase_date)
				conn.close()
			except Exception as ex:
				logging.error(str(ex))
				data = {
					"chat_id": chat_id,
					"text": f"Failed to set new purchase date: {purchase_date}.\
					\nUse the command /options to select the option again."
				}
			else:
				data = {
					"chat_id": chat_id,
					"text": f"Successfully set new purchase date: {purchase_date}"
				}
		if not data:
			data = {
				"chat_id": chat_id,
				"text": f"Failed to parse {time_str}.\nUse the command /options to select the option again."
			}
		self.PREVIOUS_COMMAND = ""
		self.send_message(data)
		# conn = create_connection()

	def set_notification_time(self, time, chat_id):
		"""Sets new notification time, especially if purchase date has been updated"""
		data = {
			"chat_id": chat_id,
			"text": 'Failed to update notification script call time'
		}
		try:
			time = datetime.strptime(time, "%H:%M")
			update_call_time(time.hour, time.minute)
		except ValueError as e:
			logging.error(f'Failed to parse the time string {time}')
			logging.error(str(e))
			data['text'] = f'Failed to parse time string {time}'
		except Exception as ex:
			logging.error(f'Failed to update notification script call time')
			logging.error(str(ex))

		self.PREVIOUS_COMMAND = ""
		self.send_message(data)

	def status_command(self, chat_id):
		conn = create_connection()
		status = get_status(conn)
		previous_date = f"{status[0]}" if status[0] else "N/A"
		notification_status = "ON" if status[1] else "OFF"
		if status[0]:
			res = f"Previous purchase date is: {previous_date}.\nNotifications are turned {notification_status}"
		else:
			res = f"No purchase date was found.\nFollow commands at /options to set a new one."
		self.send_message({"chat_id": chat_id, "text": res})
		conn.close()

	def toggle_notifications(self, chat_id, status = 0):
		conn = create_connection()
		data = {"chat_id": chat_id}
		notification_status = "ON" if status else "OFF"
		try:
			insert(conn, notifications_on = status)
			data["text"] = f"Successfully changed notification status to {notification_status}"
		except Exception as ex:
			logging.info("Failed to change notification status")
			logging.info(str(ex))
			data["text"] = f"Failed to change notification status to {notification_status}"
		self.send_message(data)
		self.settings_command(chat_id, text = "Use options in main menu for more commands")
		conn.close()

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
			elif command == "/status":
				self.status_command(chat_id)
		else:
			message = data.get("message", {}).get("text", "")
			if message == "turnoff notifications":
				self.toggle_notifications(chat_id, status = 0)
			elif message == "turnon notifications":
				self.toggle_notifications(chat_id, status = 1)
			elif message == "set purchase date":
				self.PREVIOUS_COMMAND = "set_purchase_date"
			elif message == "set notification time":
				self.PREVIOUS_COMMAND = "set_notification_time"
			elif self.PREVIOUS_COMMAND == "set_notification_time":
				self.set_notification_time(message, chat_id)
			elif self.PREVIOUS_COMMAND == "set_purchase_date":
				self.set_purchase_date(message, chat_id)
			else:
				data = {
					"chat_id": chat_id,
					"text": "Unrecognized chatter.\nRespond with /options."
				}
				self.send_message(data)

		return response


"""
Uncomment to run on localhost or on WSGIRefServer. 
Application is exported to enable it to run on a mod_wsgi server instead.
"""

if __name__ == "__main__":
	app = TelegramBot()
	app.run(host="localhost", port=8080, debug=True)


def app():
	return TelegramBot()

