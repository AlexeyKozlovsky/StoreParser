import os
import time

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Parser:
    def __init__(self, driver_path):
        self.browser = webdriver.Firefox(executable_path=os.path.abspath(driver_path))

    def _scroll_the_page(self):
        """Метод для прокрутки магазинов, чтобы прогрузились данные
        (т.к. используется ajax)"""
        browser = self.browser
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'search-list-view__content')))
        current, pause_time, max_count = 1, 2, 5
        while current < max_count:
            scrollable_div = browser.find_element_by_xpath('/html/body/div[1]/div[2]/div[9]/div/div[1]/div[1]/div[1]/div')
            browser.execute_script('arguments[0].scrollTop=arguments[0].scrollHeight', scrollable_div)
            time.sleep(pause_time)
            current += 1

    def _get_items_count(self):
        """Метод для нахождения количества магазинов
        returns: количество магазинов"""
        browser = self.browser
        source_data = browser.page_source
        soup = BeautifulSoup(source_data, 'lxml')
        items = soup.find_all('div', {'data-chunk': 'search-snippet'})
        return len(items)

    def parse(self, url):
        browser = self.browser
        browser.get(url=url)
        #self._scroll_the_page()
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'search-list-view__content')))
        current, pause_time, max_count = 1, 2, 5
        while current < max_count:
            scrollable_div = browser.find_element_by_xpath('/html/body/div[1]/div[2]/div[9]/div/div[1]/div[1]/div[1]/div')
            browser.execute_script('arguments[0].scrollTop=arguments[0].scrollHeight', scrollable_div)
            time.sleep(pause_time)
            current += 1

        items_count = self._get_items_count()

        addresses = []
        for i in range(1, items_count + 1):
            try:
                address = browser.find_element_by_xpath(f'/html/body/div[1]/div[2]/div[9]/div/div[1]/div[1]/div[1]/div/div[1]/div/div/ul/div[{i}]/li/div/div/div/div/div[4]')
                addresses.append(address.text)
                continue
            except:
                pass

            while True:
                element = browser.find_element_by_xpath(f'/html/body/div[1]/div[2]/div[9]/div/div[1]/div[1]/div[1]/div/div[1]/div/div/ul/div[{i}]')
                browser.execute_script('arguments[0].scrollIntoView()', element)
                element.click()
                try:
                    address = browser.find_element_by_class_name('business-contacts-view__address-link')
                    break
                except:
                    time.sleep(0.5)

            addresses.append(address.text)
            browser.execute_script('window.history.go(-1)')
            time.sleep(0.5)

        self.result = addresses

    def to_csv(self, filename, columns):
        """Метод для экспорта результатов в csv файл"""
        df = pd.DataFrame(columns=columns, data=np.array([self.result]).T)
        df.to_csv(filename, index=False)

    def shutdown(self):
        self.browser.quit()


if __name__ == '__main__':
    url = 'https://yandex.ru/maps/?display-text=%D0%9B%D0%B5%D1%80%D1%83%D0%B0%20%D0%9C%D0%B5%D1%80%D0%BB%D0%B5%D0%BD&ll=69.513627%2C-11.425287&mode=search&sctx=ZAAAAAgBEAAaKAoSCd45lKEqlkJAEU0UIXU7X0xAEhIJS2z9%2F3%2BNzz8R6cfx2ie%2BtD8oCjgAQJBOSAFiO3JlYXJyPXNjaGVtZV9Mb2NhbC9HZW8vTWFrZUJ1c1F1ZXJ5VHlwZUlzVmFsdWUwQWx3YXlzVHJ1ZT0xagJydXAAnQHNzEw9oAEAqAEAvQE5bskowgHOBM3qyO8F%2B%2BSovhSkls3lvQXy083fqwWc4f7p7wG3%2B%2Fen3AavxJ3ZBKfc6OIF7t2%2B%2FgXbyfTiBY6ks5XxA8%2Fj4NMEjbDHhATBw9j2vQbkg673pgOC3v2ZBvLa2dEEoNvmkgbHtJ%2FKBdWFs%2F0Dgr3o0ga8x4aFYvriseEGzbaUhQrwk7uZB9qk7JgEtNbE8luC6t2MBIanxoYGsKyN8wXzyYHIBsuq9%2F3kArDgreIFsL%2Fv7gXttafLhQLv5%2Bmn5wKY647zBejXn50G7cnrw6kC2czkpPwDk4T4hL0E4aTx4gWPheWavgbsycWicOSKvYyUBMuM%2F5IGj5%2BpgnX44v2L7wTz%2B6mx0wSUyf2%2FR8bdvfTIA%2BKekbEG5eas0dkDr4yUptMEsZ7uw54G7Ja%2FlAbs0rz4BaaYlYYGt4aqjga4%2Ff%2BY%2BAS118aQBoLH79H%2BBLDV9dkGiIj8j8wCou%2BH9wSpho77BYfO9NMGroD7ybMB9%2BqT7f8B2NHn%2FhiB1ZiwBpf%2FyobbA4rivowGi8m2iAa24srlBbz8g9edA5ncjZSYAozQ%2FfisA6qx67UZgPWKiJcEsobK1gaB1L7LBuW9redE4v7lt%2BkFgPbPn9cBjsTc4gWWxZ2JBZzHsO1h3Y2zulDgp6TprgLhusaH1wT5%2Bqns0gGO9tCnKt3hi7oFgbHO19kF%2FcGZxi%2F17Mm1zgb48IysEM7Wwo%2FYBJzymP7gAZex79qpBa63rtPeBI%2BJsv0Fr9%2BDjuIDm4DbrwbTgYKfBs6H4rcxounWooED8LHxgbAE6gEA8gEA%2BAEEggIYKChjaGFpbl9pZDooMzg5MTc0NTMxKSkpigIA&sll=69.513627%2C-11.425287&sspn=167.343750%2C163.384971&text=%7B%22text%22%3A%22%D0%9B%D0%B5%D1%80%D1%83%D0%B0%20%D0%9C%D0%B5%D1%80%D0%BB%D0%B5%D0%BD%22%2C%22what%22%3A%5B%7B%22attr_name%22%3A%22chain_id%22%2C%22attr_values%22%3A%5B%22389174531%22%5D%7D%5D%7D&z=2'
    parser = Parser('firefoxdriver/geckodriver')
    parser.parse(url)
    parser.to_csv(filename='out.csv', columns=['address'])
    parser.shutdown()



