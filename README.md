# Apartment Scraper

StreetEasy mantains a list of all past rentals. To find the best off-market
apartment in New York, scrape all past rentals in your desired area. 

## 1. Generate a List of Buildings

`osmQueries` takes in a list of landmarks and a radius and generates a
list of buildings from by querying the OSM overpass API. The script fills in
all addresses between two OSM buildings to ensure completeness. The output
is a JSON file of buildings and their addresses.

## 2. Scrape Buildings for Apartments

`scrapeApartments` takes the JSON file generated by step 1 as input. A
StreetEasy building URL is generated for each each address and retrieved
by a Selenium Webdriver.

The Webdriver uses the following logic in determining how to treat the page

  - if a Captcha is reached, alert the user by speaking a warning. Pause loop. Reload page after user input
  - if there are no past rentals, retrieve next URL
  - if there are past rentals, sanitize rental attributes such as beds, sqft, etc.
    - if rental criteria match user criteria, save apartment in database
    - else continue

## 3. Scrape Apartments for Metadata
`scrapeApartmentMetadata` queries the Apartments from the database. If an
apartment is unscraped, load the apartment page


## The Database
The database has four tables:
1. Apartments
  - data from #2 and #3
2. Buildings
3. Brokers
4. ApartmentsBrokers
  - Join table for the many-to-many relationship of Apartments and Brokers
