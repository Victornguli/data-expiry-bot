from pyvirtualdisplay import Display
from selenium import webdriver

# display = Display(visible = 0, size = (800, 600))
# display.start()

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')

driver = webdriver.Chrome('D://Dev tools//chromedriver.exe', chrome_options = options)


if __name__ == '__main__':
	driver.get('http:nytimes.com')
	print(driver.title)
