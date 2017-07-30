from robobrowser import RoboBrowser

browser = RoboBrowser(history=True) # Creates an instance of a RoboBrowser object

browser.open("https://www.coastal.edu/scs/employee") # Opens RoboBrowser to Login page
form = browser.get_form()

username = input("What is your username? ")
password = input("What is your password? ")

form['uname'] = username
form['pnum'] = password

browser.submit_form(form)


