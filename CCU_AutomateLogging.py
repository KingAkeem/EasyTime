import EmpLogin
from Chrome_Driver import Chrome_Driver
from datetime import date, datetime
from pandas import date_range
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains


class AutomateLogging:

    def __init__(self):
        driver = Chrome_Driver()
        driver_path = driver.find_path()
        self.browser_obj = webdriver.Chrome(driver_path)


    def employee_menu(self):
        """
        Gives url for Employee menu from Webadvisor homepage


        :param self: Current Selenium Chromedriver instance in use
        :return: URL for employee menu from Webadvisor homepage
        """

        # Gets URL for employee console using class name
        url_to_open = self.browser_obj.find_element_by_class_name('XWBEM_Bars').get_attribute('href')
        self.browser_obj.get(url_to_open)


    def fill_timesheet(self, *, first_date, last_date):
        """
        Void method that fills timesheet using the first and last date to generate the payperiod dates then looping
        through those dates and inserting the times of the ones that I have worked

        :param self: Current Selenium Chromedriver instance in use
        :param first_date: First date of the payperiod
        :param last_date: Last date of the payperiod
        :return: None
        """

        # Splits dates into int value of month, day and year
        start_month, start_day, start_year = map(int, first_date.split('/'))
        end_month, end_day, end_year = map(int, last_date.split('/'))

        # Checking to see if correct range of dates is being produced using Pandas date_range
        start = date(datetime.now().year, start_month, start_day)
        end = date(datetime.now().year, end_month, end_day)
        dates = date_range(start, end, freq='D').tolist()

        # Converting Timestamps to strings and then removes hours,seconds, and minutes from string
        dates = [str(x) for x in dates]
        dates = [x.replace(' 00:00:00', '') for x in dates]

        index = 1
        time_info = self.formatted_time

        for curr_date in dates:
            if curr_date in time_info:
                if len(time_info[curr_date]) == 1:
                    time_in = self.browser_obj.find_element_by_id('LIST_VAR4_' + str(index))
                    time_out = self.browser_obj.find_element_by_id('LIST_VAR5_' + str(index))
                    time_in.send_keys(time_info[curr_date][0]['Time-In'])
                    time_out.send_keys(time_info[curr_date][0]['Time-Out'])

                if len(time_info[curr_date]) == 2:
                    time_in = self.browser_obj.find_element_by_id('LIST_VAR4_' + str(index))
                    time_out = self.browser_obj.find_element_by_id('LIST_VAR5_' + str(index))
                    time_in.send_keys(time_info[curr_date][0]['Time-In'])
                    time_out.send_keys(time_info[curr_date][0]['Time-Out'])

                    time_in = self.browser_obj.find_element_by_id('LIST_VAR4_' + str(index+1))
                    time_out = self.browser_obj.find_element_by_id('LIST_VAR5_' + str(index+1))
                    time_in.send_keys(time_info[curr_date][1]['Time-In'])
                    time_out.send_keys(time_info[curr_date][1]['Time-Out'])

            index += 2

    def find_login(self):
        """
        Goes through urls on page tabs and then finds the one for the Login page

        :param self: Current Selenium Chromedriver instance in use
        :return: URL for Webadvisor login page
        """

        # Creates dictionary of urls to page tabs
        self.browser_obj.get(EmpLogin.webadvisor_home)
        links = self.browser_obj.find_elements_by_tag_name('a')
        page_urls = {}
        for link in links:
            page_urls[link.text] = link.get_attribute('href')

        self.browser_obj.get(page_urls['Log In'])

    def get_info(self):
        """
        Takes html from shift reports and serializes it into a more useful data structure. Creates a structure that
        contains dictionaries inside of list inside of dictionaries. The main dictionary contains dates as keys and the
        values are lists that contain dictionaries with useful names as keys/values. For example, if the user worked on
        '1999-19-09' and the user's name is 'John Doe' and their location was 'Paradise Island". An element inside of
        the dict would look like {'1999-19-09':[{'Name':'John Doe', 'Location':'Paradise Island'}]}.


        :param self: Current Selenium object instance in use
        :return: Dictionary containing list of dictionaries with relevant information
        """

        self.formatted_time = dict()
        # Loops through time_card and serializes information into dictionary containing relevant information
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
            except KeyError:
                self.formatted_time[spec_date] = [{
                    'Name': name,
                    'Time-In': clock_in,
                    'Time-Out': clock_out,
                    'Location': location,
                    'Hours': hours
                }]
        return self.formatted_time

    def get_dates(self, *, date_start, date_end):
        """
        Void method that sends start and end dates to datepicker to allow you to pull up a report containing all the
        shifts between the two dates


        :param self: Current Selenium Chromedriver instance in use
        :param date_start: Start date of shifts you want to see
        :param date_end: Lsat day of shifts you want to see
        :return: None
        """

        # Finds hours between pay periods through date picker using from and to dates
        wait = WebDriverWait(self.browser_obj, 10)
        wait.until(expected_conditions.presence_of_all_elements_located((By.ID,'from')))
        from_date = self.browser_obj.find_element_by_id('from')
        ActionChains(self.browser_obj).move_to_element(from_date).click().send_keys(date_start).perform()
        wait.until(expected_conditions.presence_of_all_elements_located((By.ID,'to')))
        to_date = self.browser_obj.find_element_by_id('to')
        ActionChains(self.browser_obj).move_to_element(to_date).click().send_keys(date_end).perform()
        #curr_date = self.browser_obj.find_element_by_class_name('ui-state-default ui-state-highlight ui-state-active')
        #ActionChains(self.browser_obj).move_to_element(curr_date).click().perform()
        self.submit()

    def get_shifts(self):
        """
        Expicitly waits for JavaScript to generate shift content


        :param self: Current Selenium Chromedriver instance in use
        :return: HTML source code containing shifts
        """

        try:
             return self.shifts
        except AttributeError:
            # Getting JavaScript generated html
            wait = WebDriverWait(self.browser_obj, 10)
            wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'tableHead')))
            self.shifts = self.browser_obj.find_element_by_id('reportContent').text


    def recent_payperiod(self):
        """
        Finds first and late date of most recent payperiod by ID and checks box to send you to the time entry page to
        input times

        :param self: Current Selenium Chromedriver instance in use
        :return begin_date: First date of payperiod
        :return final_date: Last date of payperiod

        """
        # Checks most recent payperiod box and start/end dates of payperiod
        self.browser_obj.find_element_by_id('LIST_VAR1_1').click()
        begin_date = self.browser_obj.find_element_by_id('DATE_LIST_VAR1_1').text
        final_date = self.browser_obj.find_element_by_id('DATE_LIST_VAR2_1').text

        self.submit()

        return begin_date, final_date

    def entry_options(self, *, usr_option):
        """
        Takes URLs from Time entry menu and puts them into a dictionary

        :param self: Current Selenium Chromedriver instance in use
        :param usr_option: Option that user wants URL of
        :return: URL of option chosen by user
        """

        self.browser_obj.find_element_by_class_name('left').find_elements_by_tag_name('a')  # Finds urls for time entry options

        # Get's all url for time entry options and creates empty dictionary to store them
        menu_options = self.browser_obj.find_elements_by_tag_name('a')
        options = {}

        # Stores name and url pairs into dictionary
        for option in menu_options:
            options[option.text] = option.get_attribute('href')

        self.browser_obj.get(options[usr_option])

    def entry_menu(self, *, option):
        """
        Puts options of submenu into a dictionary


        :param self: Current Selenium Chromedriver instance in use
        :param option: option that user wants the URL to
        :return: URL of chosen option
        """

        # Finds all elements of the submenu and creates an empty dictionary to store their name and url
        sub_menu = self.browser_obj.find_elements_by_class_name('submenu')
        emp_options = {}

        # Creates a dictionary of name and url for menu options
        for item in sub_menu:
            emp_options[item.text] = item.get_attribute('href')

        self.browser_obj.get(emp_options[option])

    def login_info(self, *, username, password):
        """
        Void method that inputs username and password for employee console/webadvisor

        :param self: Current Selenium Chromedriver instance in use
        :param username: User's login username
        :param password: User's login password
        :return: None
        """
        try:
            # Finding input elements for username and password
            uname = self.browser_obj.find_element_by_id('uname')
            pword = self.browser_obj.find_element_by_id('pnum')
            # Sending keys to elements
            uname.send_keys(username)
            pword.send_keys(password)
        except NoSuchElementException:
            try:
                # Finds input elements for username and password
                user_name = self.browser_obj.find_element_by_id('USER_NAME')
                curr_pwd = self.browser_obj.find_element_by_id('CURR_PWD')
                # Sends username and password to form
                user_name.send_keys(username)
                curr_pwd.send_keys(password)
            except NoSuchElementException:
                print('Username or password could not be sent!')

        self.submit()

    def submit(self):
        """
        Hits submit button at current browser page

        :param self: Current Selenium Chromedriver instance in use
        :return: None
        """

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

    def submit_timesheet(self, *, finalized):
        """
        Void methoat that submits timesheet and checkboxa to finalize it depending on input
        :param self: Current Selenium Chromedriver instance in use
        :param finalized: Whether or not to officially send Timesheet in
        :return: None
        """

        if finalized == 'Yes' or finalized == 'Y' or finalized == 'y':
            self.browser_obj.find_element_by_id('VAR5').click()  # Checks box to finalize timesheet

        self.submit()
        self.browser_obj.quit()


if __name__ == '__main__':
    try:
        login_process = AutomateLogging()
        # Getting times from webadvisor
        login_process.browser_obj.get(EmpLogin.webadvisor_home)
        login_process.find_login()
        login_process.login_info(username=EmpLogin.username, password=EmpLogin.password)
        login_process.employee_menu()
        login_process.entry_menu(option='Time Entry')
        login_process.entry_options(usr_option='Time entry')
        start_date, end_date = login_process.recent_payperiod()
        start_date = start_date[0:6] + '20' + start_date[6:8]
        end_date = end_date[0:6] + '20' + end_date[6:8]
        print(start_date,end_date)
        start_date = datetime.strptime(start_date, '%m/%d/%Y').strftime('%Y-%d-%m')
        end_date = datetime.strptime(end_date, '%m/%d/%Y').strftime('%Y-%d-%m')
        print(start_date, end_date)
        login_process.browser_obj.get(EmpLogin.emp_login)
        login_process.login_info(username=EmpLogin.username, password=EmpLogin.password)
        login_process.get_dates(date_start=start_date, date_end=end_date)
        print(login_process.get_shifts())
        login_process.get_info()
        login_process.find_login()
        login_process.login_info(username=EmpLogin.username, password=EmpLogin.password)
        login_process.employee_menu()
        login_process.entry_menu(option='Time Entry')
        login_process.entry_options(usr_option='Time entry')
        login_process.fill_timesheet(first_date=start_date, last_date=end_date)
        login_process.submit_timesheet(finalized='N')
    finally:
        login_process.browser_obj.quit()
