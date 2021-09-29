import os
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

googleIBMLink = 'https://speech-to-text-demo.ng.bluemix.net/'
delayTime = 2
audioToTextDelay = 10
filename = '1.mp3'


def get_use_today(pg_source):
    day_limit = 0
    remaining_for_today = 0
    soup = BeautifulSoup(pg_source, features="lxml")

    for table_data in soup.find_all('tr'):
        txt = table_data.contents[1].text
        if 'Ваш суточный лимит' in txt:
            day_limit = int(table_data.contents[3].text)
        if 'Осталось на сегодня' in txt:
            remaining_for_today = int(table_data.contents[3].text)
            break
    result = remaining_for_today // day_limit
    return result


def set_option_webdriver(proxy=None):
    option = webdriver.ChromeOptions()
    if proxy:
        option.add_argument('--proxy-server=%s' % proxy)
    option.add_argument('--disable-notifications')
    option.add_argument("--mute-audio")
    # option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    option.add_argument('--no-sandbox')
    option.add_argument('--window-size=1420,1080')
    option.add_argument('--disable-dev-shm-usage')
    option.add_argument('--headless')
    option.add_argument('--disable-gpu')
    option.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1")
    return option


def create_driver(option=None):
    driver = webdriver.Chrome(options=option)
    return driver


def solve_captcha(driver):
    time.sleep(1)
    googleClass = driver.find_elements_by_class_name('g-recaptcha')[0]
    time.sleep(2)
    outeriframe = googleClass.find_element_by_tag_name('iframe')
    time.sleep(1)
    outeriframe.click()
    time.sleep(2)
    allIframesLen = driver.find_elements_by_tag_name('iframe')
    time.sleep(1)
    audio_btn_found = False
    audio_btn_index = -1

    for index in range(len(allIframesLen)):
        driver.switch_to.default_content()
        iframe = driver.find_elements_by_tag_name('iframe')[index]
        driver.switch_to.frame(iframe)
        driver.implicitly_wait(delayTime)
        try:
            audioBtn = driver.find_element_by_id('recaptcha-audio-button') or driver.find_element_by_id('recaptcha-anchor')
            audioBtn.click()
            audio_btn_found = True
            audio_btn_index = index
            break
        except Exception as e:
            pass
    return audio_btn_found, audio_btn_index


def audio_to_text(mp3Path, driver):
    driver.execute_script('''window.open("","_blank");''')
    driver.switch_to.window(driver.window_handles[1])
    driver.get(googleIBMLink)
    delayTime = 10
    # Upload file
    time.sleep(1)
    # Upload file
    time.sleep(1)
    root = driver.find_element_by_id('root').find_elements_by_class_name('dropzone _container _container_large')
    btn = driver.find_element(By.XPATH, '//*[@id="root"]/div/input')
    # btn.send_keys('D:/Other/Coding/Programming/Python/MyProject/rich-birds/1.mp3') # На моем ПК
    btn.send_keys('/opt/project/1.mp3')  # in docker
    # Audio to text is processing
    time.sleep(delayTime)
    # btn.send_keys(os.path)
    # Audio to text is processing
    time.sleep(audioToTextDelay)
    text = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[7]/div/div/div').find_elements_by_tag_name('span')
    result = " ".join([each.text for each in text])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return result


def save_file(content, filename):
    with open(filename, "wb") as handle:
        for data in content.iter_content():
            handle.write(data)


def login_on_site(driver):
    time.sleep(5)  # Let the user actually see something!
    login_input = driver.find_element_by_class_name('lg')
    login_input.send_keys(os.getenv('EMAIL'))
    time.sleep(5)
    password_input = driver.find_element_by_class_name('ps')
    password_input.send_keys(os.getenv('PASSWORD'))
    time.sleep(1)

    use_audio_btn(driver)

    driver.switch_to.default_content()
    login_input.submit()


def use_audio_btn(driver):
    audio_btn_found, audio_btn_index = solve_captcha(driver)

    if audio_btn_found:
        try:
            while True:
                href = driver.find_element_by_id('audio-source').get_attribute('src')
                response = requests.get(href, stream=True)
                save_file(response, filename)
                response = audio_to_text(os.getcwd() + '/' + filename, driver)
                print(response + '- This is sound text//////')
                driver.switch_to.default_content()
                iframe = driver.find_elements_by_tag_name('iframe')[audio_btn_index]
                driver.switch_to.frame(iframe)
                inputbtn = driver.find_element_by_id('audio-response')

                inputbtn.send_keys(response)
                inputbtn.send_keys(Keys.ENTER)
                time.sleep(2)
                errorMsg = driver.find_elements_by_class_name('rc-audiochallenge-error-message')[0]

                if errorMsg.text == "" or errorMsg.value_of_css_property('display') == 'none':
                    print("Success")
                    break
        except Exception as e:
            print(e)
            print('Caught. Need to change proxy now')
    else:
        print('Button not found. This should not happen.')


def use_site(driver):
    new_page_url = 'https://rich-birds.com/account/burse'
    driver.get(new_page_url)
    counts_click = get_use_today(driver.page_source)
    for i in range(1, counts_click + 1):
        print(f'Click {i}')
        driver.find_element(By.XPATH, '/html/body/div[2]/div[4]/div[2]/div[2]/form/table/tbody/tr[5]/td/input').click()  # button sold
