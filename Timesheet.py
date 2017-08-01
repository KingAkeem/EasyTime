import EmpLogin


from datetime import date, timedelta, datetime
from pandas import date_range
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep



# Creates a Chrome browser instance and opens Login page
browser = webdriver.Chrome('C:\\Users\Honors Student\Desktop\chromedriver')
browser.get(EmpLogin.oldconsoleurl)

# Finding input elements for username and password
uname = browser.find_element_by_id('uname')
pword = browser.find_element_by_id('pnum')

# Getting username and password from another file
username = EmpLogin.username
password = EmpLogin.password

# Sending keys to elements
uname.send_keys(username)
pword.send_keys(password)

browser.find_element_by_xpath("//input[@type='submit' and @value='Submit']").click() # Submitting filled form


# Finds hours between pay periods through date picker using from and to dates
from_date = browser.find_element_by_id('from')
ActionChains(browser).move_to_element(from_date).click().send_keys('2017-07-20').perform()
to_date = browser.find_element_by_id('to')
ActionChains(browser).move_to_element(to_date).click().send_keys('2017-07-30').perform()
submit_btn = browser.find_element_by_id('Submit')
ActionChains(browser).move_to_element(submit_btn).click().click().perform()

# Getting JavaScript generated html
sleep(5)
time_card = browser.execute_script("return document.getElementById('reportContent')")

time_info = dict()

# Loops through time_card and serializes information into dictionary containing relevant information
for text in time_card.text.splitlines()[1:-1]:


    line = text.split()
    firstName = line[0]
    lastName = line[1]
    specDate = line[2]
    timeIn = line[3]
    timeOut = line[5]
    location = line[6] + " " + line[7]
    hours = line[8]

    try:
        time_info[specDate].append({
        'Name': firstName + " " + lastName,
        'Time-In': timeIn,
        'Time-Out': timeOut,
        'Location': location,
        'Hours': hours
    })
    except KeyError:
        time_info[specDate] = [{
        'Name': firstName + " " + lastName,
        'Time-In': timeIn,
        'Time-Out': timeOut,
        'Location': location,
        'Hours': hours
    }]


# Opening WebAdvisor
browser.get(EmpLogin.webadvisor)
links = browser.find_elements_by_tag_name('a')

# Creates dictionary of urls to page tabs
page_urls = {}
for link in links:
    page_urls[link.text] = link.get_attribute('href')

# Opens Log In page
browser.get(page_urls['Log In'])

# Finds input elements for username and password
USER_NAME = browser.find_element_by_id('USER_NAME')
CURR_PWD = browser.find_element_by_id('CURR_PWD')

# Getting username and password
username = EmpLogin.username
password = EmpLogin.password

# Sends username and password to form
USER_NAME.send_keys(username)
CURR_PWD.send_keys(password)


# Submits form
browser.find_element_by_xpath("//input[@type='submit' and @value='SUBMIT']").click()

# Gets URL for employee console using class name and opens it
emp_console = browser.find_element_by_class_name('XWBEM_Bars').get_attribute('href')
browser.get(emp_console)

# Finds all elements of the submenu and creates an empty dictionary to store their name and url
sub_menu = browser.find_elements_by_class_name('submenu')
emp_menu = {}

# Creates a dictionary of name and url for menu options
for item in sub_menu:
    emp_menu[item.text] = item.get_attribute('href')

browser.get(emp_menu['Time Entry']) # Opens Time Entry menu

browser.find_element_by_class_name('left').find_elements_by_tag_name('a') # Finds all urls for time entry options

# Get's all url for time entry options and creates empty dictionary to store them
time_entry = browser.find_elements_by_tag_name('a')
time_menu = {}

# Stores name and url pairs into dictionary
for t in time_entry:
    time_menu[t.text] = t.get_attribute('href')

browser.get(time_menu['Time entry']) # Opens time entry page to select payperiod

# Checks most recent payperiod box and start/end dates of payperiod
browser.find_element_by_id('LIST_VAR1_1').click()
start_date = browser.find_element_by_id('DATE_LIST_VAR1_1').text
end_date = browser.find_element_by_id('DATE_LIST_VAR2_1').text

# Submits form
browser.find_element_by_xpath("//input[@type='submit' and @value='SUBMIT']").click()

# Splits dates into int value of month, day and year
start_month, start_day, start_year = map(int,start_date.split('/'))
end_month, end_day, end_year = map(int,end_date.split('/'))

# Checking to see if correct range of dates is being produced using Pandas date_range
start = date(datetime.now().year, start_month, start_day)
end = date(datetime.now().year, end_month, end_day)
dates = date_range(start,end,freq='D')
print(dates[1])


browser.close() # Closing Webdriver Instance

