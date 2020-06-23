import sqlite3
import logging
import os
from datetime import datetime, timedelta

log_path = os.getenv("LOG_PATH")
logging.basicConfig(level = logging.INFO, filename = os.path.join(log_path, "logs.log"))


def create_connection():
	conn = None
	init = True
	db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.sqlite3")
	logging.info(f"Connecting to db at {db_path}")
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


def insert(conn, **kwargs):
	latest_record = get_latest_record(conn)
	if latest_record:
		latest_record = latest_record[0]
		logging.info(f"Updating entry with id {latest_record[0]}")
		# Update instead of insert..
		query = ""
		data = []
		for _ in range(len(kwargs)):
			obj = kwargs.popitem()
			query += obj[0] + " = ? "
			data.append(obj[1])
			if kwargs:
				query += ", "
		param_query = f"""UPDATE notifications SET {query} WHERE id = ?"""
		data.append(latest_record[0])
		conn.execute(param_query, tuple(data))
		conn.commit()
	elif kwargs.get("purchase_date", ""):
		logging.info(f"Creating new entry with date {kwargs.get('purchase_date')}")
		data = [kwargs.get("purchase_date")]
		sqlite_insert_with_param = """INSERT INTO 'notifications'
		('purchase_date') VALUES (?);"""
		conn.execute(sqlite_insert_with_param, tuple(data))
		conn.commit()


def get_latest_record(conn):
	cursor = conn.execute(
		"SELECT * FROM notifications ORDER BY id DESC LIMIT 1;")
	rows = [x for x in cursor]
	return rows


def get_status(conn):
	rows = get_latest_record(conn)
	if rows:
		obj = rows[0]
		return obj[1], obj[2]
	return None, 0


def calculate_expiry_date(latest_date, hours = 0, minutes = 0):
	previous_date = datetime.strptime(latest_date, "%Y-%m-%d %H:%M:%S")
	expiry_date = previous_date + timedelta(hours = 24) - timedelta(hours = hours, minutes = minutes)
	return expiry_date


# if __name__ == "__main__":
# 	connection = create_connection()
# 	row = get_latest_record(connection)
# 	print(row)
# 	if row:
# 		row = row[0]
# 		date = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
# 		print(date)
# 		expiry = calculate_expiry_date(row[1], row[2], row[3])
# 		print(expiry)
# 		insert(connection, purchase_date = expiry)
# 		row = get_latest_record(connection)
# 	date = datetime.strptime("2020-06-25 10:14:00", "%Y-%m-%d %H:%M:%S")
# 	insert(connection, purchase_date = date, notifications_on = 0)
# 	print(f"New purchase date is {date}")
# 	row = get_latest_record(connection)
# 	print(row)
# 	connection.close()
