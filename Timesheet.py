from robobrowser import RoboBrowser

browser = RoboBrowser(history=True) # Creates an instance of a RoboBrowser object

browser.open("https://www.coastal.edu/scs/employee") # Opens RoboBrowser to Login page
form = browser.find_all()

print(form)

