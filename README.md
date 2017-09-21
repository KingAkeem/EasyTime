# Automated Logging
This is a script to automate logging hours into a bi-weekly time entry system.The script is basically a web-scraping tool that can scrape one site and input the text into fields on another site. As of right now, it's for personal/co-worker use but I hope to build it to be more robust and usable once it's fully functional. I used Selenium to automate the web browsing and I also created a PhantomJS driver class specifically meant to be able to find/download the latest PhantomJS driver as needed since it's the driver that I'm using to run Selenium headlessly.


## Getting started

To get script onto your local machine, you can run 'git clone https://github.com/KingAkeem/AutoLogging.git'. It will be installed in the current working directory. 

## Prequisites

Before running AutoLogging.py, you must install these packages first. These are the instructions for deb:

pip install selenium scandir requests urllib

## Execution

Whenever you need to execute the script you can either run ./path/to/AutoLogging.py or python /path/to/AutoLogging.py


## Authors
* **Akeem King** - *Initial Work* - [KingAkeem](https://github.com/KingAkeem)

