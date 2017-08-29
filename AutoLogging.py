#!/usr/bin/env python3


import getpass
import json
import logging
from datetime import date, datetime
from phantomjs_driver import PhantomJS_driver
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


class AutomateLogging(object):
    """

    Class that automates logging hours into timesheet

    Note:
        Do not include the 'self' paramter in the 'Args' section

    Args:
        driver_path (str): Path to PhantomJs driver executable

    Attributes:
        browser_obj (Webdriver): Object being used to browse webpages
        page_urls (dict): Dictionary containg urls to Webadvisor page
        formatted_time (dict): Dictionary containing shifts

    """

    def __init__(self, driver_path):

        self.browser_obj = webdriver.PhantomJS(driver_path)  # Headless browser
        # self.browser_obj = webdriver.Chrome(driver_path)  # Test browser
        self.page_urls = {}  # Dictionary containg page urls
        self.username = input('Username: ')
        self.password = getpass.getpass()  # Defaults to 'Password: '
        self.formatted_time = dict()

    def fill_timesheet(self, *, last_date):
        """
        Void method that fills timesheet using the first and last date to generate the payperiod dates then looping
        through those dates and inserting the times of the ones that I have worked using an indexing trick

        :param self: Current Selenium phantomjs driver instance in use
        :param last_date: Last date of the payperiod
        :return: None
        """

        self.browser_obj.find_element_by_id('LIST_VAR1_1').click()  # Clicking box to select most recent payperiod
        self.submit()  # Submitting checked box

        # Splits date into a three element list and then converts each element to an int using map function
        end_year, end_month, end_day = map(int, last_date.split('-'))

        time_info = self.formatted_time  # Dictionary containing shift information
        processed_dates = []
        for p in self.browser_obj.find_elements_by_tag_name('p'):
            tag_name = p.get_attribute('id')
            curr_date = p.text
            if 'DATE' in tag_name:
                month, day, year = curr_date.split('/')
                curr_date = '-'.join(('20' + year, month, day))
                column_no = tag_name.split('_')[-1]
            if 'LIST2' in tag_name and curr_date in self.formatted_time:
                time_in = self.browser_obj.find_element_by_id('LIST_VAR4_' + column_no)
                time_out = self.browser_obj.find_element_by_id('LIST_VAR5_' + column_no)

                if curr_date in processed_dates and len(time_info[curr_date]) == 2:
                    time_in.send_keys(time_info[curr_date][1]['Time-In'])
                    time_out.send_keys(time_info[curr_date][1]['Time-Out'])
                elif curr_date not in processed_dates:
                    time_in.send_keys(time_info[curr_date][0]['Time-In'])
                    time_out.send_keys(time_info[curr_date][0]['Time-Out'])
                processed_dates.append(curr_date)
        date_currently = date.today()
        date_last = date(end_year, end_month, end_day)
        ans = input('Would you like to finalize your time sheet? (Y/N) ')
        if ans == 'y' or ans == 'Y' and date_currently >= date_last:
            self.browser_obj.find_element_by_id('VAR5').click()  # Checks box to finalize timesheet

    def get_hours(self):

        return self.browser_obj.find_element_by_id('LIST_VAR2_4').text

    def get_shifts(self, *, date_start, date_end):
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
            self.browser_obj.maximize_window()  # Enlarges window to maximum size
            wait = WebDriverWait(self.browser_obj, 10)  # Creating an explicit wait for Webdriver object for 10 seconds
            wait.until(expected_conditions.presence_of_all_elements_located((By.ID, 'from')))  # Waiting for input field
            from_date = self.browser_obj.find_element_by_id('from')  # Finding datepicker field
            ActionChains(self.browser_obj).move_to_element(from_date).click().send_keys(date_start).perform()  # Sending date to datepicker field
            wait.until(expected_conditions.presence_of_all_elements_located((By.ID, 'to')))  # Finding datepicker field
            to_date = self.browser_obj.find_element_by_id('to')  # Sending date to datepicker field
            ActionChains(self.browser_obj).move_to_element(to_date).click().send_keys(date_end).perform()  # Sending date to datepicker field
            self.submit()  # Submit dates
            wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'tableHead')))  # Waiting for Javascript to generate reportContent
            self.shifts = self.browser_obj.find_element_by_id('reportContent').text  # Getting text from shift content

            # Loops through unformatted text of shifts and puts them into a more useful data container
            for text in self.shifts.splitlines()[1:-1]:
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
                    self.formatted_time[spec_date].append({
                        'Name': name,
                        'Time-In': clock_in,
                        'Time-Out': clock_out,
                        'Location': location,
                        'Hours': hours
                    })
                except (KeyError,):
                    self.formatted_time[spec_date] = [{
                        'Name': name,
                        'Time-In': clock_in,
                        'Time-Out': clock_out,
                        'Location': location,
                        'Hours': hours
                    }]

    def recent_pay_period(self):
        """
        Finds first and late date of most recent payperiod by ID
        :param self: Current Selenium phantomjs driver instance in use

        """

        self.first_day = self.browser_obj.find_element_by_id('DATE_LIST_VAR1_1').text  # First day of pay period
        self.last_day = self.browser_obj.find_element_by_id('DATE_LIST_VAR2_1').text  # Last day of pay period
        self.current_day = datetime.today().strftime('%Y-%m-%d')  # Current day

        return self.first_day, self.current_day

    def entry_options(self, *, usr_option):
        """
        Takes URLs from Time entry menu and puts them into a dictionary

        :param self: Current Selenium phantomjs driver instance in use
        :param usr_option: Option that user wants URL of
        :return: URL of option chosen by user
        """

        self.browser_obj.find_element_by_class_name('left').find_elements_by_tag_name('a')  # Finds urls for time entry

        # Get's all url for time entry options and creates empty dictionary to store them
        menu_options = self.browser_obj.find_elements_by_tag_name('a')
        options = {}

        # Stores name and url pairs into dictionary
        for option in menu_options:
            options[option.text] = option.get_attribute('href')

        self.browser_obj.get(options[usr_option])  # Opens page of usr chosen option eg. 'Time entry' page

    def entry_menu(self, *, option):
        """
        Puts options of submenu into a dictionary


        :param self: Current Selenium phantomjs driver instance in use
        :param option: option that user wants the URL to
        :return: URL of chosen option
        """

        # Opens Employee Menu of Webadvisor by getting the URL using the class name and opening it
        emp_menu = self.browser_obj.find_element_by_class_name('XWBEM_Bars').get_attribute('href')
        self.browser_obj.get(emp_menu)

        # Finds all elements of the submenu and creates an empty dictionary to store their name and url
        sub_menu = self.browser_obj.find_elements_by_class_name('submenu')
        emp_options = {}

        # Creates a dictionary of name and url for menu options
        for item in sub_menu:
            emp_options[item.text] = item.get_attribute('href')

        self.browser_obj.get(emp_options[option])  # opening page based on user option eg. 'Time Entry'

    def login(self):
        """
        Void method that inputs username and password for employee console/webadvisor

        :param self: Current Selenium phantomjs driver instance in use
        :return: None
        """

        # If url is webadvisor or Employee Console than next page will be Webadvisor Login page
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
            # Finding input elements for username and password
            uname = self.browser_obj.find_element_by_id('uname')
            pword = self.browser_obj.find_element_by_id('pnum')
            # Sending keys to elements
            uname.send_keys(self.username)
            pword.send_keys(self.password)
        except NoSuchElementException:
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
            print('Username not found. Please be sure to enter the username in all lower case. Please try again.')
            self.username = input('Username: ')
            self.password = getpass.getpass()  # Defaults to 'Password: '
            self.login()
        if password_warning in response:
            print('You entered an invalid password. Passwords are case sensitive and have at least one upper case',
                  'character, one lower case character and one number if created after July 2007. Please try again.')
            self.username = input('Username: ')
            self.password = getpass.getpass()  # Defaults to 'Password: '
            self.login()

    def submit(self):
        """
        Hits submit button at current browser page

        :param self: Current Selenium phantomjs driver instance in use
        :return: None
        """

        # If url is not webadvisor then use one of these two submit buttons otherwise use webadvisor submit button
        if 'webadvisor' not in self.browser_obj.current_url:
            try:
                btn = WebDriverWait(self.browser_obj, 10).until(
                    expected_conditions.visibility_of_element_located((
                        By.XPATH, "//input[@type='submit' and @value='Submit']")
                    )
                )
                btn.click()
            except (NoSuchElementException, TimeoutException):

                btn = WebDriverWait(self.browser_obj, 10).until(
                    expected_conditions.visibility_of_element_located((
                        By.XPATH, "//input[@type='button' and @value='Submit']")
                    )
                )
                btn.click()
        else:
            btn = WebDriverWait(self.browser_obj, 10).until(
                expected_conditions.visibility_of_element_located((
                    By.XPATH, "//input[@type='submit' and @value='SUBMIT']")
                )
            )
            btn.click()


if __name__ == '__main__':
    driver = PhantomJS_driver()  # Creates a driver
    path = driver.get_path()  # Finds path to phantomjs driver
    if path is None:  # checks if phantomjs driver is present
        ans = input('Most recent version of PhantomJS will be downloaded now')
        if ans == 'y' or ans == 'Y':
            path = driver.download_driver()  # downloads phantomjs driver
            path = driver.get_path()  # finds new phantomjs driver path
    process = AutomateLogging(path)   # Creating Automated Logging object
    try:
        process.browser_obj.get('https://webadvisor.coastal.edu')  # Opening Webadvisor homepage
        process.login()  # Logging in into Webadvisor
        process.entry_menu(option='Time Entry')  # Opening Time Entry menu
        process.entry_options(usr_option='Time entry')  # Choosing time entry option
        start_date, end_date = process.recent_pay_period()  # Getting dates from most recent payperiod
        start_date = start_date[0:6] + '20' + start_date[6:8]  # Making two digit year into four digits eg. 17 -> 2017
        start_date = datetime.strptime(start_date, '%m/%d/%Y').strftime('%Y-%m-%d')  # Formatting start date eg. Y-m-d
        process.browser_obj.get('https://www.coastal.edu/scs/employee')  # Opening Employee Console login
        process.login()  # Logging into employee console
        process.get_shifts(date_start='2017-08-20', date_end=end_date)  # Gets information for shifts between dates
        process.login()  # Logging into Webadvisor
        process.entry_menu(option='Time Entry')  # Opening Time Entry Menu
        process.entry_options(usr_option='Time entry')  # Choosing Time Entry option
        process.fill_timesheet(last_date=end_date)  # Filling time sheet within date range
        process.submit()  # Submits timesheet based on date
        num_hours = process.get_hours()
        print("You've worked", num_hours, "hours.")
        if process.last_day <= process.current_day:
            print('The final revision of your timesheet has been submitted to your supervisor.')
        else:
            print('Your timesheet has been submitted but not finalized.')
        input('Press any key to end ...')
        logging.basicConfig(filename='EasyTime.log', level=logging.INFO, filemode='w')
    finally:
        logging.info(json.dumps(process.formatted_time))
        if process.browser_obj:
            process.browser_obj.quit()  # Closing browser
