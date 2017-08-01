import EmpLogin

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep


# Creates a Chrome browser instance and opens Login page
browser = webdriver.Chrome('/Users/Nieceyyyy/Downloads/chromedriver')
browser.get('https://www.coastal.edu/scs/employee')

# Finding input elements for username and password
uname = browser.find_element_by_id('uname')
pword = browser.find_element_by_id('pnum')

# Getting username and password
username = EmpLogin.username
password = EmpLogin.password

# Sending keys to elements
uname.send_keys(username)
pword.send_keys(password)

# Submitting filled form
browser.find_element_by_xpath("//input[@type='submit' and @value='Submit']").click()


# Finds hours between pay periods through date picker using from and to dates
from_date = browser.find_element_by_id('from')
ActionChains(browser).move_to_element(from_date).click().send_keys('2017-07-20').perform()
to_date = browser.find_element_by_id('to')
ActionChains(browser).move_to_element(to_date).click().send_keys('2017-07-30').perform()
submit_btn = browser.find_element_by_id('Submit')
ActionChains(browser).move_to_element(submit_btn).click().click().perform()

# Getting JavaScript generated html
sleep(10)
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
browser.get('https://webadvisor.coastal.edu')
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


emp_console = browser.find_element_by_class_name('XWBEM_Bars').get_attribute('href')

browser.get(emp_console)

sub_menu = browser.find_elements_by_class_name('submenu')
menu = {}

for item in sub_menu:
    menu[item.text] =item.get_attribute('href')

browser.get(menu['Time Entry'])

browser.close()