import logging
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load env since this is run on bash..
root = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(os.path.dirname(root), ".env"))
from db import create_connection, get_latest_record, calculate_expiry_date, insert
from cron import update_call_time

log_path = os.getenv("LOG_PATH")
logging.basicConfig(level = logging.INFO, filename = os.path.join(log_path, "logs.log"))


def send_message(previous, exp):
	text = f"Your data bundle will be expiring soon. Previous purchase date was {previous}.\nNext expiry date is {exp}"
	bot_url = "https://api.telegram.org/bot1179386780:AAGc5uaxmaqZi2ji-9JcmwlZanWdUw7Vi5c/"
	url = f"{bot_url}sendMessage?chat_id={887933915}&text={text}"
	r = requests.post(url)
	logging.info(f"Request to {url} returned {r.status_code}")


if __name__ == "__main__":
	conn = create_connection()
	rows = get_latest_record(conn)
	if rows:
		entry = rows[0]
		previous_date = entry[1]
		notifications_status = entry[2]
		expiry = calculate_expiry_date(previous_date, entry[3], entry[4])
		now = datetime.now()
		previous_date = datetime.strptime(previous_date, "%Y-%m-%d %H:%M:%S")
		diff = now - previous_date
		# Time elapsed between purchase time and now is greater than/equal to 24hrs - extra hours
		if not(divmod(diff.total_seconds(), 3600)[0] < (24 - (entry[3] + 1))):
			logging.info("Setting new purchase date")
			insert(conn, purchase_date = expiry)
			if notifications_status:
				send_message(previous_date, expiry)
		try:
			hour = expiry.hour
			minute = expiry.minute
			logging.info(f"Call me at {hour}:{minute}")
			update_call_time(hour, minute)
		except Exception as ex:
			logging.error("Failed to update call time")
			logging.error(str(ex))
	conn.close()
