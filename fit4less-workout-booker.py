#!/bin/env python3
# Usage: ./fit4less-booker.py book [pass] [email] [location] [minimum time to book] [maximum time to book]
# Assumptions: Account used already exists

import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os
import sys
import datetime


def scrollTo(driver, element):
    driver.execute_script("""arguments[0].scrollIntoView({
            block: 'center',
            inline: 'center'
        });""", element)
    return element


class Account():
    '''
    Account associated with fit4less account
    '''
    def __init__(self, password, emailaddress):
        self.password = password
        self.email = emailaddress
        self.countbooked = 0

    def getPassword(self):
        return self.password

    def getEmailAddress(self):
        return self.email

    def login(self, driver):
        driver.get('https://myfit4less.gymmanager.com/portal/login.asp')

        # Find username/email box, set
        email = scrollTo(driver, driver.find_element_by_name('emailaddress'))
        email.send_keys(self.getEmailAddress())

        # Find password box, set
        password = scrollTo(driver, driver.find_element_by_name('password'))
        password.send_keys(self.getPassword())

        # Find login button, click
        login_button = scrollTo(driver, driver.find_element_by_id('loginButton'))
        login_button.click()

        page = driver.find_element_by_tag_name('body').get_attribute("id")
        if page == 'login':
            raise Exception("Failed to login")

        assert(page == 'booking')

    def bookTime(self, driver, minrangetimegym, maxrangetimegym):
        alltimes_elements = driver.find_elements_by_css_selector(".available-slots > .time-slot")
        if len(alltimes_elements) == 0:
            print("No times available for this date")
            return

        for time in alltimes_elements:
            clock = time.get_attribute("data-slottime")[3::]
            time_id = time.get_attribute("id")
            index_of_colon = clock.find(':')
            index_of_space = clock.find(' ')
            hour, minute = 0, 0
            hour += int(clock[:index_of_colon])
            minute = int(clock[index_of_colon+1:index_of_space])
            if clock[-2:] == "PM":
                if hour == 12:
                    pass
                else:
                    hour += 12
            elif clock[-2:] == "AM" and hour == 12:
                hour = 0

            # print(hour, minute)
            timegym = datetime.datetime.now().replace(
                hour=int(hour),
                minute=int(minute),
                second=0,
                microsecond=0
            )
            # print(timegym)
            if minrangetimegym <= timegym <= maxrangetimegym:
                # book this time
                booktime = scrollTo(driver, driver.find_element_by_id(time_id))
                booktime.click()  # Click on the specifc time to book, falling in the time domain we want

                covid_terms = scrollTo(driver, driver.find_element_by_id("dialog_book_yes"))
                covid_terms.click()
                print("Booked time for " + clock)
                # return clock

    def selectGym(self, driver, location):
        # Desired location is not already selected
        # "Reserve a gym session in club London Argyle on Monday, 22 February 2021."
        if location not in driver.find_element_by_tag_name('h2').text:
            # Select club
            selectclub_element = scrollTo(driver, driver.find_element_by_id('btn_club_select'))
            selectclub_element.click()
            try:
                location_element = driver.find_element_by_xpath("//div[contains(text(),'{}')]".format(location))
                location_element.click()
            except selenium.common.exceptions.NoSuchElementException:
                raise Exception("Incorrect location")

    def book(self, driver, minrangetimegym, maxrangetimegym):
        # 5) Select Day: Ex: Tomorrow. Check todays date, select tomorrows date (Maximum of 3 days in advance)
        # driver.find_element_by_id('btn_date_select').click()
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        dayaftertomorrow = today + datetime.timedelta(days=2)
        days = [
            dayaftertomorrow.strftime("%Y-%m-%d"),
            tomorrow.strftime("%Y-%m-%d"),
            today.strftime("%Y-%m-%d")
        ]

        for i in days:
            # print("-------------")
            try:
                countbooked = driver.find_element_by_xpath("/html/body/div[5]/div/div/div/div/form/p[3]")
            except selenium.common.exceptions.NoSuchElementException:
                print("Maximum Booked. Booked {} times".format(self.countbooked))
                return 1
            self.countbooked = countbooked.text[9]

            selectday_element = scrollTo(driver, driver.find_element_by_id('btn_date_select'))
            selectday_element.click()
            day_element_name = "date_"+i
            # print("Looking at times for", i)
            driver.find_element_by_id(day_element_name).click()

            self.bookTime(driver, minrangetimegym, maxrangetimegym)

    def getReserved(self, driver):
        alltimes_elements = driver.find_elements_by_css_selector(".reserved-slots > .time-slot")
        for i in alltimes_elements:
            print('-', i.get_attribute('data-slotdate'), i.get_attribute('data-slotclub'), i.get_attribute('data-slottime'))


if __name__ == '__main__':
    function = sys.argv[1]  # book or reserved
    password = sys.argv[2]
    email = sys.argv[3]
    person = Account(password, email)

    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    # options.add_argument('window-size=1920x1080')
    driver = webdriver.Chrome('/usr/bin/chromedriver', options=options)

    if function == 'book':
        location = sys.argv[4].replace('-', ' ')
        start_time = sys.argv[5]
        end_time = sys.argv[6]
        minrangetimegym = datetime.datetime.now().replace(
            hour=int(start_time[:start_time.find(":")],),
            minute=int(start_time[start_time.find(":")+1:])
        )
        maxrangetimegym = datetime.datetime.now().replace(
            hour=int(end_time[:end_time.find(":")]),
            minute=int(end_time[end_time.find(":")+1:])
        )

        person.login(driver)
        person.selectGym(driver, location)
        person.book(driver, minrangetimegym, maxrangetimegym)
        person.getReserved(driver)
    elif function == 'reserved':
        person.login(driver)
        person.getReserved(driver)

    elif function == 'test-reserved':
        driver.get('file://%s/tests/booking.html' % os.path.dirname(__file__))
        person.getReserved(driver)

    elif function == 'test-book':
        location = sys.argv[4].replace('-', ' ')
        start_time = sys.argv[5]
        end_time = sys.argv[6]
        minrangetimegym = datetime.datetime.now().replace(
            hour=int(start_time[:start_time.find(":")],),
            minute=int(start_time[start_time.find(":")+1:])
        )
        maxrangetimegym = datetime.datetime.now().replace(
            hour=int(end_time[:end_time.find(":")]),
            minute=int(end_time[end_time.find(":")+1:])
        )

        driver.get('file://%s/tests/booking.html' % os.path.dirname(__file__))
        person.bookTime(driver, minrangetimegym, maxrangetimegym)
    else:
        print("Unknown command")
    # driver.quit()
