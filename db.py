import sqlite3
import logging
import schedule
import time
import os
import threading
import requests
from datetime import datetime, timedelta
# from bot import BotHandler


logging.basicConfig(level=logging.INFO)


def create_connection():
	conn = None
	init = True
	db_path = os.path.join(os.path.abspath(__file__), "db.sqlite3")
	if os.path.exists(db_path):
		init = False
	try:
		conn = sqlite3.connect("db.sqlite3")
		if init:
			create_table(conn)
	except Exception as e:
		logging.error("Could not create/connect to the db")
		print(str(e))
	finally:
		return conn


def create_table(conn):
	conn.execute('''
	CREATE TABLE notifications 
		(id INTEGER PRIMARY KEY AUTOINCREMENT,
		purchase_date TIMESTAMP NOT NULL,
		notifications_on INTEGER DEFAULT 0,
		grace_period_hours INTEGER DEFAULT 1,
		grace_period_minutes INTEGER DEFAULT 0,
		sms_notifications INTEGER DEFAULT 0);''')
	logging.info("Table created successfully")


def insert(conn, data):
	sqlite_insert_with_param = """INSERT INTO 'notifications'
		('purchase_date') 
		VALUES (?);"""
	conn.execute(sqlite_insert_with_param, tuple(data))
	conn.commit()


# def send_test():
# 	bh = BotHandler()
# 	url = bh.BOT_URL
# 	payload = {
# 		"chat_id": 887933915,
# 		"text": "Bundles will expire soon"
# 	}
# 	requests.post(url, payload)

# if __name__ == "script":
# 	conn = create_connection()
# 	# create_table(conn)
# 	# insert(conn, [datetime.now()])
# 	cursor = conn.execute(
# 		"SELECT * FROM notifications ORDER BY id ASC LIMIT 1;")
#
# 	for row in cursor:
# 		print("id = ", row[0])
# 		print("purchase_date = ", datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S.%f"))
# 		print("notifications_on = ", row[2])
# 		print("grace_period_hours = ", row[3])
# 		print("grace_period_minutes = ", row[4])
# 		print("sms_notifications = ", row[5])
# 		previous_date = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S.%f")
# 		expiry_date = previous_date + timedelta(minutes = 1)
# 		# expiry_date = expiry_date - timedelta(hours = row[3], minutes = row[4])
# 		exec_time = datetime.strftime(expiry_date, "%H:%M")
# 		# insert(conn, [expiry_date])
# 		print(expiry_date)
# 	conn.close()
