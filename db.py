import sqlite3
import logging
import os
from datetime import datetime, timedelta

log_path = os.getenv("LOG_PATH")
logging.basicConfig(level = logging.INFO, filename=os.path.join(log_path, "logs.log"))


def create_connection():
	conn = None
	init = True
	db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.sqlite3")
	logging.info(f"Creating db at {db_path}")
	if os.path.exists(db_path):
		init = False
	try:
		conn = sqlite3.connect(db_path)
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


def get_latest_record(conn):
	cursor = conn.execute(
		"SELECT * FROM notifications ORDER BY id DESC LIMIT 1;")
	row = [x for x in cursor][-1]
	return row
	# latest_date = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
	# return latest_date
	# for row in cursor:
	# 	print("id = ", row[0])
	# 	print("purchase_date = ", datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S"))
	# 	print("notifications_on = ", row[2])
	# 	print("grace_period_hours = ", row[3])
	# 	print("grace_period_minutes = ", row[4])
	# 	print("sms_notifications = ", row[5])
	# 	previous_date = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
	# 	expiry_date = previous_date + timedelta(minutes = 1)
	# 	exec_time = datetime.strftime(expiry_date, "%H:%M")
	# 	print(expiry_date)


def calculate_expiry_date(latest_date, hours = 0, minutes = 0):
	previous_date = datetime.strptime(latest_date, "%Y-%m-%d %H:%M:%S")
	expiry_date = previous_date + timedelta(hours = 24) - timedelta(hours = hours, minutes = minutes)
	return expiry_date


# if __name__ == "__main__":
# 	connection = create_connection()
# 	row = get_latest_record(connection)
# 	date = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
# 	expiry = calculate_expiry_date(row[1], row[2], row[3])
# 	print(date)
# 	print(expiry)
# 	connection.close()
