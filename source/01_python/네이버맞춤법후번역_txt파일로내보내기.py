# 네이버 맞춤법 py파일로
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import pandas as pd

# ch14_맞춤법전.txt를 300자이내로 자르기
with open('data/ch14_맞춤법전.txt', 'r', encoding='utf-8') as f:
    text = f.read()
print('총글자 수 :',len(text))
ready_list = [] # 맞춤법 검사할 text 내용(300이자 이내로 list)
while(len(text) > 300):
    temp = text[:300]
    new_line_char_index = temp.rfind('\n')
    print(new_line_char_index)
    ready_list.append(text[:new_line_char_index])
    text = text[new_line_char_index:]
ready_list.append(text)
[ready[:10] for ready in ready_list]

driver = webdriver.Chrome()

time.sleep(0.5)

driver.get('https://www.naver.com/')
input_elem = driver.find_element(By.CSS_SELECTOR, 'input[name="query"]')
input_elem.send_keys('맞춤법 검사기')
input_elem.send_keys(Keys.RETURN)

time.sleep(0.5)

results = '' # 맞춤법 검사 후 내용

textarea = driver.find_element(By.CLASS_NAME, 'txt_gray')

for ready in ready_list:
    time.sleep(2)
    
    textarea.send_keys(Keys.CONTROL, 'a') # control + a
    textarea.send_keys(ready)

    button = driver.find_element(By.CLASS_NAME, 'btn_check')
    button.click()

    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    result = soup.select_one('p._result_text.stand_txt').text
    results += result + '\n\n'
    
# driver.close()

with open('data/ch14_맞춤법후_한글원본.txt', 'w', encoding='utf-8') as f:
    f.write(results)
# ch14_맞춤법후.txt를 300자이내로 자르기
with open('data/ch14_맞춤법후_한글원본.txt', 'r', encoding='utf-8') as f:
    text = f.read()
print('총글자 수 :',len(text))
ready_list = [] # 다음에서 번역할 text 내용(300이자 이내로 list)
while(len(text) > 300):
    temp = text[:300]
    new_line_char_index = temp.rfind('\n')
    print(new_line_char_index)
    ready_list.append(text[:new_line_char_index])
    text = text[new_line_char_index:]
ready_list.append(text)
[ready[:10] for ready in ready_list]

# 다음에서 번역
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import pandas as pd

driver = webdriver.Chrome()

time.sleep(0.5)

driver.get('https://www.daum.net/')
input_elem = driver.find_element(By.NAME, 'q')
input_elem.send_keys('다음 번역기')
input_elem.send_keys(Keys.RETURN)

time.sleep(0.5)

results = '' # 번역 후 내용

textarea = driver.find_element(By.ID, 'textareaWrite')

for ready in ready_list:
    time.sleep(2)
    
    textarea.send_keys(Keys.CONTROL, 'a') # control + a
    textarea.send_keys(ready)

    button = driver.find_element(By.LINK_TEXT, '번역하기')
    button.click()

    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    result = soup.select_one('div#resultRender > div.result_area.area_item.txt_eng.translate_many').text
    results += result + '\n\n'
    
driver.close()

with open('data/ch14_자동화영어번역본.txt', 'w', encoding='utf-8') as f:
    f.write(results)