import csv
from os import close
from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    
    # Open new page
    page = context.new_page()

    # Navigate to the characters page
    page.goto("https://fallout-archive.fandom.com/wiki/Fallout:_New_Vegas_characters")

    page.wait_for_selector('table.va-table')
    hrefs = page.query_selector_all("table.va-table >> tbody >> tr >> td:nth-child(1) >> a")

    # Create CSV file to write raw data to
    with open('\\Programs\\character_hrefs_raw.csv', 'a', newline='\n') as raw_file:
        csv_writer = csv.writer(raw_file)
        
        # For each element in the elements, get the href attribute and add it to the end of the base link.
        for href in hrefs:
            wiki_link = "https://fallout-archive.fandom.com" + href.get_attribute("href")

            # If the link contains the courier player page, don't write that line and move on.
            if "/wiki/Courier" in wiki_link:
                pass
            else:
                # Write the link to the wiki page in a new line for each page.
                csv_writer.writerow([wiki_link])
    # Close the raw file
    raw_file.close()

    # Re open the raw csv data to read it, and open a new csv file to write.
    with open('\\Programs\\character_hrefs_raw.csv', 'r') as raw_file, open('\\Programs\\character_hrefs.csv', 'w') as sorted_file:
        # Read each line in the raw CSV to check if there are duplicates. If so, don't write that line and only write unique lines.
        sorted_file.writelines(unique_everseen(raw_file))
    # Close both files.
    raw_file.close()
    sorted_file.close()

    # ---------------------
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
