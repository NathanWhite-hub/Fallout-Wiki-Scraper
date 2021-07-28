import csv
import re
from os import close
from csv import reader
from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    with open('\\Programs\\location_hrefs.csv') as locationlinks:
        for link in locationlinks:
            context = browser.new_context()
            background_texts = ''
            top_texts = ''
            
            # Open new page
            page = context.new_page()
            page.set_default_navigation_timeout(300000)
            page.set_default_timeout(300000)

            # Navigate to the characters page
            page.goto(link)

            # Wait for a p selector to appear.
            page.wait_for_load_state('domcontentloaded')

            page_checker = page.query_selector('.mw-parser-output')

            if ' lists articles associated with the same title. If an internal link led you here, please change the link to point directly to the intended page.' in page_checker.text_content():
                page.goto(link + '_(Fallout:_New_Vegas)')

            page.wait_for_selector('.mw-parser-output >> h2')

            character_name = page.query_selector('.va-infobox-title-main')
            text_document_name = character_name.text_content().replace('"', '').replace('/', ' and ') + "_SCRAPED.txt"
            character_name = character_name.text_content()
            print(character_name)

            with open('\\Programs\\location page dumps\\' + text_document_name, 'w', encoding="utf-8") as cd:

                page.wait_for_selector('table.va-infobox-group >> tbody >> tr')
                infoboxes = page.query_selector_all('table.va-infobox-group >> tbody >> tr:visible')

                for infobox in infoboxes:
                    if 'Factions' in infobox.text_content():
                        cd.write(infobox.text_content().replace('Factions', 'affiliations: ') + '\n')
                    else:
                        pass
                    



                # Query the paragraph above the table of contents, which is probably the summary, hopefully.
                top_paragraphs = page.query_selector_all('p:visible:above(#Layout:has-text("Layout"))')

                for top_paragraph in top_paragraphs:
                    if character_name in top_paragraph.text_content():
                        top_texts = top_paragraph.text_content() + top_texts
                        break
                    else:
                        top_texts = top_texts + top_paragraph.text_content()
                
                top_texts = re.sub(r'\[\d+\]', '', top_texts)
                cd.write('summary: ' + top_texts)
                    


                # ---------------------
                context.close()
        browser.close()
        print('Finished!')

with sync_playwright() as playwright:
    run(playwright)
