from crontab import CronTab
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def init():
	cron = CronTab(user = "root")
	job = cron.new(command=f"python3 {os.path.join(ROOT, 'notify.py')}", comment = "notification_script")
	job.hour.on(0)
	job.minute.on(0)
	cron.write()


def update_call_time(hour = 0, minute = 0):
	"""
	Update next call time of the notification script.
	If hour and minute are left empty, next call is reset to midnight
	:param hour int The hour to be set
	:param minute int The minute value to be set
	"""
	cron = CronTab(user = "root")
	jobs = cron.find_comment("notification_script")
	for job in jobs:
		job.hour.on(hour)
		job.minute.on(minute)
	cron.write()
