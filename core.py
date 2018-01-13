#!/usr/bin/env python3

__author__ = 'Akeem King'

import getpass
import json
import logging as log
from helpers.drivers import ChromeDriver
from helpers.actions import login, submit, get_shifts, get_hours
from helpers.timesheet import fill_timesheet, pay_period, get_timesheet
from selenium import webdriver


def main():

    try:
        webadvisor = 'https://webadvisor.coastal.edu'
        emp_console = 'https://coastal.edu/scs/employee'

        username = input('Username: ')
        password = getpass.getpass()  # Defaults to 'Password: '

        exec_path = ChromeDriver().get_path()
        driver = webdriver.Chrome(exec_path)
        driver.get(webadvisor)  # Opening Webadvisor homepage
        login(driver, username, password)
        get_timesheet(driver)
        first_day, last_day = pay_period(driver)
        driver.get(emp_console)  # Opening Employee Console login
        shifts = get_shifts(driver, first_day, last_day)
        driver.get(webadvisor)
        get_timesheet(driver)
        fill_timesheet(driver, shifts, last_day)
        submit(driver)  # Submits timesheet based on date
        hours = get_hours(driver)
        print("You've worked {hours} hours.".format(hours=hours))
        input('Press any key to end ...')

        # Logs times that were entered into a log sheet in the current working
        # directory named 'easytime.log'
        log.basicConfig(filename='easytime.log', level=log.INFO, filemode='w')
        log.info(json.dumps(shifts, sort_keys=True, indent=4))
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
