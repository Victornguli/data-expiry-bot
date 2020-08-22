import logging
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load env since this is run outside wsgi environment
root = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(os.path.dirname(root), ".env"))

from notify.db import create_connection, get_latest_record, calculate_expiry_date, insert
from notify.scripts.cron import update_call_time
from notify.scripts.telkom_account import TelkomAccountManager


log_path = os.getenv("LOG_PATH") or os.getenv('LOG_PATH')
TOKEN = os.getenv('token') or os.getenv('TOKEN')
CHAT_ID = os.getenv('chat_id') or os.getenv('CHAT_ID')
logging.basicConfig(level = logging.INFO, filename = os.path.join(log_path, "logs.log"))


def send_message(text):
	bot_url = f"https://api.telegram.org/bot{TOKEN}/"
	url = f"{bot_url}sendMessage?chat_id={CHAT_ID}&text={text}"
	r = requests.post(url)
	logging.info(f"Request to {url} returned {r.status_code}")


if __name__ == "__main__":
	# send_message("test")
	# exit(0)
	conn = create_connection()
	rows = get_latest_record(conn)
	if rows:
		entry = rows[0]
		previous_date, notifications_status = datetime.strptime(entry[1], "%Y-%m-%d %H:%M:%S"), entry[2]
		expiry = calculate_expiry_date(previous_date, entry[3], entry[4])
		now = datetime.now()
		diff = now - previous_date
		# Time elapsed between purchase time and now is greater than/equal to 24hrs - extra hours
		if not(divmod(diff.total_seconds(), 3600)[0] < (24 - (entry[3]))):
			insert(conn, purchase_date = expiry)
			if notifications_status:
				# Check account balance for extra steps and instructions
				account = TelkomAccountManager()
				res, renewed = account.run(check_balance = True)
				account.driver.quit()
				if not renewed:
					res += (
						f"\nPrevious purchase date was {previous_date} and will expire on {expiry}\n"
					)
				else:
					res += (
						f"\nData bundle will expire on: {expiry + timedelta(days = 1)}"
					)
				send_message(res)
		try:
			hour = expiry.hour
			minute = expiry.minute
			logging.info(f"Next call time set to {hour}:{minute}")
			update_call_time(hour, minute)
		except Exception as ex:
			logging.error("Failed to update next call time")
			logging.error(str(ex))
	conn.close()
