#!/usr/bin/env python3

__author__ = 'Akeem King'

import getpass
import json
import logging as log
from datetime import date, datetime
from helpers.drivers import ChromeDriver
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as exp_cond
from selenium.webdriver.support.wait import WebDriverWait
from sys import argv


class EasyTime:

def fill_timesheet(driver, shifts, last_day):
    """
    Void method that fills timesheet using the first and last date to
    generate the payperiod dates then looping through those dates and
    inserting times.

    :param driver: Current Selenium phantomjs driver instance in use
    :param last_date: Last date of the payperiod
    """

    WebDriverWait(driver, 30).until(exp_cond.title_is('Time entry'))
    # Clicking box to select most recent payperiod
    driver.find_element_by_id('LIST_VAR1_1').click()
    submit(driver)  # Submitting checked box

    time_info = shifts  # Dictionary containing shift information
    processed_dates = []  # Dates that have already been processed

    # Getting list of dates
    dates = driver.find_elements_by_tag_name('p')

    # Loops over dates and sends text to input boxes that match dates
    for dt in dates:
        tag_name = dt.get_attribute('id')
        curr_date = dt.text

        # If value is a date then split it and join back in a the format of
        # '%Y-%m-%d' and gets the current column number
        if 'DATE' in tag_name:
            month, day, year = curr_date.split('/')
            curr_date = '-'.join(('20' + year, month, day))
            column_no = tag_name.split('_')[-1]

        if shifts:
            if 'LIST2' in tag_name and curr_date in shifts:
                time_in = driver.find_element_by_id('LIST_VAR4_' + column_no)
                time_out = driver.find_element_by_id('LIST_VAR5_' + column_no)

                processed = curr_date in processed_dates
                has_two_shifts = len(time_info[curr_date]) == 2

                if processed and has_two_shifts:
                    time_in.send_keys(time_info[curr_date][1]['Time-In'])
                    time_out.send_keys(time_info[curr_date][1]['Time-Out'])

                elif curr_date not in processed_dates:
                    time_in.send_keys(time_info[curr_date][0]['Time-In'])
                    time_out.send_keys(time_info[curr_date][0]['Time-Out'])

                processed_dates.append(curr_date)  # Caching dates

    # Timesheet will not be finalized if the day is equal to/past the
    # last day on the timesheet or if you press any other key besides y.
    date_currently = str(date.today())
    ans = input('Would you like to finalize your time sheet? (Y/N) ')
    date_last = last_day

    if ans == 'y' or ans == 'Y' and date_currently >= date_last:
        print('Your timesheet has been finalized.')
        # Checks box to finalize timesheet
        driver.find_element_by_id('VAR5').click()
    else:
        print('Your timesheet has not been finalized.')


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
    wait = WebDriverWait(driver, 10)
    wait.until(exp_cond.presence_of_all_elements_located((By.ID, 'from')))

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



def login(driver, username, password, page_urls):
    """
    Void method that inputs username and password for employee console

    :param driver: Current Selenium phantomjs driver instance in use
    :return: None
    """

    # If url is webadvisor or Employee Console than next page will be
    # Webadvisor Login page
    if 'webadvisor' in driver.current_url or 'intranet' in driver.current_url:
        try:
            driver.get(page_urls['Log In'])
        except KeyError:
            # Creates dictionary of urls to page tabs
            driver.get('https://webadvisor.coastal.edu')
            links = driver.find_elements_by_tag_name('a')
            for link in links:
                page_urls[link.text] = link.get_attribute('href')
            driver.get(page_urls['Log In'])

    try:
        # Finds input elements for username and password
        user_name = driver.find_element_by_id('USER_NAME')
        curr_pwd = driver.find_element_by_id('CURR_PWD')
        # Sends username and password to form
        user_name.send_keys(username)
        curr_pwd.send_keys(password)
    except NoSuchElementException:
        pass

    submit(driver)

    response = driver.find_element_by_tag_name('div').text
    username_warning = 'Username not found'
    password_warning = 'You entered an invalid password'
    if username_warning in response:
        print('Username not found. Please be sure to enter the username in',
              'all lower case. Please try again.')
        username = input('Username: ')
        password = getpass.getpass()  # Defaults to 'Password: '
        login(driver, username, password, page_urls)
    if password_warning in response:
        print('You entered an invalid password. Passwords are case',
              'sensitive and have at least one upper case',
              'character, one lower case character and one number if',
              'created after July 2007. Please try again.')
        username = input('Username: ')
        password = getpass.getpass()  # Defaults to 'Password: '
        login(driver, username, password, page_urls)


def submit(driver):
    """
    Hits submit button at current browser page

    :param driver: Current Selenium phantomjs driver instance in use
    :return: None
    """

    # If url is not webadvisor then use one of these two submit buttons
    # otherwise use webadvisor submit button
    if 'webadvisor' not in driver.current_url:
        try:
            btn = WebDriverWait(driver, 3).until(
                exp_cond.visibility_of_element_located((
                    By.XPATH, "//input[@type='submit' and @value='Submit']")
                )
            )
            btn.click()
        except (NoSuchElementException, TimeoutException):

            btn = WebDriverWait(driver, 3).until(
                exp_cond.visibility_of_element_located((
                    By.XPATH, "//input[@type='button' and @value='Submit']")
                )
            )
            btn.click()
    else:
        btn = WebDriverWait(driver, 3).until(
            exp_cond.visibility_of_element_located((
                By.XPATH, "//input[@type='submit' and @value='SUBMIT']")
            )
        )
        btn.click()


if __name__ == '__main__':

    try:
        webadvisor = 'https://webadvisor.coastal.edu'
        emp_console = 'https://coastal.edu/scs/employee'

        page_urls = {}  # Dictionary containing page urls
        username = input('Username: ')
        password = getpass.getpass()  # Defaults to 'Password: '

        exec_path = ChromeDriver().get_path()
        WINDOW = "1920,1080"
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size={size}".format(size=WINDOW))
        driver = webdriver.Chrome(exec_path, chrome_options=chrome_options)
        driver.get(webadvisor)  # Opening Webadvisor homepage
        # Logging in into Webadvisor
        login(driver, username, password, page_urls)
        emp_menu = get_menu(driver)
        driver.get(emp_menu)
        entry_menu(driver)  # Opening Time Entry menu

        # Getting dates from most recent payperiod
        first_day, last_day = recent_pay_period(driver)

        driver.close()
        driver = webdriver.Chrome(exec_path)
        driver.get(emp_console)  # Opening Employee Console login
        WebDriverWait(driver, 600).until(
            exp_cond.presence_of_element_located((By.ID, 'from'))
        )

        shifts = get_shifts(driver, first_day, last_day)
        login(driver, username, password, page_urls)  # Logging into Webadvisor
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
