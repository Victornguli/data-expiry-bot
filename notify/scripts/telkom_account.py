import logging
import os
import sys
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv, find_dotenv

# Load env since this is run outside wsgi environment
load_dotenv(find_dotenv())

MAX_RETRIES = 3
log_path = os.getenv("LOG_PATH")
logging.basicConfig(level = logging.INFO, filename = os.path.join(log_path, "logs.log"))

if not sys.platform.startswith('win'):
	# On a linux server this is needed for wrapping around X virtual framebuffer(Xvfb)
	display = Display(visible = 0, size = (800, 600))
	display.start()


class TelkomAccountManager:
	"""Telkom mobile account manager class"""
	INDEX_URL = 'https://myaccount.telkom.co.ke/3G/index.jsp'

	def __init__(self):
		self.phone_number = os.getenv('PHONE_NUMBER')
		self.password = os.getenv('PASSWORD')
		self.login_url = os.getenv('TELKOM_LOGIN_URL')
		self.logged_in = False
		self.current_page = 'login'

		options = webdriver.ChromeOptions()
		# options.headless = True
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

		# Submit login form and wait until logout btn is present to confirm login..
		form.submit()
		WebDriverWait(self.driver, 10).until(
			EC.presence_of_element_located((By.ID, 'userLogoutBtn'))
		)
		self.logged_in = True
		self.current_page = 'index'

	def get_balances(self):
		"""
		Scrapes the balances from the logged-in user's index page
		:return: Data and Airtime balance information
		:rtype: dict
		"""
		# Enforce that the driver is currently at the index first.
		if self.current_page != 'index':
			self.driver.get(self.INDEX_URL)
		WebDriverWait(self.driver, 10).until(
			EC.presence_of_element_located((By.ID, 'txtCurrBal'))
		)
		airtime_bal = self.driver.find_element_by_id('txtCurrBal').get_property('value')
		data_balance = self.driver.find_element_by_xpath(
			'//*[@id="tableAcctContent"]/tbody/tr[5]/td[2]/input').get_property('value')
		airtime, data = airtime_bal.lower(), data_balance.lower()
		return {
			'airtime': int(float(airtime.replace('ksh', ''))),
			'data': int(float((data.replace('mb', ''))))
		}

	def check_balances(self, parsed_data):
		"""
		Checks the data and airtime balance and performs necessary actions
		"""
		data, airtime = parsed_data.get('data'), parsed_data.get('airtime')
		balance_info = f'Current data balance is: {data}MB and current airtime balance is KES{airtime}.'
		renewed = False
		if data >= 1500:
			# send notification directing user to buy 700MB for now.
			instructions = 'You should manually initiate 700MB bundle purchase of KES60.'
		elif data < 1500 and airtime >= 100:
			# Condition for auto-renewal..
			renewal = self.purchase_bundle()
			balance_info = (
				f"Current data balance is: {renewal.get('data')}MB "
				f"and current airtime balance is KES{renewal.get('airtime')}."
			)
			instructions = 'Successfully Renewed 2GB data bundle.'
			renewed = True
		else:
			# Insufficient airtime for auto renewal.
			instructions = 'Low airtime balance. Recharge your account and initiate bundle purchase.'
		return f'{instructions}\n{balance_info}', renewed

	def purchase_bundle(self):
		"""
		Purchase a given data package. Currently fixed for the 2GB package
		:return: Balance info after purchase
		:rtype: dict
		"""
		purchase_btn = WebDriverWait(self.driver, 10).until(
			EC.presence_of_element_located((By.ID, 'tdSS_MY_BUNDLE'))
		)
		purchase_btn.click()
		package = WebDriverWait(self.driver, 10).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="supPricePlan"]/tbody/tr[2]/td[5]/span'))
		)
		package.click()
		confirm_button = WebDriverWait(self.driver, 10).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="btnOk"]'))
		)
		confirm_button.click()
		self.driver.get(self.INDEX_URL)
		self.current_page = 'index'
		WebDriverWait(self.driver, 10).until(
			EC.presence_of_element_located((By.ID, 'txtCurrBal'))
		)
		balance = self.get_balances()
		return balance

	def run(self, check_balance = False):
		"""
		Retrieves the balance only. Works by first confirming login and homepage status
		before scraping the balance and returning it.
		:param check_balance: A condition to dictate whether to check balance for
		extra operations and responses.
		:type check_balance: bool
		:return: The scraped balance
		:rtype: dict
		"""
		try:
			if not self.logged_in:
				self.login()
			balance = self.get_balances()
			if not check_balance:
				return balance
			res = self.check_balances(balance)
			return res
		except Exception as ex:
			logging.exception(f'account run Exception: {str(ex)}')
			self.driver.quit()
