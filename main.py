import time
from datetime import datetime

from business_logic import set_option_webdriver, create_driver, login_on_site, use_site


def main():
    option = set_option_webdriver()
    driver = create_driver(option)
    driver.get('https://rich-birds.com/signin')
    login_on_site(driver)
    driver.get_screenshot_as_file(str(datetime.now()) + '.png')
    time.sleep(2)
    use_site(driver)
    driver.close()


if __name__ == '__main__':
    while 1:
        main()
        time.sleep(86400)  # 24 hours to seconds
