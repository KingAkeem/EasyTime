
import esky
import getpass
import sys
from phantomjs_driver import PhantomJS_driver
from datetime import date, datetime, time
from pandas import date_range
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains


if hasattr(sys,"frozen"):
    #app = esky.Esky(sys.executable,"https://example-app.com/downloads/")
    app = esky.Esky(sys.executable,"http://localhost:8000/Time Entry Updates")
    try:
        app.auto_update()
    except Exception as e:
        print ("ERROR UPDATING APP:", e)



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

        self.browser_obj = webdriver.PhantomJS(driver_path)
        self.username = input('Username: ')
        self.password = getpass.getpass()
        self.page_urls = {}
        self.formatted_time = dict()

    def fill_timesheet(self, *, first_date, last_date):
        """
        Void method that fills timesheet using the first and last date to generate the payperiod dates then looping
        through those dates and inserting the times of the ones that I have worked using an indexing trick

        :param self: Current Selenium phantomjs driver instance in use
        :param first_date: First date of the payperiod
        :param last_date: Last date of the payperiod
        :return: None
        """

        self.browser_obj.find_element_by_id('LIST_VAR1_1').click()  # Clicking box to select most recent payperiod
        self.submit()  # Submitting checked box

        # Splits date into a three element list and then converts each element to an int using map function
        start_year, start_month, start_day = map(int, first_date.split('-'))
        end_year, end_month, end_day = map(int, last_date.split('-'))

        # Producing range of dates for payperiod using pandas date_range
        start = date(start_year, start_month, start_day)
        end = date(end_year, end_month, end_day)
        dates = date_range(start, end, freq='D').tolist()

        dates = [str(x) for x in dates]  # Converting each Timestamp element to a string
        dates = [x.replace(' 00:00:00', '') for x in dates]  # Removing extra time eg. second, hours and minutes

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

            index += 2  # Moving to next day

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
                print('Username or password could not be sent!')

        self.submit()

        response = process.browser_obj.find_element_by_tag_name('div').text
        username_warning = 'Username not found'
        password_warning = 'You entered an invalid password'
        if username_warning in response:
            print('Username not found. Please be sure to enter the username in all lower case. Please try again.')
            self.username = input('Username: ')
        if password_warning in response:
            print('You entered an invalid password. Passwords are case sensitive and have at least one upper case',
                  'character, one lower case character and one number if created after July 2007. Please try again.')
            self.password = getpass.getpass()
            self.login()

    def submit(self):
        """
        Hits submit button at current browser page

        :param self: Current Selenium phantomjs driver instance in use
        :return: None
        """
        try:
            now = datetime.now()
            curr_time = time(now.hour, now.minute, now.second)
            final_time = time(23, 59, 59)
            if self.last_day == self.current_day and curr_time > final_time:
                self.browser_obj.find_element_by_id('VAR5').click()  # Checks box to finalize timesheet
        except AttributeError:
            pass

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
        process.get_shifts(date_start=start_date, date_end=end_date)  # Gets information for shifts between dates
        process.login()  # Logging into Webadvisor
        process.entry_menu(option='Time Entry')  # Opening Time Entry Menu
        process.entry_options(usr_option='Time entry')  # Choosing Time Entry option
        process.fill_timesheet(first_date=start_date, last_date=end_date)  # Filling time sheet within date range
        print('Shifts from', start_date, 'to', end_date,'have been filled and submitted.')
        process.submit()  # Submits timesheet based on date
        if process.last_day == process.current_day:
            print('The final revision of your timesheet has been submitted to your supervisor.')
        else:
            print('Your timesheet has been submitted but not finalized.')
        input('Press any key to end ...')
    finally:
        if process.browser_obj:
            process.browser_obj.quit()  # Closing browser

