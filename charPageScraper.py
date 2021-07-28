import csv
import re
from os import close
from csv import reader
from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    with open('C:\\Users\\zenti\\Desktop\\Programs\\character_hrefs.csv') as charlinks:
        for link in charlinks:
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

            with open('C:\\Users\\zenti\\Desktop\\Programs\\character page dumps\\' + text_document_name, 'w', encoding="utf-8") as cd:

                page.wait_for_selector('table.va-infobox-group >> tbody >> tr')
                infoboxes = page.query_selector_all('table.va-infobox-group >> tbody >> tr:visible')

                for infobox in infoboxes:
                    if 'Race' in infobox.text_content():
                        cd.write(infobox.text_content().replace('Race', 'race: ') + '\n')

                    elif 'Gender' in infobox.text_content():
                        cd.write(infobox.text_content().replace('Gender', 'gender: ') + '\n')

                    elif 'Affiliation' in infobox.text_content():
                        cd.write(infobox.text_content().replace('Affiliation', 'affiliation: ') + '\n')

                    elif 'Role' in infobox.text_content():
                        cd.write(infobox.text_content().replace('Role', 'role: ') + '\n')

                    elif 'Rank' in infobox.text_content():
                        cd.write(infobox.text_content().replace('Rank', 'rank: ') + '\n')
                    else:
                        pass
                    



                # Query the paragraph above the table of contents, which is probably the summary, hopefully.
                top_paragraphs = page.query_selector_all('p:visible:above(h2:has-text("Background"))')

                for top_paragraph in top_paragraphs:
                    if character_name in top_paragraph.text_content():
                        top_texts = 'summary: ' + top_paragraph.text_content() + top_texts
                        break
                    else:
                        top_texts = top_texts + top_paragraph.text_content()
                
                top_texts = re.sub(r'\[\d+\]', '', top_texts)

                # query all selectors below the header with text "Background"
                background_paragraphs = page.query_selector_all(':visible:below(h2:has-text("Background"))')

                for paragraph in background_paragraphs:
                    
                    # Check that shit to see if it has "mw-headline" class. That means its a header.
                    # And that means you got all the paragraphs in "Background".
                    # Congrats dumb fuck it only took you 9 hours to figure that out.
                    if 'mw-headline' in paragraph.inner_html():
                        break
                    else:
                        background_texts = background_texts + paragraph.text_content()

                background_texts = re.sub(r'\[\d+\]', '', background_texts)
                cd.write(top_texts + ' ' + background_texts)
                    


                # ---------------------
                context.close()
        browser.close()
        print('Finished!')

with sync_playwright() as playwright:
    run(playwright)