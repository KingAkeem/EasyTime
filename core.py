#!/usr/bin/env python3

__author__ = 'Akeem King'

import getpass
import json
import logging as log
from datetime import datetime
from helpers.drivers import ChromeDriver
from helpers.actions import login, wait_for, submit
from helpers.timesheet import fill_timesheet
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


def recent_pay_period(driver):
    """Finds first and lates date of most recent payperiod by ID
    :param driver: Current Selenium PhantomJS driver instance in use
    """

    # First and last day of payperiod
    first_day = driver.find_element_by_id('DATE_LIST_VAR1_1').text
    last_day = driver.find_element_by_id('DATE_LIST_VAR2_1').text

    # Making two digit year into four digits eg. 17 -> 2017
    first_day = first_day[0:6] + '20' + first_day[6:8]
    last_day = last_day[0:6] + '20' + last_day[6:8]

    # Formatting start date eg. Y-m-d
    first_day = datetime.strptime(first_day, '%m/%d/%Y').strftime('%Y-%m-%d')
    last_day = datetime.strptime(last_day, '%m/%d/%Y').strftime('%Y-%m-%d')

    return (first_day, last_day)


def get_hours(driver):

    return driver.find_element_by_id('LIST_VAR2_4').text


def get_shifts(driver, first_day, last_day):
    """
    Expicitly waits for JavaScript to generate shift content


    :param driver: Current Selenium phantomjs driver instance in use
    :param date_start: beginning date of shifts
    :param date_end: last date of shifts
    :return: None
    """

    shifts = dict()

    # Enlarges window to maximum size
    driver.maximize_window()

    # Webdriver explicitly waits up until 10 seoncds or when it finds
    # the chosen element by id then it moves to
    # the element and sends data
    wait_for(driver, 600, 'from')
    from_date = driver.find_element_by_id('from')
    ActionChains(driver).move_to_element(
        from_date).click().send_keys(first_day).perform()
    to_date = driver.find_element_by_id('to')
    ActionChains(driver).move_to_element(
        to_date).click().send_keys(last_day).perform()
    submit(driver)  # Submit dates

    # Waiting for JavaScript text to be generated and then assigning
    # the text to driver.shifts
    shifts_text = driver.find_element_by_id('reportContent').text

    # Loops through unformatted text of driver.shifts and puts them into
    # a dict with list as shifts
    # Used [1:-1] to ignore header and footer in list from splitting
    for text in shifts_text.splitlines()[1:-1]:
        line = text.split()
        if len(line) == 9:
            name = line[0] + ' ' + line[1]
            spec_date = line[2]
            clock_in = line[3]
            clock_out = line[5]
            location = line[6] + ' ' + line[7]
            hours = line[8]

        if len(line) == 8:
            name = line[0] + ' ' + line[1]
            spec_date = line[2]
            clock_in = line[3]
            clock_out = line[5]
            location = line[6]
            hours = line[7]

        try:
            shifts[spec_date].append({
                'Name': name,
                'Time-In': clock_in,
                'Time-Out': clock_out,
                'Location': location,
                'Hours': hours
            })

        except KeyError:
            shifts[spec_date] = [{
                'Name': name,
                'Time-In': clock_in,
                'Time-Out': clock_out,
                'Location': location,
                'Hours': hours
            }]


def get_menu(driver):
    wait_for(driver, 10, 'XWBEM_Bars', By.CLASS_NAME)
    return driver.find_element_by_class_name('XWBEM_Bars').get_attribute('href')


def entry_menu(driver):
    """
    Puts options of submenu into a dictionary


    :param driver: Current Selenium phantomjs driver instance in use
    :return: URL of chosen option
    """
    # Finds all elements of the submenu and creates an empty dictionary to
    # store their name and url
    sub_menu = driver.find_elements_by_class_name('submenu')

    emp_options = {}

    # Creates a dictionary of name and url for menu options
    for item in sub_menu:
        emp_options[item.text] = item.get_attribute('href')

    # Opening page based on user option eg. 'Time Entry'
    driver.get(emp_options['Time Entry'])

    # Finds urls for time entry
    driver.find_element_by_class_name('left').find_elements_by_tag_name('a')

    # Get's all url for time entry options
    menu_options = driver.find_elements_by_tag_name('a')
    options = dict()

    # Stores name and url pairs into dictionary
    for option in menu_options:
        options[option.text] = option.get_attribute('href')

    # Opens page of usr chosen option eg. 'Time entry' page
    driver.get(options['Time entry'])


if __name__ == '__main__':

    try:
        webadvisor = 'https://webadvisor.coastal.edu'
        emp_console = 'https://coastal.edu/scs/employee'

        username = input('Username: ')
        password = getpass.getpass()  # Defaults to 'Password: '

        exec_path = ChromeDriver().get_path()
        driver = webdriver.Chrome(exec_path)
        driver.get(webadvisor)  # Opening Webadvisor homepage
        login(driver, username, password)
        emp_menu = get_menu(driver)
        driver.get(emp_menu)
        entry_menu(driver)  # Opening Time Entry menu
        first_day, last_day = recent_pay_period(driver)
        driver.get(emp_console)  # Opening Employee Console login
        shifts = get_shifts(driver, first_day, last_day)
        driver.get(webadvisor)
        driver.get(emp_menu)
        entry_menu(driver)  # Opening Time Entry Menu
        fill_timesheet(driver, shifts, last_day)
        submit(driver)  # Submits timesheet based on date
        hours = get_hours(driver)
        print("You've worked {hours} hours.".format(hours=hours))
        input('Press any key to end ...')

        # Logs times that were entered into a log sheet in the current working
        # directory named 'easytime.log'
        log.basicConfig(filename='easytime.log', level=log.INFO, filemode='w')
        log.info(json.dumps(shifts, sort_keys=True, indent=4))
    finally:
        driver.quit()
