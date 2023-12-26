## Project Zomboid Steam Workshop Scraper
## v1.0

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs

import argparse, os, re, csv


# Handle terminal args for Workshop ID or URL
def dir_path(string):
    if os.path.exists(string):
        return string

    rePath = re.match(r".*\/", string)
    if rePath != None:
        path = rePath.group()
        if os.path.isdir(path) == False:
            raise NotADirectoryError(
                f"Error: {string} is not a valid path. One or more directories do not exist."
            )
    if string[-4:] == ".csv":
        return string
    elif string[-4] == ".":
        raise NotImplementedError(
            f"Error: Please output to an existing directory or a .csv file only."
        )
    else:
        raise NotADirectoryError(
            f"Error: {string} is not a valid path. One or more directories do not exist."
        )


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--id", help="The Steam Workshop collection ID.")
parser.add_argument("-u", "--url", help="The Steam Workshop collection URL.")
parser.add_argument(
    "-o", "--output", type=dir_path, help="The path where you want the .csv output."
)
parser.add_argument(
    "-q",
    "--quiet",
    action="store_true",
    help="Scrape without any prompts or screen output.",
)
parser.add_argument(
    "-f", "--force", action="store_true", help="Scrape without any prompts."
)
args = parser.parse_args()


base_url = ""
base_url_head = "https://steamcommunity.com/sharedfiles/filedetails/?id="

# Resolve target Workshop ID or URL
if args.id != None and args.url != None:
    raise RuntimeError(
        "Error: Use the --id or the --url argument. Do not use both arguments."
    )
elif args.id != None:
    base_url = base_url_head + args.id
elif args.url != None:
    base_url = args.url
else:
    raise RuntimeError(
        "Error: Either the --id or the --url arguments need to be used to point to the respective Steam Workshop collection ID or URL."
    )


# Resolve output argument
output = "./output/addon_details.csv"
if args.output != None:
    path = re.match(r"(.+\/)(?=[^\/\\]+.csv)", args.output)
    if path == None:
        prefix = "./output/"
    else:
        prefix = path.group()
    filename = re.search(r"([^\/\\]+.csv)", args.output)
    if filename == None:
        suffix = "addon_details.csv"
    else:
        suffix = filename.group()
    output = prefix + suffix

if args.quiet == False and args.force == False:
    print(f"Output target: {output}")
    print(f"Is this correct?")
    confirm = input(f"y/n\n")
    match = re.match("y", confirm.lower())
    if match is None:
        quit()
    print()



# Set up Selenium driver
options = webdriver.FirefoxOptions()
options.add_argument("-headless")
driver = webdriver.Firefox(options=options)

# Navigate to provided collection (Workshop ID/URL) based on type of submitted args
# base_url = 'https://steamcommunity.com/sharedfiles/filedetails/?id={WorkshopID}'
driver.get(base_url)

# Scrape collection details
collection_title = driver.find_element(
    by=By.XPATH, value='//div[@class="workshopItemTitle"]'
).text
collection_assembler_raw = driver.find_element(
    by=By.XPATH, value='//div[@class="friendBlockContent"]'
).text
collection_assembler = re.match(r".*", collection_assembler_raw).group()
items = driver.find_elements(by=By.XPATH, value='//div[@class="collectionItemDetails"]')
raw_collection_description = driver.find_element(
    by=By.XPATH, value='//div[@class="workshopItemDescription"]'
).text
soup = bs(raw_collection_description, features="html.parser")
collection_description = soup.get_text(strip=True).replace("\n", " ")

collection = {
    "link": base_url,
    "title": collection_title,
    "assembler": collection_assembler,
    "description": collection_description,
    "items": len(items),
    "workshopID": re.search(r"(?<=id=)([0-9]+)", base_url).group(),
}

# Output will be written at the end of the scrape with a dictionary.
# Opportunity to combine with collection
rows = []
rows.append(
    {
        "Title": collection["title"],
        "Type": "Collection",
        "Link": collection["link"],
        "Author": collection["assembler"],
        "Description": collection["description"],
        "Workshop ID": collection["workshopID"],
        "Mod ID": "n/a",
    }
)

if args.quiet == False:
    print(f"Collection details:")
    print(f"Title:\t{collection['title']}")
    print(f"Assembler:\t{collection['assembler']}")
    print(f"Item count: \t{collection['items']}")

    if args.force == False:
        print(f"\nProceed with scraping this collection?")
        confirm = input(f"y/n\n")
        match = re.match("y", confirm.lower())
        if match is None:
            quit()
    print()
items_list = []

for i in range(len(items)):
    # For testing only to limit requests. Comment out to scrape full list.
    # if(i != 0):
      # break

    a = items[i].find_element(by=By.XPATH, value=".//a")
    link = a.get_attribute("href")
    title = a.find_element(by=By.XPATH, value='.//div[@class="workshopItemTitle"]').text
    workshopID = re.search(r"(?<=id=)([0-9]+)", link).group()

    item = {
        "link": link,
        "title": title,
        "workshopID": workshopID,
    }
    items_list.append(item)


for i in range(len(items_list)):
    # Visit every Workshop item linked.
    item = items_list[i]
    link = item["link"]

    driver.get(link)
    author_raw = driver.find_element(
        by=By.XPATH, value='//div[@class="friendBlockContent"]'
    ).text
    author = re.match(r".*", author_raw).group()

    raw_description = driver.find_element(
        by=By.XPATH, value='.//div[@class="workshopItemDescription"]'
    ).text
    soup = bs(raw_description, features="html.parser")
    text = soup.get_text(strip=True)
    description = text.replace("\n", " ")
    modIDs = re.findall(r"(?<=Mod ID: )(.+)", text)

    item["author"] = author
    item["description"] = description
    item["modIDs"] = modIDs

    if args.quiet == False:
        print(f"Item {i}\n-----------")
        print(f"Link:\t{item['link']}")
        print(f"Title:\t{item['title']}")
        print(f"Created by:\t{item['author']}")
        print(f"Description:\t{item['description']}")
        print(f"Workshop ID:\t{item['workshopID']}")
        print(f"Mod IDs: {item['modIDs']}")
        print(f"-----------\n")

    rows.append(
        {
            "Title": item["title"],
            "Type": "Addon",
            "Link": item["link"],
            "Author": item["author"],
            "Description": item["description"],
            "Workshop ID": item["workshopID"],
            "Mod ID": item["modIDs"],
        }
    )

driver.close()
if args.quiet == False:
    print(f"Scrape successful. Scraped {collection['items']} addons.")

# Create a csv of the scraped data.
f = open(output, "w")
header = ["Title", "Type", "Link", "Author", "Description", "Workshop ID", "Mod ID"]
writer = csv.DictWriter(f, fieldnames=header)
writer.writeheader()
writer.writerows(rows)
f.close()
if args.quiet == False:
    print(f"Scraped data successfully written to .csv at {os.path.abspath(output)}")
