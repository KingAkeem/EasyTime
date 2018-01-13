from .actions import wait_for, submit, get_menu
from datetime import date, datetime


def pay_period(driver):
    """Finds first and lates date of most recent payperiod by ID
    Args:
     driver: driver instance being used

    Returns:
     (first_day, last_day): tuple contiaing the first and last day of the
                            most recent payperiod
    """

    # First and last day of payperiod
    first_day = driver.find_element_by_id('DATE_LIST_VAR1_1').text
    last_day = driver.find_element_by_id('DATE_LIST_VAR2_1').text

    # Making two digit year into four digits eg. 17 -> 2017
    first_day = first_day[0:6] + '20' + first_day[6:8]
    last_day = last_day[0:6] + '20' + last_day[6:8]

    # Formatting start date eg. Y-m-d
    first_day = datetime.strptime(first_day, '%m/%d/%Y').strftime('%Y-%m-%d')
    last_day = datetime.strptime(last_day, '%m/%d/%Y').strftime('%Y-%m-%d')

    return (first_day, last_day)


def write_time(time_in, time_out, curr_date, shifts, index):
    """Writes time to page

    Fills time in and time out cells of timesheet stored in shifts based on
    index

    Args:
        time_in: time clocked into work
        time_out: time clocked out of work
        curr_date: The current date being written to
        shifts: data structure containing shifts (time information)
        index: determines where shift is
    """

    time_in.send_keys(shifts[curr_date][index]['Time-In'])
    time_out.send_keys(shifts[curr_date][index]['Time-Out'])


def get_timesheet(driver):
    emp_menu = get_menu(driver)
    driver.get(emp_menu)
    sub_menu = driver.find_elements_by_class_name('submenu')

    emp_options = {}

    # Creates a dictionary of name and url for menu options
    for item in sub_menu:
        emp_options[item.text] = item.get_attribute('href')
    # Opening page based on user option eg. 'Time Entry'
    driver.get(emp_options['Time Entry'])

    # Finds urls for time entry
    driver.find_element_by_class_name('left').find_elements_by_tag_name('a')

    # Get's all url for time entry options
    menu_options = driver.find_elements_by_tag_name('a')
    options = dict()

    # Stores name and url pairs into dictionary
    for option in menu_options:
        options[option.text] = option.get_attribute('href')

    # Opens page of usr chosen option eg. 'Time entry' page
    driver.get(options['Time entry'])


def fill_timesheet(driver, shifts, last_day):
    """
    Fills timesheet using the first and last date to generate the payperiod
    dates then looping through those dates and inserting times.

    Args:
        driver: driver instance being used
        shifts: data structure containing shifts with time information
    """

    wait_for(driver, 15, 'LIST_VAR1_1')
    # Clicking box to select most recent payperiod
    driver.find_element_by_id('LIST_VAR1_1').click()
    submit(driver)  # Submitting checked box

    processed_dates = []  # Dates that have already been processed

    # Getting list of dates
    dates = driver.find_elements_by_tag_name('p')

    # Loops over dates and sends text to input boxes that match dates
    for dt in dates:
        tag_name = dt.get_attribute('id')
        curr_date = dt.text

        if shifts:
            # If value is a date then split it and join back in a the format of
            # '%Y-%m-%d' and gets the current column number
            if 'DATE' in tag_name:
                month, day, year = curr_date.split('/')
                curr_date = '-'.join(('20' + year, month, day))
                column_no = tag_name.split('_')[-1]

            if 'LIST2' in tag_name and curr_date in shifts:
                time_in = driver.find_element_by_id('LIST_VAR4_' + column_no)
                time_out = driver.find_element_by_id('LIST_VAR5_' + column_no)

                processed = curr_date in processed_dates
                has_two_shifts = len(shifts[curr_date]) == 2

                if processed and has_two_shifts:
                    write_time(time_in, time_out, shifts, curr_date, 1)
                elif curr_date not in processed_dates:
                    write_time(time_in, time_out, shifts, curr_date, 0)

                processed_dates.append(curr_date)  # Caching dates

    # Timesheet will not be finalized if the day is equal to/past the
    # last day on the timesheet or if you press any other key besides y.
    date_currently = str(date.today())
    ans = input('Would you like to finalize your time sheet? (Y/N) ')

    if ans == 'y' or ans == 'Y' and date_currently >= last_day:
        print('Your timesheet has been finalized.')
        # Checks box to finalize timesheet
        driver.find_element_by_id('VAR5').click()
    else:
        print('Your timesheet has not been finalized.')
