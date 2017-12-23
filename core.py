#!/usr/bin/env python3

__author__ = 'Akeem King'

"""
This is a python script that is used for automating my time logging for my job's
timesheet.
"""


import getpass
import json
import logging
from datetime import date, datetime
from helpers.drivers import PhantomJSDriver, ChromeDriver
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from sys import argv


class AutomateLogging:
    """

    Class that automates logging hours into time entry website.

    Note:
        Do not include the 'self' parameter in the 'Args' section

    Args:
        driver_path (str): Path to PhantomJs driver executable

    Attributes:
        browser_obj (Webdriver): Object being used to browse webpages
        page_urls (dict): Dictionary containg urls to Webadvisor page
        formatted_time (dict): Dictionary containing shifts

    """

    def __init__(self):
        self.browser_obj = None
        self.page_urls = {}  # Dictionary containing page urls
        self.username = input('Username: ')
        self.password = getpass.getpass()  # Defaults to 'Password: '

    def __enter__(self):

        self.browser_obj = webdriver.Chrome(ChromeDriver().get_path())
        return self

    def __exit__(self, *args):
        self.browser_obj.quit()

    def fill_timesheet(self):
        """
        Void method that fills timesheet using the first and last date to
        generate the payperiod dates then looping through those dates and
        inserting times.

        :param self: Current Selenium phantomjs driver instance in use
        :param last_date: Last date of the payperiod
        """

        WebDriverWait(self.browser_obj, 30).until(
            expected_conditions.title_is('Time entry')
        )
        # Clicking box to select most recent payperiod
        self.browser_obj.find_element_by_id('LIST_VAR1_1').click()
        self.submit()  # Submitting checked box

        time_info = self.shifts  # Dictionary containing shift information
        processed_dates = []  # Dates that have already been processed

        # Getting list of dates
        dates = self.browser_obj.find_elements_by_tag_name('p')

        # Loops over dates and sends text to input boxes that match dates
        for d in dates:
            tag_name = d.get_attribute('id')
            curr_date = d.text

            # If value is a date then split it and join back in a the format of
            # '%Y-%m-%d' and gets the current column number
            if 'DATE' in tag_name:
                month, day, year = curr_date.split('/')
                curr_date = '-'.join(('20' + year, month, day))
                column_no = tag_name.split('_')[-1]

            if 'LIST2' in tag_name and curr_date in self.shifts:
                time_in = self.browser_obj.find_element_by_id(
                    'LIST_VAR4_' + column_no
                )
                time_out = self.browser_obj.find_element_by_id(
                    'LIST_VAR5_' + column_no
                )

                if (
                    # Checking if date was processed
                    curr_date in processed_dates
                    # and if date contains two shifts
                    and len(time_info[curr_date]) == 2
                ):
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
        date_last = self.last_day
        if ans == 'y' or ans == 'Y' and date_currently >= date_last:
            print('Your timesheet has been finalized.')
            # Checks box to finalize timesheet
            self.browser_obj.find_element_by_id('VAR5').click()
        else:
            print('Your timesheet has not been finalized.')

    def recent_pay_period(self):
        """Finds first and lates date of most recent payperiod by ID
        :param self: Current Selenium PhantomJS driver instance in use
        """
        self.first_day = self.browser_obj.find_element_by_id(
            'DATE_LIST_VAR1_1'
        ).text  # First day of pay period
        self.last_day = self.browser_obj.find_element_by_id(
            'DATE_LIST_VAR2_1'
        ).text  # Last day of pay period
        self.current_day = datetime.today().strftime('%Y-%m-%d')  # Current Day
        # Making two digit year into four digits eg. 17 -> 2017
        self.first_day = self.first_day[0:6] + '20' + self.first_day[6:8]
        # Making two digit year into four digits eg. 17 -> 2017
        self.last_day = self.last_day[0:6] + '20' + self.last_day[6:8]
        self.first_day = datetime.strptime(self.first_day, '%m/%d/%Y').strftime(
            '%Y-%m-%d'
        )  # Formatting start date eg. Y-m-d
        self.last_day = datetime.strptime(self.last_day, '%m/%d/%Y').strftime(
            '%Y-%m-%d'
        )  # Same as previous

    def get_hours(self):

        return self.browser_obj.find_element_by_id('LIST_VAR2_4').text

    def get_shifts(self):
        """
        Expicitly waits for JavaScript to generate shift content


        :param self: Current Selenium phantomjs driver instance in use
        :param date_start: beginning date of shifts
        :param date_end: last date of shifts
        :return: None
        """

        try:
            return self.shifts  # Returns shifts if it already exists
        except AttributeError:
            self.shifts = dict()

            # Enlarges window to maximum size
            self.browser_obj.maximize_window()

            # Webdriver explicitly waits up until 10 seoncds or when it finds
            # the chosen element by id then it moves to
            # the element and sends data
            wait = WebDriverWait(self.browser_obj, 10)
            wait.until(expected_conditions.presence_of_all_elements_located((
                By.ID, 'from'
            )))

            from_date = self.browser_obj.find_element_by_id('from')
            ActionChains(self.browser_obj).move_to_element(
                from_date).click().send_keys(self.first_day).perform()
            to_date = self.browser_obj.find_element_by_id('to')
            ActionChains(self.browser_obj).move_to_element(
                to_date).click().send_keys(self.last_day).perform()
            self.submit()  # Submit dates

            # Waiting for JavaScript text to be generated and then assigning
            # the text to self.shifts
            """
            wait.until(expected_conditions.presence_of_element_located((
                By.CLASS_NAME, 'tableHead'
            )))
            """
            self.shifts_text = self.browser_obj.find_element_by_id(
                'reportContent').text
            # Loops through unformatted text of self.shifts and puts them into
            # a dict with list as shifts
            # Used [1:-1] to ignore header and footer in list from splitting
            for text in self.shifts_text.splitlines()[1:-1]:
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
                    self.shifts[spec_date].append({
                        'Name': name,
                        'Time-In': clock_in,
                        'Time-Out': clock_out,
                        'Location': location,
                        'Hours': hours
                    })
                except (KeyError,):
                    self.shifts[spec_date] = [{
                        'Name': name,
                        'Time-In': clock_in,
                        'Time-Out': clock_out,
                        'Location': location,
                        'Hours': hours
                    }]

    def entry_menu(self):
        """
        Puts options of submenu into a dictionary


        :param self: Current Selenium phantomjs driver instance in use
        :return: URL of chosen option
        """

        # Opens Employee Menu of Webadvisor by getting the URL using the class
        # name and opening it
        emp_menu = self.browser_obj.find_element_by_class_name(
            'XWBEM_Bars').get_attribute('href')
        self.browser_obj.get(emp_menu)

        # Finds all elements of the submenu and creates an empty dictionary to
        # store their name and url
        sub_menu = self.browser_obj.find_elements_by_class_name('submenu')
        emp_options = {}

        # Creates a dictionary of name and url for menu options
        for item in sub_menu:
            emp_options[item.text] = item.get_attribute('href')

        # Opening page based on user option eg. 'Time Entry'
        self.browser_obj.get(emp_options['Time Entry'])

        self.browser_obj.find_element_by_class_name(
            'left').find_elements_by_tag_name('a')  # Finds urls for time entry

        # Get's all url for time entry options
        menu_options = self.browser_obj.find_elements_by_tag_name('a')
        options = dict()

        # Stores name and url pairs into dictionary
        for option in menu_options:
            options[option.text] = option.get_attribute('href')

        # Opens page of usr chosen option eg. 'Time entry' page
        self.browser_obj.get(options['Time entry'])

        self.first_day = self.browser_obj.find_element_by_id(
            'DATE_LIST_VAR1_1').text  # First day of pay period
        self.last_day = self.browser_obj.find_element_by_id(
            'DATE_LIST_VAR2_1').text  # Last day of pay period

    def login(self):
        """
        Void method that inputs username and password for employee console

        :param self: Current Selenium phantomjs driver instance in use
        :return: None
        """

        # If url is webadvisor or Employee Console than next page will be
        # Webadvisor Login page
        if 'webadvisor' in self.browser_obj.current_url or 'intranet' in self.browser_obj.current_url:
            try:
                self.browser_obj.get(self.page_urls['Log In'])
            except KeyError:
                # Creates dictionary of urls to page tabs
                self.browser_obj.get('https://webadvisor.coastal.edu')
                links = self.browser_obj.find_elements_by_tag_name('a')
                for link in links:
                    self.page_urls[link.text] = link.get_attribute('href')
                self.browser_obj.get(self.page_urls['Log In'])

        try:
            # Finds input elements for username and password
            user_name = self.browser_obj.find_element_by_id('USER_NAME')
            curr_pwd = self.browser_obj.find_element_by_id('CURR_PWD')
            # Sends username and password to form
            user_name.send_keys(self.username)
            curr_pwd.send_keys(self.password)
        except NoSuchElementException:
            pass

        self.submit()

        response = process.browser_obj.find_element_by_tag_name('div').text
        username_warning = 'Username not found'
        password_warning = 'You entered an invalid password'
        if username_warning in response:
            print('Username not found. Please be sure to enter the username in',
                  'all lower case. Please try again.')
            self.username = input('Username: ')
            self.password = getpass.getpass()  # Defaults to 'Password: '
            self.login()
        if password_warning in response:
            print('You entered an invalid password. Passwords are case',
                  'sensitive and have at least one upper case',
                  'character, one lower case character and one number if',
                  'created after July 2007. Please try again.')
            self.username = input('Username: ')
            self.password = getpass.getpass()  # Defaults to 'Password: '
            self.login()

    def submit(self):
        """
        Hits submit button at current browser page

        :param self: Current Selenium phantomjs driver instance in use
        :return: None
        """

        # If url is not webadvisor then use one of these two submit buttons
        # otherwise use webadvisor submit button
        if 'webadvisor' not in self.browser_obj.current_url:
            try:
                btn = WebDriverWait(self.browser_obj, 3).until(
                    expected_conditions.visibility_of_element_located((
                        By.XPATH, "//input[@type='submit' and @value='Submit']")
                    )
                )
                btn.click()
            except (NoSuchElementException, TimeoutException):

                btn = WebDriverWait(self.browser_obj, 3).until(
                    expected_conditions.visibility_of_element_located((
                        By.XPATH, "//input[@type='button' and @value='Submit']")
                    )
                )
                btn.click()
        else:
            btn = WebDriverWait(self.browser_obj, 3).until(
                expected_conditions.visibility_of_element_located((
                    By.XPATH, "//input[@type='submit' and @value='SUBMIT']")
                )
            )
            btn.click()


if __name__ == '__main__':

    webadvisor = 'https://webadvisor.coastal.edu'
    emp_console = 'https://coastal.edu/scs/employee'

    with AutomateLogging() as process:
        process.browser_obj.get(webadvisor)  # Opening Webadvisor homepage
        process.login()  # Logging in into Webadvisor
        process.entry_menu()  # Opening Time Entry menu
        process.recent_pay_period()  # Getting dates from most recent payperiod
        process.browser_obj.get(emp_console)  # Opening Employee Console login
        WebDriverWait(process.browser_obj, 600).until(
            expected_conditions.presence_of_element_located((By.ID, 'from'))
        )
        process.get_shifts()  # Gets information for shifts between dates
        process.login()  # Logging into Webadvisor
        process.entry_menu()  # Opening Time Entry Menu
        process.fill_timesheet()  # Filling time sheet within date range
        process.submit()  # Submits timesheet based on date
        hours = process.get_hours()
        print("You've worked {hours} hours.".format(hours=hours))
        input('Press any key to end ...')

        # Logs times that were entered into a log sheet in the current working
        # directory named 'easytime.log'
        logging.basicConfig(
            filename='easytime.log',
            level=logging.INFO,
            filemode='w'
        )
        logging.info(json.dumps(process.shifts, sort_keys=True, indent=4))
