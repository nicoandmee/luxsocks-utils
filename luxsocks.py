from time import time
import requests
import re
from time import sleep
from bs4 import BeautifulSoup
from json import load
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from twocaptchaapi import TwoCaptchaApi
from PIL import Image
from pprint import pprint



api = TwoCaptchaApi('2b67434ad6039b2c71cb986d1e4d7ca6')
fileName = f"{time()}.csv"
captcha_filename = f"captcha/{time()}.png"


#Load login details and search query data
with open("login_details.txt") as r:
    auth = load(r)

user_id = auth['USERNAME']
pwd = auth['PASSWORD']
wait_more = float(auth['LAZY_LOGIN'])
wait_less =float(auth['LAZY_FORM'])

with open("luxsocks.csv", "r") as f:
    rows = f.read().split("\n")
#-------------------------------------


print("LuxSocks Utility - Quickly get your work started by auto-buying the cleanest, freshest, and fastest SOCKS on luxsocks.ru - Created by Lulzpid")

driver = webdriver.Chrome()

wait = WebDriverWait(driver, 60)
driver.get("https://luxsocks.ru/")
#Solving the captcha
element = driver.find_element_by_id('yw1') # find captcha image area on the page
location = element.location
size = element.size
driver.save_screenshot('captcha/tempcaptcha.png') # saves screenshot of entire page
im = Image.open('captcha/tempcaptcha.png') # uses PIL library to open image in memory


left = location['x']
top = location['y']
right = location['x'] + size['width']
bottom = location['y'] + size['height']
im = im.crop((int(left), int(top), int(right), int(bottom))) # defines crop points
im.save(captcha_filename) # saves new cropped image

#Send the image to 2Captcha, poll for a response
with open(captcha_filename, 'rb') as captcha_file:
    captcha = api.solve(captcha_file)

captchaSolution = captcha.await_result()
print(f"Captcha Solved Successfully:  {captchaSolution}")


# Login form fill
username = driver.find_element_by_name("LoginForm[username]")
password = driver.find_element_by_name("LoginForm[password]")
captchafield = driver.find_element_by_name("LoginForm[captcha]")



username.send_keys(user_id)
password.send_keys(pwd)
captchafield.send_keys(captchaSolution)



driver.find_element_by_id("yw2").click()

wait.until(EC.presence_of_element_located((By.NAME, "Socks[zip]")))

for row in rows[1:]:
    driver.get(
        "https://luxsocks.ru/socks/search/")
    try:
        row = re.sub("^\s*|\s*$", "", row)
        row = re.sub("\s\s+", " ", row)
        row = re.sub("^ | $", "", row)
        row = row.replace(" | ", "|")
        print(f"Searching matching SOCKS5 for {row}")
        info = row.split("|")


        #Specify only clean SOCKS
        wait.until(EC.visibility_of_element_located((By.ID, 'Socks_blacklisted_search')))
        blacklists = Select(driver.find_element_by_id("Socks_blacklisted_search"))
        blacklists.select_by_value("clean")


        #Specify geolocation radius of 50 miles (to be safe)
        wait.until(EC.visibility_of_element_located((By.ID, 'Socks_radius')))
        blacklists = Select(driver.find_element_by_id("Socks_radius"))
        blacklists.select_by_value("50")

        #Specify ZIP Code
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'col-sm-12 col-md-10 col-lg-10 items-side grid-view-loading')))
        wait.until(EC.visibility_of_element_located((By.NAME, 'Socks[zip]')))
        zipcode = driver.find_element_by_name("Socks[zip]")
        zipcode.send_keys(info[5])
        zipcode.send_keys(Keys.ENTER)

        #Wait for AJAX response
        sleep(5)

        firstsocks = driver.find_element_by_name("yt1")
        sockid = firstsocks.get_attribute("id")
        sockid = sockid.replace('grid-socks-btn-', '')
        print(f"Buying Out SOCKS5 with id {sockid}")



        driver.get(f"https://luxsocks.ru/socks/buy/{sockid}")
        x = json.loads(driver.find_element_by_tag_name('body').text)

        #last socks added to our cart, aka the one we just bought
        socks5 = x['CART'][-1]['value']
        socks5_info = x['CART'][-1]['title']
        pprint(socks5_info)






        data = '"' + '","'.join(re.sub("\s\s+|\n+", " ", str(x)) for x in [info[0], info[1], info[2], info[3], info[4],info[5], socks5]) + '"'
        print(data)
        with open(fileName, "a") as d:
            d.write(data)
            d.write("\n")


    except Exception as e:
        with open("Luxsocks_log.txt", "a") as log:
            log.write(str(e))
            log.write("\n")
        with open("Luxsocks_error.txt", "a") as error:
            error.write(row)
            error.write("\n")
