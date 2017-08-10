import EmpLogin
from Chrome_Driver import Chrome_Driver
from datetime import date, datetime
from pandas import date_range
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains


class AutomateLogging:
    """

    Class that automates logging hours into timesheet

    Note:
        Do not include the 'self' paramter in the 'Args' section

    Args:
        driver_path (str): Path to Chrome Driver executable

    Attributes:
        browser_obj (Webdriver): Object being used to browse webpages
        page_urls (dict): Dictionary containg urls to Webadvisor page
        formatted_time (dict): Dictionary containing shifts

    """

    def __init__(self, driver_path):

        self.browser_obj = webdriver.Chrome(driver_path)
        self.page_urls = {}
        self.formatted_time = dict()

    def fill_timesheet(self, *, first_date, last_date):
        """
        Void method that fills timesheet using the first and last date to generate the payperiod dates then looping
        through those dates and inserting the times of the ones that I have worked using an indexing trick

        :param self: Current Selenium Chromedriver instance in use
        :param first_date: First date of the payperiod
        :param last_date: Last date of the payperiod
        :return: None
        """

        self.browser_obj.find_element_by_id('LIST_VAR1_1').click() # Clicking box to select most recent payperiod
        self.submit() # Submitting checked box

        # Splits date into a three element list and then converts each element to an int using map function
        start_year, start_month, start_day = map(int, first_date.split('-'))
        end_year, end_month, end_day = map(int, last_date.split('-'))

        # Producing range of dates for payperiod using pandas date_range
        start = date(start_year, start_month, start_day)
        end = date(end_year, end_month, end_day)
        dates = date_range(start, end, freq='D').tolist()

        dates = [str(x) for x in dates] # Converting each Timestamp element to a string
        dates = [x.replace(' 00:00:00', '') for x in dates] # Removing extra time eg. second, hours and minutes

        index = 1  # Index of first field
        time_info = self.formatted_time  # Dictionary containing shift information

        # Loops through range of dates and sends times to fields based on how many shifts exist per day
        for curr_date in dates:

            if curr_date in time_info:
                if len(time_info[curr_date]) == 1:
                    time_in = self.browser_obj.find_element_by_id('LIST_VAR4_' + str(index))  # Gets Time in field
                    time_out = self.browser_obj.find_element_by_id('LIST_VAR5_' + str(index))  # Gets Time out field
                    time_in.send_keys(time_info[curr_date][0]['Time-In'])  # Sends time out info to time out field
                    time_out.send_keys(time_info[curr_date][0]['Time-Out'])  # Sends time in info to time in field

                if len(time_info[curr_date]) == 2:
                    time_in = self.browser_obj.find_element_by_id('LIST_VAR4_' + str(index))
                    time_out = self.browser_obj.find_element_by_id('LIST_VAR5_' + str(index))
                    time_in.send_keys(time_info[curr_date][0]['Time-In'])
                    time_out.send_keys(time_info[curr_date][0]['Time-Out'])

                    time_in = self.browser_obj.find_element_by_id('LIST_VAR4_' + str(index+1))
                    time_out = self.browser_obj.find_element_by_id('LIST_VAR5_' + str(index+1))
                    time_in.send_keys(time_info[curr_date][1]['Time-In'])
                    time_out.send_keys(time_info[curr_date][1]['Time-Out'])

            index += 2 # Moving to next day

    def get_shifts(self, *, date_start, date_end):
        """
        Expicitly waits for JavaScript to generate shift content


        :param self: Current Selenium Chromedriver instance in use
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
        :param self: Current Selenium Chromedriver instance in use

        """

        first_day = self.browser_obj.find_element_by_id('DATE_LIST_VAR1_1').text # First day of pay period
        current_day = datetime.today().strftime('%Y-%m-%d') # Current day

        return first_day, current_day

    def entry_options(self, *, usr_option):
        """
        Takes URLs from Time entry menu and puts them into a dictionary

        :param self: Current Selenium Chromedriver instance in use
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

        self.browser_obj.get(options[usr_option]) # Opens page of usr chosen option eg. 'Time entry' page

    def entry_menu(self, *, option):
        """
        Puts options of submenu into a dictionary


        :param self: Current Selenium Chromedriver instance in use
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

        self.browser_obj.get(emp_options[option]) # opening page based on user option eg. 'Time Entry'

    def login_info(self, *, username, password):
        """
        Void method that inputs username and password for employee console/webadvisor

        :param self: Current Selenium Chromedriver instance in use
        :param username: User's login username
        :param password: User's login password
        :return: None
        """

        # If url is webadvisor or Employee Console than next page will be Webadvisor Login page
        if 'webadvisor' in self.browser_obj.current_url or 'intranet' in self.browser_obj.current_url:
            try:
                self.browser_obj.get(self.page_urls['Log In'])
            except KeyError:
                # Creates dictionary of urls to page tabs
                self.browser_obj.get(EmpLogin.webadvisor_home)
                links = self.browser_obj.find_elements_by_tag_name('a')
                for link in links:
                    print(link.text)
                    self.page_urls[link.text] = link.get_attribute('href')
                self.browser_obj.get(self.page_urls['Log In'])

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


if __name__ == '__main__':
    try:
        driver = Chrome_Driver() # Finds path to Chrome Driver
        login_process = AutomateLogging(driver.find_path()) # Creating Automated Logging object
        login_process.browser_obj.get(EmpLogin.webadvisor_home) # Opening Webadvisor homepage
        login_process.login_info(username=EmpLogin.username, password=EmpLogin.password) # Logging in into Webadvisor
        login_process.entry_menu(option='Time Entry') # Opening Time Entry menu
        login_process.entry_options(usr_option='Time entry') # Choosing time entry option
        start_date, end_date = login_process.recent_pay_period() # Getting dates from most recent payperiod
        start_date = start_date[0:6] + '20' + start_date[6:8] # Making two digit year into four digits eg. 17 -> 2017
        start_date = datetime.strptime(start_date, '%m/%d/%Y').strftime('%Y-%m-%d') # Formatting start date eg. Y-m-d
        login_process.browser_obj.get(EmpLogin.emp_login) # Opening Employee Console login
        login_process.login_info(username=EmpLogin.username, password=EmpLogin.password) # Logging into employee console
        login_process.get_shifts(date_start=start_date, date_end=end_date) # Gets information for shifts between dates
        login_process.login_info(username=EmpLogin.username, password=EmpLogin.password) # Logging into Webadvisor
        login_process.entry_menu(option='Time Entry') # Opening Time Entry Menu
        login_process.entry_options(usr_option='Time entry') # Choosing Time Entry option
        login_process.fill_timesheet(first_date=start_date, last_date=end_date) # Filling time sheet within date range
        login_process.submit_timesheet(finalized='N') # Submitting timesheet
    finally:
        login_process.browser_obj.quit() # Closing browser
