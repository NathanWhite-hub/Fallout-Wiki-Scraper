# Fallout-Wiki-Scraper
This is a personal project I created using Python and the Playwright framework in Visual Studio Code to scrape webdata from https://fallout-archive.fandom.com.

In order to get comfortable with Playwright amazing features for automating naviating webpages, I started this project to collect data to be used in NovelAI for writers.

This project was difficult due to me having to make this as dynamic as possible. Each page has a similar, but slightly different layout and programing it to be completely automated meant me having to account for this.

A special thanks to the developers of Playwright, you guys did an amazing job and this wouldn't have been possible without it. Check them out here: https://playwright.dev

## The Start
This program starts with the *character href collector* script which navigates to the Fallout: New Vegas characters page. This page holds a table with every character in the game. The script waits for the table to load then queries every selector located in that table that is a tag and the first child in the table. After querying the element selectors, the selectors are stored in a list which the script cycles through a for loop.

These element selectors are typically stored as JSNode data, so the script gets the href attribute, which is formated like such: /wiki/John_Doe and concatinates the the href attribute to the prewritten text https://fallout-archive.fandom.com. This is stored in a variable wiki_link which now holds the string https://fallout-archive.fandom.com/wiki/John_Doe then writes this variable to a row in the csv file character_hrefs.csv for the next step.

## Scraping the Pages
The next step (and the real meat and potatoes) starts in the *char Page Scraper* script. The script opens the character_href.csv file and loops through each row in the csv file. For each loop the script navigates to the page, waits for the dom content to load, then begins querying. It first starts off by querying the .mw-parser-output as a second check to make sure the page is not a search page. Sometimes the link in the csv file will lead to a search page that contains multiple characters and not that actual character's page. This is due to multiple characters having the same name, but we only want a character from Fallout: New Vegas. If that is the case, it adds _(Fallout:_New_Vegas) to the URL, which will navigate it to the correct character page.

### Infobox and the Top Paragraph(s)

Now the actual scraping. After the correct page is loaded, the script moves onto querying and scraping. The script starts by querying the 'infobox' table which holds the  full name, race, gender, faction afffiliation, role, and rank of the character. It only selects elements that have a visible attribute, so invisible data is not scraped (we don't want that). These are selected row by row and formated to be lowercase, add a colon, a space, and a new line, otherwise you get this: RaceHumanGenderMale

After that, it writes it to a text file that has the character's name that is formated to remove quotes. It then queries the top paragraphs by using Playwright's element selectors by location feature. This scans the page to query selectors that are on the specified layout. In this case, the top paragraphs are p elements, that are visible, and are above an h2 tag that has the text 'Background'. Every page has this, so the dynamic layout is not a problem here.

Because it is querying from the h2 tag and up, it checks each of the selectors text content to check if the character name is it in. Always the first paragraph contains text such as "John Doe is a guy in the Mojave Wasteland in 2278...". If the name is detected in the first paragraph, that means that the top has been reached and it breaks from the for loop. It then moves onto removing any citations in the text content (ex: [1], [2], [3], etc). NovelAI doesn't like this, so to make life easier, I automated the removal of these here. This is also done for the next step as well

### Background Paragraph(s)

This was the most difficult part of this project. Every page has a background header and under that are paragraphs that contain more indepth background information about the character. I only wanted the paragraphs under the background header, but I didn't want the paragraphs located under and other header. This was easier said then done and being completely honest, it took me about nine hours of working through this problem to figure it out (including remoting into my computer from my phone to write while I was visiting family). This ended up being two lines of code and I felt stupid afterwards, but you live and you learn, and I was so happy I figured this out.

### The Problem

So, the script queries every single visible element selectors that is below the h2 tag that contains the text "Background". Why every single element? Well, I wanted to write a check and balance that would stop once it reached another header. If I query all of the p tags, I'll get every single paragraph, including the paragraphs below other header tags, and I don't want that.

### The Solution

So, for each selector in the selector list, it checks to see if the tag has the text "mw-headline" within the inner html. The inner HTML looks like this `<span class="mw-headline" id="Background">Background</span>`
The text mw-headline is a CSS class specific to the h2 tag, so knowing that, if it detects that the inner html has that text in it, then it means that is a header. Unlike the top paragraphs where it was working from the bottom up (from the h2 background tag), it is now working down (from the h2 background tag). Once it detects a header, it breaks from the for loop, which means you got all of the paragraphs that are below the h2 background tag, but above whatever h2 tag was next.

### Why this Solution?
This adds a very dynamic element to the script, which was needed. While the h2 background tag is always on a character page, the next h2 tag could have any text, and this was the best way to account for it, while keeping the code as clean as possible.

## The End
The scraped text content in the variable background_texts is formated to remove citations then both the top paragraph text content and the background paragraph text content is written to the text file. This process for the location scraper is nearly identical, with only changes for the type of text it is grabbing from the info box. If you wish to see this in action, feel free to download these scripts and load them up on your favorite editor.

## Scraped Text Example
This was scraped from the page https://fallout-archive.fandom.com/wiki/Bert_Gunnarsson
```
race: Ghoul
gender: Male
affiliation: Followers of the ApocalypseNew Canaan (formerly)New California Republic
role: MinisterDoctor
summary: Elder Bert Gunnarsson is a Mormon who is a doctor and minister residing in the Aerotech office park refugee camp in New Vegas in Fallout: New Vegas.
 A Mormon priest from Utah, Bert is a relatively new arrival in the Mojave wasteland, having come to the area only six months earlier.He followed the trail his old friend, Nephi, in an attempt to turn him back to the Church, away from drugs and the Fiends. To do so, Bret trained under the Followers of the Apocalypse to learn medicine and other forms of care. However, after following him to New Vegas, he soon realized that it is a lost cause, that Nephi allowed himself to be consumed by drugs and hate.
Bert, despite losing his friend, chose to move on.  He saw an opportunity to help Vegas at the Aerotech Office Park that the NCR repurposed into a refugee camp. Much to the chagrin of the Followers, he chose to focus his efforts in guiding through ministry and as a doctor, helping the beleaguered  Captain Parker. He accepts the fact that Nephi will one day be killed and hopes his soul will find peace.
```
