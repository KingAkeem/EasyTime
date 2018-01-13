import getpass

from selenium.webdriver.support.expected_conditions import (
                            visibility_of_element_located as is_visible)
from selenium.webdriver.support.wait import WebDriverWait
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
