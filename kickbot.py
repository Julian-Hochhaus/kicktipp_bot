"""
The kickbot logs into your kicktipp-account and automatically tips for you based on the betting odds in the kicktipp app.
"""

import robobrowser
from bs4 import BeautifulSoup
import math
import getpass
import sys

url_login= "http://www.kicktipp.de/info/profil/login"

home_divisor=1.5#Increase, to lower expected goals for home team
guest_divisor=1.5#Increase, to lower expected goals for guest team

def get_community_name():
    """Searches for the community names by checking, if content of any a href is equal to its content variable, which is the community name here"""
    for i in browser.find_all("a"):
        link = i.get("href")
        name = i.contents[0]
        if link.replace("/","") == name:
            return name
            break

def set_urls(community_name):
    """Sets bet-URLs"""
    global url
    global url_m
    url = "http://www.kicktipp.de/" + community_name + "/tippabgabe"
    url_m = "http://m.kicktipp.de/" + community_name + "/tippabgabe"

def login():
    "Logs into user account"
    while True:
        print("Please Login with your kicktipp-account:")
        username = input("Email: ")
        password = getpass.getpass(stream=sys.stderr)
        browser.open(url_login)
        form = browser.get_form()
        form['kennung'] = username
        form['passwort'] = password
        browser.submit_form(form)
        if login_failed():
            print("Your email or password was incorrect. Please try again.")
        else:
            break


def login_failed():
    "Returns true if input field for username is still present, which means login was not sucessful"
    for i in browser.find_all(id="kennung"):
        if i.get("name") == "kennung":
            return True
    return False

def grab_odds():
    """Grabs latest odds for each match"""
    odds = []
    browser.open(url)
    browser.find_all("td", class_="kicktipp-wettquote")
    for i in browser.find_all("td", class_="kicktipp-wettquote"):
        quote_str=i.get_text()
        quote = float(quote_str.replace(',', '.'))
        odds.append(quote)
    odds = [odds[i:i+3] for i in range(0, len(odds), 3)]
    return odds


def calc_results(odds):
    """By considering odds, calculates match results"""
    results = []
    for i in odds:
        results.append([int(round(i[2]/home_divisor,0)),int(round(i[0]/guest_divisor,0))])#results are currently calculated by taking the odds and using them to calculate the expected goals
    return results





def get_keys():
    """Get keys of the input form on kicktipp page"""
    formkeys = []
    browser.open(url)

    for i in browser.find_all("input",type="tel"):
        formkeys.append(i.get("name"))
    formkeys = [formkeys[i:i+2] for i in range(0, len(formkeys), 2)]
    return formkeys


def pass_results(results):
    """Submit calculated results and save them to kicktipp"""
    browser.open(url_m)
    formkeys = get_keys()
    form = browser.get_form()
    for i in range(0,len(formkeys)):
        form[formkeys[i][0]] = str(results[i][0])
        form[formkeys[i][1]] = str(results[i][1])
    browser.submit_form(form)




if __name__ == '__main__':
    browser = robobrowser.RoboBrowser(parser="html.parser")
    login()
    set_urls(get_community_name())
    my_odds = grab_odds()
    my_results = calc_results(my_odds)
    pass_results(my_results)
    print("Done!")
