import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime
import argparse


def get_historic_cotization(url, start, end):
    driver = webdriver.Chrome(executable_path='/home/fran/Downloads/chromedriver')
    driver.get(url)
    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CLASS_NAME, 'noHeader')))
    driver.find_element_by_class_name('noHeader').click()
    driver.find_element_by_id('datePickerIconWrap').click()

    # dynamically generate displayed variables
    _vars = driver.find_element_by_id('curr_table').find_elements_by_tag_name('th')
    variables = [var.text.lower() for var in _vars]

    # calculate how many months you have to go back from present (present = current month - 2)
    starting_day, starting_month, starting_year = map(int, start.split('/'))
    last_day, last_month, last_year = map(int, end.split('/'))
    current_month = datetime.now().month
    current_year = datetime.now().year
    go_back_factor = (current_year - starting_year) * 12 + (current_month - 2 - starting_month)

    # click arrow to go back to that month
    for i in range(go_back_factor):
        sleep(0.1)
        go_back_arrow = driver.find_element_by_class_name('ui-datepicker-prev')
        go_back_arrow.click()

    # from that month to last_month
    go_forward_factor = ((last_year - starting_year) * 12 + (last_month - 2 - starting_month)) / 3
    _file = open("%s/%s-%s" % (os.getcwd(), start.replace('/','.'), end.replace('/', '.')), 'a')
    _file.write('%s\n' % (", ".join(variables)))
    for i in range(go_forward_factor+1):
        # select first day of lefmost month and last day of rightmost month
        els = filter(lambda x: x.tag_name == 'a', driver.find_elements_by_class_name('ui-state-default'))
        sleep(0.1)
        els[0].click()
        sleep(0.1)
        els[-1].click()
        sleep(0.1)
        apply_changes = driver.find_element_by_class_name('ui-datepicker-buttonpane').find_element_by_tag_name('a')
        apply_changes.click()
        # scrap
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'historicalTbl')))
        soup = BeautifulSoup(driver.page_source)
        table = soup.find('table', {'class': 'genTbl closedTbl historicalTbl'})
        rows = table.tbody.find_all('tr')
        with _file as f:
            for row in rows[::-1]:
                vals = map(lambda x: x.text.replace(',', ''), row.find_all('td'))
                f.write('%s\n' % (', '.join(vals)))
        driver.find_element_by_id('datePickerIconWrap').click()
        sleep(0.1)
        for i in range(3):
            go_forward_arrow = driver.find_element_by_class_name('ui-datepicker-next')
            go_forward_arrow.click()
            sleep(0.1)
        _file = open("%s/%s-%s" % (os.getcwd(), start.replace('/','.'), end.replace('/', '.')), 'a')


parser = argparse.ArgumentParser(description="Get asset cotization from the start to the end of the period chosen")
parser.add_argument('--url', help="investing url from where to crawl information.")
parser.add_argument('--start', help="start of the period to crawl. Ex: 15/08/2011")
parser.add_argument('--end', help="end of the period to crawl. Ex: 03/10/2015")
args = parser.parse_args()
get_historic_cotization(args.url, args.start, args.end)
