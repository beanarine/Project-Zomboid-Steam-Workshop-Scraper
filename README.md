# About
I wanted to play some multiplayer Project Zomboid with my wife and grabbing all the Mod IDs was going to be a pain. So I put together a small scraping script.


## Requirements
- Python 3.11
- Selenium(Firefox webdriver)


## Instructions
Run from the command line as
```
python ./scraper.py [--id ID OR --url URL] [options]
```
**NOTE:**

  Either the --id or --url option **MUST** be included as the scraping target.
  Failure to include either or including both will throw an error.


| Option | |
| ---- | ---- |
| -h, --help | Show help. |
|-i ID, --id ID | The Steam Workshop ID of the collection to be scraped. |
| -u URL, --url URL | The Steam Workshop URL of the collection to be scraped. |
| -o OUTPUT, --output OUTPUT | The path where you want the data output as a .csv file. |
| -q, --quiet | Scrape without any prompts or screen output. |
| -f, --force | Scrape without any prompts. |


**NOTE:**

  If --output isn't specified, the data will be output to ./output/addon_details.csv
