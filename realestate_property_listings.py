from bs4 import BeautifulSoup
import httpx
import random
import lxml
import re
import time
import pandas as pd

headers_list = [
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none'
    },
    {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    },
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,/;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none'
    },
    {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none'
    }
]

headers = random.choice(headers_list)

city = "new-york/new-york"
country = "united-states"
start_page = 1
end_page = 10

listings = []

for pagin in range(start_page, end_page + 1):
    print(f"Scraping page {pagin}...")

    base_url = f"https://www.luxuryestate.com/{country}/{city}?sort={pagin}"
    
    try:
        r = httpx.get(base_url, headers=headers, timeout=60, follow_redirects=True)
        if r.status_code != 200:
            print(f"Failed to fetch {base_url}: Status {r.status_code}")
            
    except httpx.RequestError as e:
        print(f"Request failed for {base_url}: {e}")
    
    soup = BeautifulSoup(r.text, "lxml")
    
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/p"):
            links.append("https://www.luxuryestate.com" + href)
        elif href.startswith("https://www.luxuryestate.com/p"):
            links.append(href)
    
    links = list(set(links))
    
    for url in links:
        try:
            r = httpx.get(url, headers=headers, timeout=180, follow_redirects=True)
            if r.status_code != 200:
                print(f"Failed to fetch {url}: Status {r.status_code}")
                continue
        except httpx.RequestError as e:
            print(f"Request failed for {url}: {e}")
            continue
    
        try:
            page_soup = BeautifulSoup(r.text, "lxml")
            
            listing_title = page_soup.select_one("div.listing-title-with-map, h1.title-property.style-display3.mobile-style-display-subtitle")
            listing_title = listing_title.get_text(strip=True) if listing_title else None
            
            listing_price = page_soup.select_one('div.prices.visible-xs.style-display3, [data-rol="amount-price"]')
            listing_price = listing_price.get_text(strip=True) if listing_price else None
            
            rooms = None
            bedrooms = None
            bathrooms = None
            cooling = None
            elevator = False
            floor = None
            reference = None
            view = None
            year = None
            
            features = page_soup.select('div.general-features div.item-inner.short-item.feat-item')
            
            for feat in features:
                label = feat.select_one("span.feat-label.style-body")
                value = feat.select_one("div.single-value.style-body")
                if label and value:
                    label_text = label.get_text(strip=True)
                    value_text = value.get_text(strip=True)
                    if "Rooms" in label_text:
                        rooms = value_text
                    elif "Bedrooms" in label_text:
                        bedrooms = value_text
                    elif "Bathrooms" in label_text:
                        bathrooms = value_text
                    elif "Year of construction" in label_text:
                        year = value_text
                    elif "Cooling Systems" in label_text:
                        cooling = value_text
                    elif "Floor Type" in label_text:
                        floor = value_text
                    elif "Reference" in label_text:
                        reference = value_text
                    elif "View" in label_text:
                        view = value_text
                    elif "Elevator" in label_text:
                        elevator = True
        
            time.sleep(random.uniform(0.3, 0.8))
        
            listings.append({
                'Listing_Title': listing_title,
                'Listing_Price': listing_price,
                'Rooms': rooms,
                'Bedrooms': bedrooms,
                'Bathrooms': bathrooms,
                'Year_of_Construction': year,
                'Cooling_System': cooling,
                'Floor_Type': floor,
                'Reference': reference,
                'View': view,
                'Elevator': elevator,
                'URL': url
            })
    
        except:
            print(f"Failed to fetch {url}")

print(f"Successfully scraped {len(listings)} listings.")
#for listing in listings:
  #  print(listing)

df = pd.DataFrame(listings)
df.to_csv('Luxury_Property_Listings.csv', index=False)
