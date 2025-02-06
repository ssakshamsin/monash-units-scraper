# monash-units-scraper
A simple Python script to scrape all the units available on the Monash handbook.

First, the script makes API calls to https://api-ap-southeast-2.prod.courseloop.com/publisher/search-all? to simply get all the units and their names, codes and handbook URLs (that is basically all the information available from the API) in portions of 100, before saving them to monash_units.json. It then uses selenium to go to the handbook URL of each page and scrape the page content and save the unit faculty, credit points, and assessment summary along with the code, name and url to monash_units_extracted.json. 

Personally, I ran this overnight with 2 seconds between each unit to avoid rate limiting - you can play around with the interval to make it faster. It took between 6-8 hours to scrape it all (not completely sure because I was asleep).
