import csv
import re
from os import close
from csv import reader
from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    
    # Open the previously scraped href csv file
    with open('\\Programs\\character_hrefs.csv') as charlinks:
        
        # Loops through each row in the csv file and navigate to the link in that row. This visits all of the character pages in the csv file.
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

            # Wait for the dom to load.
            page.wait_for_load_state('domcontentloaded')
            
            # Queries the .mw-parser-output selector to get JNode information.
            page_checker = page.query_selector('.mw-parser-output')
            
            # Checks to see if the converted Href link from the Href scraper script led to a search page.
            # Search pages appear when there are multiple pages with the same name.
            # If so, add Fallout: New Vegas to the URL
            if ' lists articles associated with the same title. If an internal link led you here, please change the link to point directly to the intended page.' in page_checker.text_content():
                page.goto(link + '_(Fallout:_New_Vegas)')
                
            # Wait for the header to appear.
            page.wait_for_selector('.mw-parser-output >> h2')
            
            # Grab the JNode info for the character name in the infobox.
            character_name = page.query_selector('.va-infobox-title-main')
            
            # Sets the text document name it is going to output as the character name it grabbed.
            # And, format the title by replacing any quotes that may have appeared in the character name. Also add _SCRAPED.txt to the end.
            text_document_name = character_name.text_content().replace('"', '').replace('/', ' and ') + "_SCRAPED.txt"
            # Attached the character name to the character name variable.
            character_name = character_name.text_content()
            
            # Open a text document with the formated title and set encoding as utf-8.
            with open('Programs\\character page dumps\\' + text_document_name, 'w', encoding="utf-8") as cd:
                
                # Wait for then query each selector in the infobox. This is dynamic and does not query selectors specific to that page,
                # such as nth:child or things like that.
                page.wait_for_selector('table.va-infobox-group >> tbody >> tr')
                
                #Make sure to only query only the selectors with the visible attribute. You don't want hidden data.
                infoboxes = page.query_selector_all('table.va-infobox-group >> tbody >> tr:visible')
                
                # Look for only the Race, Gender, Affiliation, Role, and Rank rows in the table.
                for infobox in infoboxes:
                    if 'Race' in infobox.text_content():
                        # This formats each row of information to be lowercase, add a colon, add a space, then a new line.
                        # Other wise, you get this: RaceHuman
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
                # This is found by using Playwrights element selector's based on layout feature which
                # queries the selectors that are paragraphs, visible, but above the header 2 that has the text "Background".
                top_paragraphs = page.query_selector_all('p:visible:above(h2:has-text("Background"))')
                
                # After querying the JNode information for the top paragraphs, it then grabs the text content.
                # The top paragraphs are the paragraphs that are at the top of the character page, but not below the first header.
                for top_paragraph in top_paragraphs:
                    
                    # A check and balance to make sure the character name is in the 'top text'.
                    # The character name is usually located in the top text and if it grabs text that as that, since it works
                    # from the bottom up, it means it hit the end of the top texts.
                    if character_name in top_paragraph.text_content():
                        
                        # Format the scraped text to add summary: to the beginning.
                        top_texts = 'summary: ' + top_paragraph.text_content() + top_texts
                        break
                    else:
                        # Concatinates the scraped top text content to the top_texts variable.
                        # The reason for the variable top_paragraph not being used is due to the top_paragraph(s) varaibles
                        # being used to store JNode information while it loops through it.
                        top_texts = top_texts + top_paragraph.text_content()
                        
                #This removes the citations that are in the text (ex: [1], [2], etc). NovelAI doesn't like that for writing.
                top_texts = re.sub(r'\[\d+\]', '', top_texts)

                # Query all element selectors below the header2 with text "Background". This is similar to the above, but now working
                # down from the header 2.
                background_paragraphs = page.query_selector_all(':visible:below(h2:has-text("Background"))')

                for paragraph in background_paragraphs:
                    
                    # While going through the selector list, this checks to see if the selector has mw-headline in the html.
                    # Since we only want the paragraph selectors below h2 with the text 'Background', but above the next h2 in the page
                    # I needed to write this as a check and balance. This was difficult to solve, not because of the code, but because of the logic
                    # I had to go through to figure out this little bit of code below. I'm proud I figured this out.
                    if 'mw-headline' in paragraph.inner_html():
                        # While working down, a headline has been detected. All the paragraphs have been scarped. Break the for loop.
                        break
                    else:
                        # Concatinate the scraped text content on the variable.
                        background_texts = background_texts + paragraph.text_content()
                        
                # Format the text to remove citations.
                background_texts = re.sub(r'\[\d+\]', '', background_texts)
                
                # Write the both the scraped top paragraphs and the background paragraphs to the text file.
                cd.write(top_texts + ' ' + background_texts)
                    


                # ---------------------
                context.close()
        browser.close()
        
        #Print finish once done.
        print('Finished!')

with sync_playwright() as playwright:
    run(playwright)
