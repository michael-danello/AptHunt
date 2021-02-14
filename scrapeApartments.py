# web scraping
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
# data cleaning
import pandas as pd
# standard library
from datetime import datetime, timedelta
import time
import json
import re
import sqlite3
from concurrent.futures import ThreadPoolExecutor, wait
import os

def print_row(row_id, address, message, seconds):
    print(f"{str(row_id).ljust(5)} | {address.ljust(20)} | STATUS: {message.ljust(20)} | {str(seconds)} seconds")

def clean_date(last_rented):

    last_rented_date = datetime.strptime(last_rented, "%m/%d/%Y")
    return last_rented_date


def clean_unit(unit):

    return unit

def clean_rent(rent):

    rent = rent.replace(",","")
    rent = rent.replace("$","")
    rent = int(rent)

    return rent

def clean_beds(beds):

    if beds == 'studio':
        return 1

    beds = int(beds[0])

    return beds

def clean_baths(baths):

    baths = clean_beds(baths)

    return baths


def clean_ft(ft):

    if len(ft) == 0:

        return None

    else:
        ft = re.search(r"(\d*)",ft)[0]
        ft = int(ft)
        return ft

def clean_floorplan(floorplan):

    return None

def insert_apartment(conn, **kwargs):

    add_row_query = """
                    INSERT INTO apartments(date,unit,rent,beds,baths,ft,url, buildingID)
                    VALUES(?,?,?,?,?,?,?,?)
                    """

    cur = conn.cursor()

    try:
        cur.execute(add_row_query,list(kwargs.values()))
        conn.commit()

    except sqlite3.IntegrityError:
        pass



def get_building_id(address):
    lookup_building = f"""
    SELECT id from buildings
    WHERE address = '{address}'
    """
    cur = conn.cursor()
    cur.execute(lookup_building)
    id = cur.fetchone()[0]

    return id

def insert_building(**kwargs):

    add_row_query = """
                    INSERT INTO buildings(address,url,scraped)
                    VALUES(?,?,?)
                    """
    cur = conn.cursor()
    cur.execute(add_row_query,list(kwargs.values()))
    conn.commit()

def is_address_scraped(address):

    is_scraped = f"""
    SELECT scraped from buildings
    WHERE address = '{address}'
    """
    cur = conn.cursor()
    cur.execute(is_scraped)
    scraped = cur.fetchone()[0]

    return scraped

def update_scrape_status(address):

    update_scrape_status = f"""
    UPDATE buildings
    SET scraped = True
    WHERE address = '{address}';
    """
    cur = conn.cursor()
    cur.execute(update_scrape_status)
    conn.commit()

def update_apt_buildings(address):
    update_building_status = f"""
    UPDATE buildings
    SET pastRentals = True
    WHERE address = '{address}';
    """
    cur = conn.cursor()
    cur.execute(update_building_status)
    conn.commit()

def has_apartments(address):
    has_apts_query = f"""
    SELECT pastRentals from buildings
    WHERE address = '{address}'
    """
    cur = conn.cursor()
    cur.execute(has_apts_query)
    has_apt = cur.fetchone()[0]

    return has_apt


conn = sqlite3.connect("/Users/mdanello/code/Projects/AptHunt/dbs/Apartments.db")
page_section = "#tab_building_detail=3"

with open("building.json","r") as buildings_file:
    buildings = json.load(buildings_file)

total_scraped = 0
total_to_scrape = len(buildings)
driver = webdriver.Chrome(ChromeDriverManager().install())
for address, building in buildings.items():

    start = time.time()
    if is_address_scraped(address):
        continue

    if not has_apartments(address):
        continue

    building_url = f"{building['url']}{page_section}"
    update_scrape_status(address)
    total_scraped += 1


    if total_scraped > 15000:
        break
    driver.get(building_url)

    # first check if captcha - if so wait for user input and reload page
    try:
        driver.find_element_by_id("px-captcha")
        os.system('say "CAPTCHA reached"')
        input("Captcha Reached - navigate to page to reload")
        driver.get(building_url)

    except NoSuchElementException:
        pass

    # check for past rentals - if none are found, continue to next iteration
    try:
        table = driver.find_element_by_id("past_transactions_table")
        update_apt_buildings(address)
        end = time.time()
        elapsed = round(end-start,2)
        print_row(total_scraped,address,"past rentals",elapsed)

    except NoSuchElementException:
        end = time.time()
        elapsed = round(end-start,2)
        print_row(total_scraped,address,"no past rentals",elapsed)
        time.sleep(0.25)
        continue

    headers = driver.find_elements_by_xpath('//table[@id="past_transactions_table"]/thead/tr/th')
    header_text = [header.text for header in headers]

    rentals = driver.find_elements_by_xpath('//table[@id="past_transactions_table"]/tbody/tr')

    rentalMatches = 0

    for rental in rentals:

        apt = {}

        rental_cols = rental.find_elements_by_css_selector('td')
        cells = [cell.text for cell in rental_cols]

        for idx, col in enumerate(cells):

            type = header_text[idx].lower().replace("²","").strip()

            if col == "" or None:
                apt[type] = None
                continue

            clean_method = f"""clean_{type}('{col}')"""
            clean_data = eval(clean_method)
            apt[type] = clean_data

        if apt['beds'] == None or apt['beds'] < 3:
            continue

        if apt['rent'] > 4500:
            continue

        if apt['date'] == None or apt['date'] < datetime.now() - timedelta(weeks=156):
            continue

        url = rental.find_element_by_css_selector('a').get_attribute("href")
        buildingID = get_building_id(address)

        apt['url'] = url
        apt['buildingID'] = buildingID

        apt.pop('floorplan', None)

        insert_apartment(conn, **apt)
        rentalMatches += 1

    end = time.time()
    elapsed = round(end-start,2)
    if not rentalMatches:
        print_row(total_scraped, address, f"no apts found",elapsed)
    else:
        print_row(total_scraped, address, f"LFGO: {rentalMatches} apts found",elapsed)
    time.sleep(0.25)


driver.close()
