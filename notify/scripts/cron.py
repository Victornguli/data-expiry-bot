from crontab import CronTab
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def init():
	"""
	Initializes a crontab entry for notify.py(Runs every midnight)
	"""
	cron = CronTab(user = True)
	job = cron.new(command=f"python3 {os.path.join(ROOT, 'notify.py')}", comment = "notification_script")
	job.hour.on(0)
	job.minute.on(0)
	cron.write()


def update_call_time(hour = 0, minute = 0):
	"""
	Update next call time of the notification script.
	If hour and minute are left empty, next call is reset to midnight
	:param hour: The hour to be set
	:type hour: int
	:param minute: The minute value to be set
	:type minute: int
	"""
	cron = CronTab(user = True)
	jobs = cron.find_comment("notification_script")
	for job in jobs:
		job.hour.on(hour)
		job.minute.on(minute)
	cron.write()
