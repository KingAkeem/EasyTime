import EmpLogin
from datetime import date, datetime
from pandas import date_range
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep


def employee_menu(browser_obj):

    # Gets URL for employee console using class name
    return browser_obj.find_element_by_class_name('XWBEM_Bars').get_attribute('href')


def fill_timesheet(browser_obj, *, first_date, last_date):
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
    for curr_date in dates:
        if curr_date in time_info:
            if len(time_info[curr_date]) == 1:
                time_in = browser_obj.find_element_by_id('LIST_VAR4_' + str(index))
                time_out = browser_obj.find_element_by_id('LIST_VAR5_' + str(index))
                time_in.send_keys(time_info[curr_date][0]['Time-In'])
                time_out.send_keys(time_info[curr_date][0]['Time-Out'])

        index += 2


def find_login(browser_obj):

    # Creates dictionary of urls to page tabs
    links = browser_obj.find_elements_by_tag_name('a')
    page_urls = {}
    for link in links:
        page_urls[link.text] = link.get_attribute('href')

    return page_urls['Log In']


def get_info(unformatted_time):
    
    formatted_time = dict()
    # Loops through time_card and serializes information into dictionary containing relevant information
    for text in unformatted_time.text.splitlines()[1:-1]:
        line = text.split()
        first_name = line[0]
        last_name = line[1]
        spec_date = line[2]
        clock_in = line[3]
        clock_out = line[5]
        location = line[6] + " " + line[7]
        hours = line[8]
        try:
            formatted_time[spec_date].append({
                'Name': first_name + " " + last_name,
                'Time-In': clock_in,
                'Time-Out': clock_out,
                'Location': location,
                'Hours': hours
            })
        except KeyError:
            formatted_time[spec_date] = [{
                'Name': first_name + " " + last_name,
                'Time-In': clock_in,
                'Time-Out': clock_out,
                'Location': location,
                'Hours': hours
            }]
    return formatted_time


def get_dates(browser_obj, *, date_start, date_end):

    # Finds hours between pay periods through date picker using from and to dates
    from_date = browser_obj.find_element_by_id('from')
    ActionChains(browser_obj).move_to_element(from_date).click().send_keys(date_start).perform()
    to_date = browser_obj.find_element_by_id('to')
    ActionChains(browser_obj).move_to_element(to_date).click().send_keys(date_end).perform()


def get_shifts(browser_obj):

    # Getting JavaScript generated html
    wait = WebDriverWait(browser_obj, 10)
    wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'tableHead')))
    return browser_obj.find_element_by_id('reportContent')


def recent_payperiod(browser_obj):

    # Checks most recent payperiod box and start/end dates of payperiod
    browser_obj.find_element_by_id('LIST_VAR1_1').click()
    begin_date = browser.find_element_by_id('DATE_LIST_VAR1_1').text
    final_date = browser.find_element_by_id('DATE_LIST_VAR2_1').text

    return begin_date, final_date


def entry_options(browser_obj, *, usr_option):

    browser_obj.find_element_by_class_name('left').find_elements_by_tag_name('a')  # Finds urls for time entry options

    # Get's all url for time entry options and creates empty dictionary to store them
    menu_options = browser_obj.find_elements_by_tag_name('a')
    options = {}

    # Stores name and url pairs into dictionary
    for option in menu_options:
        options[option.text] = option.get_attribute('href')

    return options[usr_option]


def entry_menu(browser_obj, *, option):

    # Finds all elements of the submenu and creates an empty dictionary to store their name and url
    sub_menu = browser_obj.find_elements_by_class_name('submenu')
    emp_options = {}

    # Creates a dictionary of name and url for menu options
    for item in sub_menu:
        emp_options[item.text] = item.get_attribute('href')

    return emp_options[option]


def login_info(browser_obj, *, username, password):
    try:
        # Finding input elements for username and password
        uname = browser_obj.find_element_by_id('uname')
        pword = browser_obj.find_element_by_id('pnum')
        # Sending keys to elements
        uname.send_keys(username)
        pword.send_keys(password)
    except NoSuchElementException:
        try:
            # Finds input elements for username and password
            user_name = browser_obj.find_element_by_id('USER_NAME')
            curr_pwd = browser_obj.find_element_by_id('CURR_PWD')
            # Sends username and password to form
            user_name.send_keys(username)
            curr_pwd.send_keys(password)
        except NoSuchElementException:
            print('Username or password could not be sent!')


def submit(browser_obj):

    try:
        browser_obj.find_element_by_xpath("//input[@type='submit' and @value='SUBMIT']").click()
    except NoSuchElementException:
        try:
            browser_obj.find_element_by_xpath("//input[@type='submit' and @value='Submit']").click()
        except NoSuchElementException:
            try:
                browser_obj.find_element_by_xpath("//input[@type='button' and @value='Submit']").click()
            except NoSuchElementException:
                try:
                    browser_obj.find_element_by_xpath("//input[@type='button' and @value='SUBMIT']").click()
                except NoSuchElementException:
                    print('Could not click submit button!')



if __name__ == '__main__':

    browser = webdriver.Chrome('//Users/Nieceyyyy/Downloads/chromedriver')  # Creates a Chrome browser instance
    browser.get(EmpLogin.emp_login)  # Opens Employee Console login page

    login_info(browser, username=EmpLogin.username, password=EmpLogin.password)  # Fills in login information
    submit(browser)  # Submits form

    get_dates(browser, date_start='2017-08-01', date_end='2017-08-03')  # Retrieves unformatted information of shifts
    submit(browser)  # Submits form

    time_card = get_shifts(browser)  # Returns unformatted html text of shifts
    time_info = get_info(time_card)  # Formats shifts into usable data structure

    browser.get(EmpLogin.webadvisor_home)  # Opens Webadvisor home page
    webadvisor_login = find_login(browser)  # Gets login page for Webadvisor
    browser.get(webadvisor_login)  # Opens Webadvisor login page

    login_info(browser, username=EmpLogin.username, password=EmpLogin.password)  # Fills in login information
    submit(browser)  # Submits form

    emp_menu = employee_menu(browser)  # Retrieves URL for employee menu
    browser.get(emp_menu)  # Opens employee menu page of Webadvisor

    time_menu = entry_menu(browser, option='Time Entry')  # Gets options and returns whichever option is chosen
    browser.get(time_menu)  # Opens Time Entry menu

    entry_page = entry_options(browser, usr_option='Time entry')  # Gets url for time entry page
    browser.get(entry_page)  # Opens time entry page to select payperiod

    start_date, end_date = recent_payperiod(browser)  # Gets start/end date of most recent payperiod
    submit(browser)  # Submits form

    fill_timesheet(browser, first_date=start_date, last_date=end_date)  # Fills out timesheet
    browser.find_element_by_id('VAR5').click()  # Checks box to finalize timesheet
    #submit(browser) # Submits timesheet
