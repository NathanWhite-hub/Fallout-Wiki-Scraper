import csv
from os import close
from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    
    # Open new page
    page = context.new_page()

    # Navigate to the characters page
    page.goto("https://fallout-archive.fandom.com/wiki/Fallout:_New_Vegas_locations")

    page.wait_for_selector('.va-columns')
    hrefs = page.query_selector_all(".va-columns >> a")

    # Create CSV file to write raw data to
    with open('C:\\Users\\zenti\\Desktop\\Programs\\location_hrefs_raw.csv', 'a', newline='\n') as raw_file:
        csv_writer = csv.writer(raw_file)
        
        # For each element in the elements, get the href attribute and add it to the end of the base link.
        for href in hrefs:
            wiki_link = "https://fallout-archive.fandom.com" + href.get_attribute("href")
            csv_writer.writerow([wiki_link])
    # Close the raw file
    raw_file.close()

    # ---------------------
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)