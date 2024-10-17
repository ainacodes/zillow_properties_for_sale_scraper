import os
import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import logging
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(filename='scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define headers for the HTTP request
HEADERS = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Define proxy settings (if needed)
proxy = os.getenv("PROXY")

PROXIES = {
    'http': f'http://{proxy}',
    'https': f'http://{proxy}'
}


def fetch_data(url):
    try:
        response = requests.get(url, headers=HEADERS, proxies=PROXIES)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        return None


def parse_data(content):
    try:
        soup = BeautifulSoup(content, 'html.parser')
        script_content = soup.find('script', id='__NEXT_DATA__')

        if script_content:
            json_content = script_content.string
            return json.loads(json_content)
        else:
            logging.error("Could not find the required script tag.")
            return None
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON: {e}")
        return None


def save_to_csv(house_details, output_file, mode='a'):
    with open(output_file, mode, newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)

        if mode == 'w':
            csvwriter.writerow([
                'HOUSE URL', 'PHOTO URLs', 'PRICE', 'FULL ADDRESS',
                'STREET', 'CITY', 'STATE', 'ZIP CODE',
                'NUMBER OF BEDROOMS', 'NUMBER OF BATHROOMS',
                'HOUSE SIZE', 'LOT SIZE', 'HOUSE TYPE'
            ])

        for detail in tqdm(house_details, desc="Saving house details", unit="house"):
            try:
                home_info = detail.get('hdpData', {}).get('homeInfo', {})
                photo_urls = ','.join([photo.get('url', '')
                                      for photo in detail.get('carouselPhotos', [])])

                # Concatenate lot area value and unit
                lot_size = f"{home_info.get('lotAreaValue', '')} {home_info.get('lotAreaUnit', '')}"

                csvwriter.writerow([
                    detail.get('detailUrl', ''),
                    photo_urls,
                    detail.get('price', ''),
                    detail.get('address', ''),
                    detail.get('addressStreet', ''),
                    detail.get('addressCity', ''),
                    detail.get('addressState', ''),
                    detail.get('addressZipcode', ''),
                    home_info.get('bedrooms', ''),
                    home_info.get('bathrooms', ''),
                    home_info.get('livingArea', ''),
                    lot_size,
                    home_info.get('homeType', '').replace('_', ' ')
                ])
            except Exception as e:
                logging.error(f"Error processing house detail: {e}")
                logging.error(f"Problematic detail: {detail}")


def main():
    base_url = "https://www.zillow.com/ne"
    page = 1
    max_pages = 5  # Set this to the number of pages you want to scrape, or None for all pages

    output_directory = 'OUTPUT_1'
    os.makedirs(output_directory, exist_ok=True)
    file_name = f'house_details-1-{max_pages}.csv'
    output_file = os.path.join(output_directory, file_name)

    with tqdm(total=max_pages, desc="Scraping pages", unit="page") as pbar:
        while max_pages is None or page <= max_pages:
            if page == 1:
                url = base_url
            else:
                url = f"{base_url}/{page}_p"

            logging.info(f"Scraping page {page}: {url}")
            content = fetch_data(url)

            if content:
                data = parse_data(content)
                if data:
                    try:
                        house_details = data['props']['pageProps']['searchPageState']['cat1']['searchResults']['listResults']
                        if house_details:
                            save_to_csv(house_details, output_file,
                                        mode='a' if page > 1 else 'w')
                            logging.info(
                                f"Data from page {page} has been saved to house_details-1-10.csv")
                        else:
                            logging.info(
                                f"No more results found on page {page}. Stopping.")
                            break
                    except KeyError as e:
                        logging.error(f"KeyError on page {page}: {e}")
                        logging.error(f"Data structure: {data}")
                        break
                else:
                    logging.error(
                        f"Failed to parse data from page {page}. Stopping.")
                    break
            else:
                logging.error(
                    f"Failed to fetch data from page {page}. Stopping.")
                break

            page += 1
            pbar.update(1)
            # Add a delay between requests to be respectful to the server
            time.sleep(5)

    logging.info("Scraping completed.")


if __name__ == "__main__":
    main()
