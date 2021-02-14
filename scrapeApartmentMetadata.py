# web scraping
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
# standard library
import sqlite3
import re
import time

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect("/Users/mdanello/code/Projects/AptHunt/dbs/Apartments.db")
conn.row_factory = dict_factory
cur = conn.cursor()

def find_number(str):
    num = re.search("\d+",str)
    if not num:
        return None

    return num[0]

def get_broker(brokerURL):

    get_broker_query = """
    select id
    from brokers
    where url = ?
    """
    cur.execute(get_broker_query, [brokerURL])
    id = cur.fetchone()

    return id


def insert_broker(brokerURL):

    brokerID = get_broker(brokerURL)

    if brokerID:
        brokerID = brokerID.get('id')
        return brokerID

    insert_broker_query = """
    INSERT INTO brokers(url)
    VALUES(?)
    """.format(brokerURL)
    cur.execute(insert_broker_query, [brokerURL])
    conn.commit()
    brokerID = cur.lastrowid

    return brokerID

def add_join_row(brokerID, aptID):

    insert_join_query = f"""
    INSERT INTO apartments_brokers(apartmentID, brokerID)
    VALUES(?,?)
    """
    cur.execute(insert_join_query, (aptID,brokerID))
    conn.commit()

def insert_apt_metadata(days_on_market, saves, apt_id):

    insert_apt_metadata_query = """
    UPDATE apartments
    SET daysOnMarket = ?,
    saves = ?,
    scraped = 1
    WHERE ID = ?
    """.format(days_on_market, saves, apt_id)
    cur.execute(insert_apt_metadata_query, (days_on_market,saves,apt_id))
    conn.commit()

def insert_description(apt_id, description):

    insert_description = """
    UPDATE apartments
    SET description = ?,
    scraped = 1
    WHERE ID = ?
    """
    cur.execute(insert_description, (description,apt_id))
    conn.commit()

def scrape_description(driver):

    try:
        driver.find_element_by_id("px-captcha")
        os.system('say "CAPTCHA reached"')
        input("Captcha Reached - navigate to page to reload")
        # rescrape if captcha reached
        scrape_description(driver, url)

    except NoSuchElementException:

        try:
            description = driver.find_element_by_xpath("//div[@class = 'Description-block jsDescriptionExpanded']/p")

            return description.text

        except NoSuchElementException:

            return None



def scrape_apartments():

    driver = webdriver.Chrome(ChromeDriverManager().install())

    cur.execute('SELECT url, id, scraped  from apartments')
    apts = cur.fetchall()

    for apt in apts:

        cur.execute('SELECT scraped from apartments where id = ?',[apt['id']])
        scraped = cur.fetchone().get('scraped')

        if scraped:
            continue
        else:
            start = time.time()
            cur.execute('UPDATE apartments SET scraped = 1 where id = ?',[apt['id']])
            conn.commit()
            driver.get(apt['url'])

        try:
            driver.find_element_by_id("px-captcha")
            input("Captcha Reached - navigate to page to reload")
            driver.get(apt['url'])

        except NoSuchElementException:
            pass

        try:
            saves = driver.find_element_by_xpath("//div[@class='popularity']").text
            saves = find_number(saves)


        except NoSuchElementException:
            saves = None

        try:
            vitals_array = driver.find_elements_by_xpath("//div[@class='Vitals']//div[@class='Vitals-data']")
            if not vitals_array:
                time.sleep(0.5)
                continue
            days_on_market = vitals_array[1].text

            if days_on_market == 'N/A':
                days_on_market = None

            else:
                days_on_market = find_number(days_on_market)

        except NoSuchElementException:
            days_on_market = None

        try:
            brokerURLs = driver.find_elements_by_xpath("//span[starts-with(@class, 'Listing')]/a")
            # broker urls are scarped twice
            brokerURLs = [broker.get_attribute("href") for broker in brokerURLs]
            for broker in brokerURLs:

                brokerID  = insert_broker(broker)
                add_join_row(brokerID, apt['id'])

        except NoSuchElementException:
            brokerURLs = None

        insert_apt_metadata(days_on_market, saves, apt['id'])

        description = scrape_description(driver)

        if description:
            insert_description(apt['id'], description)

        end = time.time()
        elapsed = round(end - start,2)
        print(f"""APT: {str(apt['id']).ljust(5," ")} saves: {str(saves).ljust(5, " ")} days on market: {str(days_on_market).ljust(5, " ")}  brokers: {str(len(brokerURLs)).ljust(5, " ")}  TIME: {elapsed}s""")

        time.sleep(0.5)

    driver.close()

if __name__ == "__main__":
    scrape_apartments()
