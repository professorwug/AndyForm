""" Hi there! These are the things you HAVE to change -  - - - -- - - - - - -  - -  - - - - -  -  -- - - -- - - - - - - - -  --"""
# credentials for VAN.
myname = 'username'
mykey = 'password'
# which website do you go to to login to VAN?
loginPage = "http://van_login.your_organization.org"
# the location of the 'AndyForm Generation' folder on your computer
andyPath = "/Users/adjourner/Desktop/AndyForm Generation/"
# should we ask before adding new people? "True" means we will ask; "False" means we won't.
# (Make sure they are capitalized)
askBeforeBirthing = True
# should AndyForm use the speech synthesizer to say things like "Add a new person?" We recommend you set this to True; it lets you wander away from your computer while data is being processed.
# But if you find it annoying, change it to False, and we'll just make a "beep" sound instead.
andyCanTalk = True
""" -- - - - - - - - - - - - - -- - - - - - - - - - -  - --  - - - - - - -  -  - - - - - - - -- - - - -- - - - - """
# And let the program begin!
# Selenium imports
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.command import Command

#for browser monitoring
import http.client
import socket

# administrative things
import sys
import logging
import logging.handlers
import unicodedata
import time
import csv
import re
import os
import datetime
from difflib import SequenceMatcher
import webbrowser
import usaddress  # address parser
import tkinter  # messagebox creater
from tkinter import messagebox

logPath = andyPath + "/Script/AndyNotes.log"


def ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()


# survey names - these are samples, which are later overwritten.
actionName = '2019 Action: Petition Signature'
actionType = 'Walk'
surveyName = 'MT: CleanEnergy4All'

now = datetime.datetime.now()
year = now.year
print(year)
reportCard = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html>
    <head>
    <meta content="text/html; charset=ISO-8859-1"
    http-equiv="content-type">
    <style type="text/css">
    body{
    background: dark-grey;
    }
    tr.success td{
    width: 100vw;
    height: 10vh
    border: 2px grey;
    margin: 5px;
    background: green;
    }
    tr.failure td{
    width: 100vw;
    height: 10vh
    border: 2px grey;
    margin: 5px;
    background: red;
    }
    tr.true td {
    width: 100vw;
    height: 20vh
    border: 2px grey;
    margin: 5px;
    background: green;
    font-size: 4vh;
    }
    tr.false td {
    width: 100vw;
    height: 20vh
    border: 2px grey;
    margin: 5px;
    background: #CC9999;
    font-size: 4vh;
    }
    </style>
    <title>AndyForm Report</title>
    </head>
    <body>
    <h1> AndyForm Report on RIGHTNOW</h1>
    <h2> SUCCESSFULPEOPLE people were successfully entered, but MISSINGPEOPLE could not be located. </h2>
    <table style="width:100%">
    <tr>
    <th> Report </th>
    <th>Name</th>
    <th>Phone</th>
    <th>Address </th>
    <th> Email </th>
    <th> Notes </th>
    </tr>
    '''
handler = logging.handlers.WatchedFileHandler(
                                              os.environ.get("LOGFILE", logPath))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)


def strToFile(text, filename):
    """Write a file with the given name and the given text."""
    output = open(filename, "w")
    output.write(text)
    output.close()


def browseLocal(webpageText, filename=andyPath + 'Results/report' + str(now.ctime()) + '.html'):
    """Start your webbrowser on a local file containing the text
        with given filename."""
    strToFile(webpageText, filename)
    time.sleep(2)
    filename = filename.replace(" ", "%20")
    logging.info("The file name is " + filename)
    # webbrowser.open("file://" + filename)
    webdriver.ActionChains(driver).key_down(Keys.CONTROL).send_keys('t').key_up(Keys.CONTROL).perform()
    driver.get("file://" + filename)


driver = webdriver.Chrome(ChromeDriverManager().install())
# chrome_options = Options()
# chrome_options.add_experimental_option("detach", True)


def get_status(driver):
    try:
        driver.execute(Command.STATUS)
        return True
    except (socket.error, http.client.CannotSendRequest):
        return False


def missoulizer(string):
    """Replaces common substitutions."""
    string = string.lower()
    string = string.replace('msla', 'missoula')
    string = string.replace(' e ', " east ")
    string = string.replace(' s ', " south ")
    string = string.replace(' n ', ' north ')
    string = string.replace(' w ', ' west ')
    # string = string.replace()
    
    return string


def csvDaemon(filePath):
    global reportCard
    with open(filePath,encoding="utf-8") as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        results = []
        for row in readCSV:
            if row[0].strip() != '' and row[0] != 'Name':
                logging.info(unicodedata.normalize('NFKD',row).encode("ascii","replace"))
                name = row[0].replace('\n', ' ')
                name = name.strip()
                name = name.split(' ')
                number = ''.join(re.findall('\d+', row[1]))
                if len(name) == 3:
                    name = [name[0], name[2], name[1]]
                if 0 < len(number) < 10:  # Arbitrary: add montana area code to unspecified numbers.
                    number = "406" + number
                address = missoulizer(row[2].replace('\n', ' '))
                address = address.strip()
                niceAddress = addressing(address)
                # if "city" not in niceAddress[0]:
                #     address += "Missoula"
                # if "state" not in niceAddress[0]:
                #     address += "MT"
                
                email = row[3].replace(' ', '').replace('\n', '')
                noteThis = row[4].strip()
                logging.info(str(name) + " " + number + " " + address + " " + email)
                try:
                    success = whereisBob(name, number, address, email, noteThis, False)
                except Exception:
                    logging.exception("Whoops! Something went wrong.")
                    success = [False, "Mysterious error! Whoops."]
                if not success[0] and success[1] != "POSSIBLE DUPLICATE: Two results were SUSPICIOUSLY similar! We couldn't tell the difference.":
                    try:
                        success = whereisBob(name, number, address, email, noteThis, True)
                    except Exception:
                        logging.exception("Whoops! Something went wrong.")
                        success = [False, "Mysterious error! Whoops."]
            # we'll try it a second time, just in case something timed out
            results.append([success[0], name, number, address, email, noteThis, success[1]])
# and now run some statistics
results.sort()  # brings the missing ones to the front.
    falseCount = 0
        for i in results:
            reportCard += '''<tr class = "classcode"><td> TrueValue </td><td>Dan Speed</td><td>banana phone</td> <td>The Suburban Hotel</td><td> speedaway@dan.org </td><td> NOTES GO HERE </td></tr>'''.replace(
                                                                                                                                                                                                                 "TrueValue", str(i[-1])).replace("Dan Speed", ' '.join(i[1])).replace('banana phone', i[2]).replace(
                                                                                                                                                                                                                                                                                                                     "The Suburban Hotel", i[3]).replace("speedaway@dan.org", i[4]).replace("classcode",
                                                                                                                                                                                                                                                                                                                                                                                            str(i[0]).lower()).replace(
                                                                                                                                                                                                                                                                                                                                                                                                                       "NOTES GO HERE", i[5])
                                                                                                                                                                                                                                                                                                                                                                                                                       if not i[0]:
                                                                                                                                                                                                                                                                                                                                                                                                                           falseCount += 1
        reportCard = reportCard.replace("RIGHTNOW", str(now.ctime())).replace("SUCCESSFULPEOPLE",
                                                                              str(len(results) - falseCount)).replace(
                                                                                                                      "MISSINGPEOPLE", str(falseCount))
                                                                                                                      reportCard += "</table></body></html>"
                                                                                                                      browseLocal(reportCard)


def login():
    """Initializes with QuickMark"""
    # find the element that's name attribute is q (the google search box)
    usernameBox = driver.find_element_by_id("TextBoxUserName")
    usernameBox.send_keys(myname)
    passwordBox = driver.find_element_by_id("TextBoxPassword")
    passwordBox.send_keys(mykey)
    # submit the form (although google automatically searches now without submitting)
    passwordBox.submit()
    WebDriverWait(driver, 10).until(EC.title_contains("Main Menu"))
    
    # And navigate into Quick Mark
    quickMark = driver.find_element_by_link_text("Quick Mark")
    quickMark.click()
    logging.info(unicodedata.normalize('NFKD',driver.title).encode("ascii","replace"))
    
    WebDriverWait(driver, 10).until(EC.title_contains("Quick Mark"))


logging.info(sys.argv)


def doesItMatch(name, number, address, email, currName, currAddress, currCity, currState, currPhone, currEmail):
    """contained function to assign score to different names based on specified criteria.
        Is the last name correct? Is either city, state, address, or number currect?  Is it within a "similarity threshold"?
        Each of these factors earns"""
    score = 0
    logging.info("the curr: " + unicodedata.normalize('NFKD',currName).encode("ascii","replace") + "the real: " + unicodedata.normalize('NFKD',name).encode("ascii","replace"))
    
    # Please be advised: These numbers are kind of random.
    if currName[0] == name[1]:
        score += 10
        logging.info("last name match")
    else:
        score += 5 * ratio(currName[0], name[1])
    score += 5 * ratio(currName[1], name[0])
    
    if number in currPhone:
        score += 10
    else:
        score += 8 * ratio(number, currPhone)
    
    if currCity in address:
        score += 10
    if currState in address:
        score += 10
    
    if ratio(address, currAddress) > 0.5:
        logging.info("address match")
        score += 10
    
    if ratio(currEmail, email) > 0.8:
        score += 8
    return score


def initialize():
    driver.get(loginPage)
    if driver.title != "League of Conservation Voters - Main Menu":
        login()  # which logs in (duh)
    if driver.title == "League of Conservation Voters - Main Menu":
        # And navigate into Quick Mark
        quickMark = driver.find_element_by_link_text("Quick Mark")
        quickMark.click()
        logging.info(unicodedata.normalize('NFKD',driver.title).encode("ascii","replace"))
        
        WebDriverWait(driver, 10).until(EC.title_contains("Quick Mark"))

survey = driver.find_element_by_id(
                                   "ctl00_ContentPlaceHolderVANPage_WizardControl_VANDetailsItemQuickMarkType_VANInputItemDetailsItemQuickMarkType_QuickMarkType_0")
    survey.click()
    through = driver.find_element_by_id(
                                        "ctl00_ContentPlaceHolderVANPage_WizardControl_StartNavigationTemplateContainerID_ButtonStartNext")
                                        through.click()
                                        
                                        time.sleep(1)
                                        
                                        select = Select(driver.find_element_by_id(
                                                                                  'ctl00_ContentPlaceHolderVANPage_WizardControl_VANDetailsItemAddSurveyQuestion_VANInputItemDetailsItemAddSurveyQuestion_AddSurveyQuestion'))
                                        
                                        # select by visible text
                                        select.select_by_visible_text(actionName)
                                        
                                        select2 = Select(driver.find_element_by_id(
                                                                                   'ctl00_ContentPlaceHolderVANPage_WizardControl_VANDetailsItemContactType_VANInputItemDetailsItemContactType_ContactType'))
                                        
                                        # select by visible text
                                        select2.select_by_visible_text(actionType)
                                        
                                        finish = driver.find_element_by_id(
                                                                           "ctl00_ContentPlaceHolderVANPage_WizardControl_FinishNavigationTemplateContainerID_ButtonFinishNext")
                                        
                                        webdriver.ActionChains(driver).move_to_element(finish).click(finish).perform()
                                        time.sleep(1)


def whereisBob(name, number, address, email, noteThis, nationalLook):
    # go to the Van main page
    time.sleep(2)
    logging.info(driver.title)
    if driver.title != "League of Conservation Voters - Quick Mark":
        logging.info("We have driver title: " + driver.title)
        logging.debug("Initializing ; )")
        initialize()  # loads the quick mark page, if not loaded

    logging.info(unicodedata.normalize('NFKD',driver.title).encode("ascii","replace"))

# enable (or disable) search of all people
if nationalLook:
    allPeople = driver.find_element_by_id("ctl00_ContentPlaceHolderVANPage_ctl00_RadioButtonMyActivist_0")
    webdriver.ActionChains(driver).move_to_element(allPeople).click(allPeople).perform()
    else:
        allPeople = driver.find_element_by_id("ctl00_ContentPlaceHolderVANPage_ctl00_RadioButtonMyActivist_1")
        webdriver.ActionChains(driver).move_to_element(allPeople).click(allPeople).perform()

    lastName = driver.find_element_by_id("ctl00_ContentPlaceHolderVANPage_ctl00_TextBoxFilterLastName")
    lastName.clear()
    lastName.send_keys(name[1])
    firstName = driver.find_element_by_id("ctl00_ContentPlaceHolderVANPage_ctl00_TextBoxFilterFirstName")
    firstName.clear()
    firstName.send_keys(name[0])

search = driver.find_element_by_id("ctl00_ContentPlaceHolderVANPage_ctl00_RefreshFilterButton")
webdriver.ActionChains(driver).move_to_element(search).click(search).perform()
time.sleep(2)

table = driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_gvList')
tbody = table.find_elements_by_tag_name('tbody')[0]
rows = tbody.find_elements_by_tag_name('tr')
logging.info(unicodedata.normalize('NFKD',str(rows)).encode("ascii","replace"))
if (len(rows) == 0 or len(rows[0].find_elements_by_tag_name('td')) < 2):  # the latter case is for the one row that says "person not found"
    logging.info("No one found.")
    if nationalLook:
        returnVal = personMaker(name, number, address, email, noteThis)
        else:
            returnVal = [False,'Try again, with nationalLook enabled.']
    return returnVal
auspiciousPersons = []

for row in rows:
    # Get the columns (all the column 2)
    currName = row.find_elements_by_tag_name('td')[1].text  # note: index start from 0, 1 is col 2
    currName = currName.replace(',', '').split(' ')
    currAddress = row.find_elements_by_tag_name('td')[2].text
    currCity = row.find_elements_by_tag_name('td')[3].text
    currState = row.find_elements_by_tag_name('td')[4].text
    currPhone = row.find_elements_by_tag_name('td')[6].text
    currPhone = ''.join(re.findall('\d+', currPhone))
    currEmail = row.find_elements_by_tag_name('td')[7].text
    logging.info(unicodedata.normalize('NFKD',currName).encode("ascii","replace") + " " + unicodedata.normalize('NFKD',currAddress).encode("ascii","replace") + " " + unicodedata.normalize('NFKD',currCity).encode("ascii","replace") + " " + unicodedata.normalize('NFKD',currState).encode("ascii","replace") + " " + unicodedata.normalize('NFKD',currPhone).encode("ascii","replace") + " " + unicodedata.normalize('NFKD',currEmail).encode("ascii","replace"))  # prints text from the element
                      needsPhone = False
                          needsEmail = False
                              score = doesItMatch(name, number, address, email, currName, currAddress, currCity, currState, currPhone,
                                                  currEmail)
                                                      if ratio(currEmail, email) < 0.7 and email:
                                                          needsEmail = True
                                                              if ratio(currPhone, number) < 0.7 and number:
                                                                  needsPhone = True
                                                                      auspiciousPersons.append([score, rows.index(row), currName, needsPhone, needsEmail])
                                                                      logging.info("we have a score of " + " " + str(score))
                                                                  logging.info(unicodedata.normalize('NFKD',str(auspiciousPersons)).encode("ascii","replace"))
auspiciousPersons.sort()
bestCandidate = auspiciousPersons[-1]
try:
    if bestCandidate[0] < 10:
        logging.info("No one scored highly enough.")
        return [False, "No one scored highly enough."]
        if bestCandidate[0] - auspiciousPersons[-2][0] < 5:  # There's a chance that there's only one matching person,
            logging.info("Too similar! Possible duplicate...")
            return [False,
                    "POSSIBLE DUPLICATE: Two results were SUSPICIOUSLY similar! We couldn't tell the difference."]
    except:
        if bestCandidate[0] < 10:  # possibly of dubious similarity
            logging.info("No one scored really high.")
            return [False, "No one scored highly enough"]
# Select response
yesDial = Select(rows[bestCandidate[1]].find_elements_by_tag_name('select')[0])
yesDial.select_by_visible_text(surveyName)

search = driver.find_element_by_id("ctl00_ContentPlaceHolderVANPage_ctl00_RefreshFilterButton")
# search.click() #and save the results with another click of the search button
webdriver.ActionChains(driver).move_to_element(search).click(search).perform()
    
    time.sleep(2)
    notes = "Success! "
    if bestCandidate[3] or bestCandidate[3] or noteThis:
        logging.info("needs info")
        table = driver.find_element_by_id(
                                          'ctl00_ContentPlaceHolderVANPage_gvList')  # apparently this must be refreshed...
                                          tbody = table.find_elements_by_tag_name('tbody')[0]
                                          rows = tbody.find_elements_by_tag_name('tr')
                                          infoAdder(bestCandidate[4], bestCandidate[3], rows[bestCandidate[1]].find_elements_by_tag_name('a')[0], email, number, bestCandidate[2], noteThis)
                                          notes += "We added"
                                          if bestCandidate[2]:
                                              notes += " a shiny new Phone Number..."
                                          if bestCandidate[3]:
                                              notes += " an email address..."
                                              if noteThis:
                                                  notes += " some notes..."

logging.info("Bob has been found! Yay!")
return [True, notes]
# surveyButton = driver.find_element_by_id("ctl00_ContentPlaceHolderVANPage_ctl38_UpdatePanel_SurveyQuestions_EID295C3E9B_ExpandButton")
# surveyButton.click()


def addNotes(link, notes, name):
    webdriver.ActionChains(driver).move_to_element(link).click(link).perform()
    logging.info("We're adding notes! Waiting...")
    WebDriverWait(driver, 10).until(EC.title_contains(name))
    wideRow = driver.find_elements_by_class_name('panel-heading')
    logging.info("And here are the wide rows:" + " " + unicodedata.normalize('NFKD',str(wideRow)).encode("ascii","replace"))
    primaryButton = driver.find_elements_by_partial_link_text('Save All')[0]
    addedTally = 0
    for i in range(len(wideRow)):
        opts = driver.find_elements_by_class_name('panel-heading')[i]
        logging.info(" The opts text is " + " " + unicodedata.normalize('NFKD',opts.text).encode("ascii","replace")))
        if "Notes" in opts.text:
            logging.info("found the notes button")
            emailButton = opts.find_elements_by_tag_name("input")[0]
            webdriver.ActionChains(driver).move_to_element(emailButton).click(emailButton).perform()
            time.sleep(1)
            optsHolder = opts.find_element_by_xpath('..')
            noteBox = optsHolder.find_elements_by_tag_name("textarea")
            webdriver.ActionChains(driver).move_to_element(noteBox).click(noteBox).send_keys(
                                                                                        notes).perform()
            return "Success!"


def infoAdder(needsEmail, needsPhone, link, email, number, name, noteThis):
    webdriver.ActionChains(driver).move_to_element(link).click(link).perform()
    logging.info('waiting...')
    WebDriverWait(driver, 10).until(EC.title_contains(name[0]))
    wideRow = driver.find_elements_by_class_name('panel-heading')
    logging.info("And here are the wide rows:" + " " + str(wideRow))
    primaryButton = driver.find_elements_by_partial_link_text('Save All')[0]
    addedTally = 0
    for i in range(len(wideRow)):
        opts = driver.find_elements_by_class_name('panel-heading')[i]
        logging.info(" The opts text is " + unicodedata.normalize('NFKD',str(opts.text)).encode("ascii","replace"))
        if not needsEmail and not needsPhone and not noteThis:
            logging.info("Finished! trying to go back")
            webdriver.ActionChains(driver).move_to_element(primaryButton).click(primaryButton).perform()
            try:
                alert_obj = driver.switch_to.alert  # is it an actual alert?
                alert_obj.accept()  # press the enter key to escape the alert box that should come up.
            except Exception:
                logging.info("Whoops. There was no alert.")
            # qMark = driver.find_elements_by_partial_link_text('Quick Mark')
            # for f in qMark:
            #    if f.get_attribute("class")=="BreadCrumbs":
            #        f.click()
            driver.get("https://members.lcv.org/QuickLookup.aspx?ReturnToList=1")  # it's the cheap way out
            WebDriverWait(driver, 10).until(EC.title_contains("Quick Mark"))
            logging.info('infoAdd out!')
            return True
        if noteThis:
            if "Notes" in opts.text:
                print("located the notes")
                logging.info("found the notes button")
                emailButton = opts.find_elements_by_tag_name("input")[0]
                webdriver.ActionChains(driver).move_to_element(emailButton).click(emailButton).perform()
                time.sleep(1)
                optsHolder = opts.find_element_by_xpath('..')
                noteBox = optsHolder.find_element_by_tag_name("textarea")
                webdriver.ActionChains(driver).move_to_element(noteBox).click(noteBox).send_keys(
                                                                                                 noteThis).perform()
                                                                                                 saver = optsHolder.find_element_by_partial_link_text('Save')
                                                                                                 webdriver.ActionChains(driver).move_to_element(saver).click(saver).perform()
                                                                                                 print("successfully added notes")
                                                                                                 noteThis = False

        if needsEmail:
            if "Email" in opts.text:
                logging.info('email drop down found')
                emailButton = opts.find_elements_by_tag_name("input")[0]
                webdriver.ActionChains(driver).move_to_element(emailButton).click(emailButton).perform()
                time.sleep(1)
                possibleInputs = driver.find_elements_by_tag_name("td")
                for a in possibleInputs:
                    logging.info('searching through the tables. Current class: ' + " " + a.get_attribute("class"))
                    if len(a.find_elements_by_tag_name("input")):
                        if a.find_elements_by_tag_name("input")[0].get_attribute("class") == "input-element":
                            logging.info('Found it!')
                            emailBox = a.find_elements_by_tag_name("input")[0]
                            webdriver.ActionChains(driver).move_to_element(emailBox).click(emailBox).send_keys(
                                                                                                               email).perform()
                                                                                                               saver = driver.find_elements_by_partial_link_text('Save New')[addedTally]
                                                                                                               addedTally += 1
                                                                                                               webdriver.ActionChains(driver).move_to_element(saver).click(saver).perform()
                                                                                                               # alert_obj = driver.switch_to.alert  # is it an actual alert?
                                                                                                               # alert_obj.accept()
                            needsEmail = False
        if needsPhone:
            if "Phones" in opts.text:
                logging.info("trying to add number...")
                phoneButton = opts.find_elements_by_tag_name("input")[0]
                phoneButton.click()
                time.sleep(1)
                possibleInputs = driver.find_elements_by_tag_name("td")
                for b in possibleInputs:
                    logging.info('searching through the tables. Current class: ' + " " + str(len(
                                                                                                 b.find_elements_by_tag_name("input"))))
                                                                                                 if len(b.find_elements_by_tag_name("input")) >= 3:
                                                                                                     logging.info('Found it!')
                                                                                                     eForm = b.find_elements_by_tag_name("input")[
                                                                                                                                                  0]  # I believe it's the first input element (as the first, I think, was the pop down box)
                                                                                                         webdriver.ActionChains(driver).move_to_element(eForm).click(eForm).send_keys(
                                                                                                                                                                                      number).perform()
                                                                                                                                                                                      saveNew = driver.find_elements_by_partial_link_text("Save New")[addedTally]
                                                                                                                                                                                          addedTally += 1
                                                                                                                                                                                              webdriver.ActionChains(driver).move_to_element(saveNew).click(saveNew).perform()
                                                                                                                                                                                              needsPhone = False
            
                '''
                    wideRow2 = driver.find_elements_by_class_name('panel-heading')
                    for opts2 in wideRow2:
                    logging.info(opts2.text)
                    if "Email" in opts2.text:
                    eForm = opts2.find_elements_by_class_name("input-element")[0]
                    eForm.send_keys(email)
                    primaryButton = driver.find_elements_by_partial_link_text('Save All')[0]
                    primaryButton.click()
                    alert_obj = driver.switch_to.alert  # is it an actual alert?
                    alert_obj.send_keys(uue007')  # press the enter key to escape the alert box that should come up.
                    needsEmail = False'''
                        logging.info("loop finished! Heading home!")
                        primaryButton.click()
                        alert_obj = driver.switch_to.alert  # is it an actual alert?
                            alert_obj.accept()  # press the enter key to escape the alert box that should come up.
                            driver.get("https://members.lcv.org/QuickLookup.aspx?ReturnToList=1")  # it's the cheap way out
                            WebDriverWait(driver, 10).until(EC.title_contains("Quick Mark"))
                            logging.info('infoAdd out!')
                            return True


def addressing(address):
    try:
        address = usaddress.tag(address, tag_mapping={
                                'Recipient': 'recipient',
                                'AddressNumber': 'address1',
                                'AddressNumberPrefix': 'address1',
                                'AddressNumberSuffix': 'address1',
                                'StreetName': 'address1',
                                'StreetNamePreDirectional': 'address1',
                                'StreetNamePreModifier': 'address1',
                                'StreetNamePreType': 'address1',
                                'StreetNamePostDirectional': 'address1',
                                'StreetNamePostModifier': 'address1',
                                'StreetNamePostType': 'address1',
                                'CornerOf': 'address1',
                                'IntersectionSeparator': 'address1',
                                'LandmarkName': 'address1',
                                'USPSBoxGroupID': 'address1',
                                'USPSBoxGroupType': 'address1',
                                'USPSBoxID': 'address1',
                                'USPSBoxType': 'address1',
                                'BuildingName': 'address2',
                                'OccupancyType': 'address2',
                                'OccupancyIdentifier': 'address2',
                                'SubaddressIdentifier': 'address2',
                                'SubaddressType': 'address2',
                                'PlaceName': 'city',
                                'StateName': 'state',
                                'ZipCode': 'zip_code',
                                })
        return address
    except Exception:
        return [{"address1",address}]


root = tkinter.Tk()
root.withdraw()


def personMaker(name, number, address, email, noteThis):
    """ Makes new people (in VAN) with given information. If askBeforeBirthing is set to True,
        it generates a dialogue box asking for user confirmation."""
    if askBeforeBirthing:
        if andyCanTalk:
            os.system("say 'add a new person?'")
        else:
            os.system("tput bel")
        userConfirmation = messagebox.askokcancel("Add New Person?", name[0] + " " + name[
                                                                                          1] + " was not found. Shall we make a new person? Known data: " + str(number) + " " + address + " " + email,
                                                  icon='warning')
                                                  print(userConfirmation)
                                                  root.update()
                                                      if not userConfirmation:
                                                          return [False, 'No one found. You chose to enter this one manually.']
                                                      print("person maker actived!")
                                                      parsedAddress = addressing(address)
print(parsedAddress)
newPerson = driver.find_elements_by_partial_link_text('Add New Person')[0]
webdriver.ActionChains(driver).move_to_element(newPerson).click(newPerson).perform()
WebDriverWait(driver, 10).until(EC.title_contains("New Person"))
if "address1" in parsedAddress[0]:
    street = driver.find_element_by_id(
                                       "ctl00_ContentPlaceHolderVANPage_VanInputItem639_VanInputItem639AddressLine1")
        street.clear()
        street.send_keys(parsedAddress[0]["address1"])
                                       elif "address2" in parsedAddress[0]:
        street = driver.find_element_by_id(
                                           "ctl00_ContentPlaceHolderVANPage_VanInputItem639_VanInputItem639AddressLine1")
                                           street.clear()
                                           street.send_keys(parsedAddress[0]["address2"])
                                           if "city" in parsedAddress[0]:
                                               city = driver.find_element_by_id("ctl00_ContentPlaceHolderVANPage_VanInputItem639_VanInputItem639City")
                                               city.clear()
                                               city.send_keys(parsedAddress[0]["city"])
                                           if "state" in parsedAddress[0]:
                                               state = driver.find_element_by_id("ctl00_ContentPlaceHolderVANPage_VanInputItem639_VanInputItem639State")
                                               state.clear()
                                               state.send_keys(parsedAddress[0]["state"])
if "zip_code" in parsedAddress[0]:
    zip = driver.find_element_by_id("ctl00_ContentPlaceHolderVANPage_VanInputItem639_VanInputItem639Zip5")
    zip.clear()
    if len(parsedAddress[0]["zip_code"]) == 5:
        zip.send_keys(parsedAddress[0]["zip_code"])
    if len(number) == 10:
        # phoneBox = driver.find_elements_by_id("ctl00_ContentPlaceHolderVANPage_VanInputItem642_VanInputItem642_phone_VanInputItem642_phone_VanInputItem642Input")[0]
        # new way
        theLabel = driver.find_element_by_xpath("//label[contains(text(),'Home Phone')]")
        theParent = theLabel.find_element_by_xpath('..')
        phoneBox = theParent.find_element_by_tag_name("input")
        webdriver.ActionChains(driver).move_to_element(phoneBox).click(phoneBox).send_keys(number).perform()
    if email != "":
        theLabel = driver.find_element_by_xpath("//label[contains(text(),'Email')]")
        theParent = theLabel.find_element_by_xpath('..')
        currentBox = theParent.find_element_by_tag_name("input")
        webdriver.ActionChains(driver).move_to_element(currentBox).click(currentBox).send_keys(email).perform()
    try:
        saveIt = driver.find_element_by_id("ctl00_ContentPlaceHolderVANPage_ButtonNext")
        webdriver.ActionChains(driver).move_to_element(saveIt).click(saveIt).perform()
    except Exception:
        nextButton = driver.find_element_by_id("ctl00_ContentPlaceHolderVANPage_ctl00_RefreshFilterButton")
        webdriver.ActionChains(driver).move_to_element(nextButton).click(nextButton).perform()
whereisBob(name, number, address, email, noteThis, False)
return [True, "Added to VAN as a brand NEW PERSON!"]


theySay = sys.argv
logging.info(surveyName == theySay[1])
surveyName = theySay[1].strip()
csvPath = theySay[2].replace(':', '/').replace("Macintosh HD", '')
if 'Social Media' in surveyName:
    actionName = "2019 Action: Social Media"
    actionType = "Social Media"
    if "Facebook" in surveyName:
        surveyName = "Facebook"
    if "Twitter" in surveyName:
        surveyName = "Twitter"
    if "Instagram" in surveyName:
        surveyName = "Instagram"
csvDaemon(csvPath)
# TODO Find a better way to keep this open.
while get_status(driver):
    time.sleep(30)
    pass
