import getpass

from selenium.webdriver.support.expected_conditions import (
                            visibility_of_element_located as is_visible)
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


def submit(driver):
    """Clicks submit button

    Checks current webpage url and uses the appropriate submit button based on
    the url.

    Args:
        driver: driver instance being used
    """

    if 'webadvisor' not in driver.current_url:
        btn = wait_for(driver, 3, 'Submit', By.ID)
        btn.click()
    else:
        webadv_xpath = "//input[@type='submit' and @value='SUBMIT']"
        btn = wait_for(driver, 3, webadv_xpath, By.XPATH)
        btn.click()


def wait_for(driver, time, element, selector=By.ID):
    """Waits for element to be found if it exists

    Waits for element to be visible and if not then a timeout
    exception is thrown. Just a wraapper around the WebDriverWait

    Args:
        driver: driver instance being used
        time: amount of time before TimeoutException will be thrown
        element: element that is being waited for

    Returns:
        Returns element that was waited for if it exists else TimeoutException
        will be returned
    """

    return WebDriverWait(driver, time).until(is_visible((selector, element)))


def login(driver, username, password):
    """Logs into website

    Finds Log In link on homepage and clicks on it, then sends the strings that
    were passed in as username and password.

    Args:
        driver: driver instance being used
        username: Login username
        password: Login password

    """

    if 'webadvisor' in driver.current_url:
        links = driver.find_elements_by_tag_name('a')
        for link in links:
            url = link.get_attribute('href')
            if link.text == 'Log In':
                driver.get(url)
                break

    wait_for(driver, 30, 'USER_NAME')
    uname = driver.find_element_by_id('USER_NAME')
    pword = driver.find_element_by_id('CURR_PWD')
    uname.send_keys(username)
    pword.send_keys(password)
    submit(driver)

    resp = driver.find_element_by_tag_name('div').text
    uname_warning = 'Username not found'
    pword_warning = 'YOu entered an invalid password'

    if uname_warning in resp:
        print('Username not found. Please be sure to enter the username in',
              'all lower case. Please try again.')
        username = input('Username: ')
        password = getpass.getpass()
        login(driver, username, password)

    if pword_warning in resp:
        print('You entered an invalid password. Passwords are case',
              'sensitive and have at least one upper case',
              'character, one lower case character and one number if',
              'created after July 2007. Please try again.')
        username = input('Username: ')
        password = getpass.getpass()
        login(driver, username, password)


def get_menu(driver):
    wait_for(driver, 10, 'XWBEM_Bars', By.CLASS_NAME)
    return driver.find_element_by_class_name('XWBEM_Bars').get_attribute('href')


def get_hours(driver):
    """ Gets hours worked through payperiod

    Args:
        driver: instance being used

    Returns:
        str containing hours worked during recent payperiod
    """

    return driver.find_element_by_id('LIST_VAR2_4').text


def get_shifts(driver, first_day, last_day):
    """Creates data structure of shifts

    Expicitly waits for JavaScript to generate shift content using the days
    form the payperiod.

    Args:
        driver: driver instance being used
        first_day: first day of the payperiod
        last_day: last day of the payperiod

    Returns:
        shifts: data strucutre containing shifts
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
