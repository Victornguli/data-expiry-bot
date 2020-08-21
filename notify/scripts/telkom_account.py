import logging
import os
import time
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Load env since this is run outside wsgi environment
root = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(os.path.dirname(root), ".env"))

MAX_RETRIES = 3
log_path = os.getenv("LOG_PATH")
logging.basicConfig(level = logging.INFO, filename = os.path.join(log_path, "logs.log"))


# display = Display(visible = 0, size = (800, 600))
# display.start()


class TelkomAccountManager:
	"""Telkom mobile account manager class"""

	def __init__(self):
		self.phone_number = os.getenv('PHONE_NUMBER')
		self.password = os.getenv('PASSWORD')
		self.login_url = os.getenv('TELKOM_LOGIN_URL')

		options = webdriver.ChromeOptions()
		options.add_argument('--no-sandbox')
		self.driver = webdriver.Chrome(os.getenv('CHROMEDRIVER_PATH'), options = options)

	def login(self):
		self.driver.get(self.login_url)
		form = WebDriverWait(self.driver, 10).until(
			EC.presence_of_element_located((By.ID, 'userLoginForm'))
		)
		phone_input = self.driver.find_element_by_id('number')
		password_input = self.driver.find_element_by_id('pwd')
		phone_input.send_keys(self.phone_number)
		password_input.send_keys(self.password)
		form.submit()

	def get_balances(self):
		airtime_bal = self.driver.find_element_by_id('txtCurrBal').get_property('value')
		data_balance = self.driver.find_element_by_xpath(
			'//*[@id="tableAcctContent"]/tbody/tr[5]/td[2]/input').get_property('value')
		return {'airtime': airtime_bal, 'data': data_balance}

	def check_balances(self, balance_data):
		"""
		Checks the data and airtime balance and performs necessary actions
		"""

		airtime, data = balance_data.get('airtime').lower(), balance_data.get('data').lower()
		data = int(float(data.replace('mb', '')))
		airtime = int(float((airtime.replace('ksh', ''))))
		if data >= 1500:
			# send notification directing user to buy 700MB
			pass
		elif data < 1500 and airtime >= 100:
			# Proceed to automatically reload 2GB bundle
			pass
		else:
			# Notification with instructions to buy airtime
			pass

	def run(self):
		try:
			self.login()
			WebDriverWait(account.driver, 10).until(
				EC.presence_of_element_located((By.ID, 'txtCurrBal'))
			)
			balance = self.get_balances()
			return balance
		except Exception as ex:
			logging.exception(f'An error occurred while opening telkom account: {str(ex)}')
			# account.driver.quit()
			raise ex


if __name__ == '__main__':
	account = TelkomAccountManager()
	# account.run()
	account.check_balances({'airtime': '69.03ksh', 'data': '3145.88MB'})
