import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import pandas as pd
import random
import time
import logging
from tqdm import tqdm

load_dotenv()

# Set up logging
logging.basicConfig(filename='scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

HEADERS = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def load_proxies(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]


PROXY_LIST = load_proxies('proxy-list.txt')


def get_random_proxy():
    return random.choice(PROXY_LIST)


def get_proxies(proxy):
    return {
        'http': f'http://{proxy}',
        'https': f'http://{proxy}'
    }


def scrape_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        proxy = get_random_proxy()
        proxies = get_proxies(proxy)
        try:
            response = requests.get(
                url, headers=HEADERS, proxies=proxies, timeout=30)
            if response.status_code == 200:
                return response
            else:
                logging.warning(
                    f"Attempt {attempt + 1} failed with status code {response.status_code} for URL: {url}")
        except requests.RequestException as e:
            logging.error(
                f"Attempt {attempt + 1} failed with error: {e} for URL: {url}")

        time.sleep(random.uniform(1, 3))

    logging.error(
        f"Failed to fetch data for {url} after {max_retries} attempts.")
    return None


def scrape_house_data(house_url):
    response = scrape_with_retry(house_url)
    if not response:
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    content = soup.find('div', class_='ds-data-view-list')

    if not content:
        logging.error(f"Failed to find content for {house_url}")
        return None

    year = content.find('span', class_='Text-c11n-8-100-2__sc-aiai24-0',
                        string=lambda text: "Built in" in text)
    year_built = year.text.strip().replace('Built in ', '') if year else "N/A"

    description_elem = content.find(
        'div', attrs={'data-testid': 'description'})
    description = description_elem.text.strip().replace(
        'Show more', '') if description_elem else "N/A"

    listing_details = content.find_all(
        'p', class_='Text-c11n-8-100-2__sc-aiai24-0', string=lambda text: text and "Listing updated" in text)
    listing_date = "N/A"
    if listing_details:
        date_details = listing_details[0].text.strip()
        date_part = date_details.split(' at ')[0]
        listing_date = date_part.replace('Listing updated: ', '').strip()

    containers = content.find_all('dt')
    days_on_zillow = containers[0].text.strip() if len(
        containers) > 0 else "N/A"
    views = containers[2].text.strip() if len(containers) > 2 else "N/A"
    total_save = containers[4].text.strip() if len(containers) > 4 else "N/A"

    realtor_elem = content.find(
        'p', attrs={'data-testid': 'attribution-LISTING_AGENT'})
    if realtor_elem:
        realtor_content = realtor_elem.text.strip().replace(',', '')
        if 'M:' in realtor_content:
            name, contact = realtor_content.split('M:')
        else:
            name_contact = realtor_content.rsplit(' ', 1)
            name = name_contact[0]
            contact = name_contact[1]

        realtor_name = name.strip()
        realtor_contact = contact.strip()

    else:
        realtor_name = "N/A"
        realtor_contact = "N/A"

    agency_elem = content.find(
        'p', attrs={'data-testid': 'attribution-BROKER'})
    agency_name = agency_elem.text.strip().replace(',', '') if agency_elem else "N/A"

    co_realtor_elem = content.find(
        'p', attrs={'data-testid': 'attribution-CO_LISTING_AGENT'})
    if co_realtor_elem:
        co_realtor_content = co_realtor_elem.text.strip().replace(',', '')
        if 'M:' in co_realtor_content:
            name, contact = co_realtor_content.split('M:')
        else:
            name_contact = co_realtor_content.rsplit(' ', 1)
            name = name_contact[0]
            contact = name_contact[1]

        co_realtor_name = name.strip()
        co_realtor_contact = contact.strip()

    else:
        co_realtor_name = "N/A"
        co_realtor_contact = "N/A"

    co_realtor_agency_elem = content.find(
        'p', attrs={'data-testid': 'attribution-CO_LISTING_AGENT_OFFICE'})
    co_realtor_agency_name = co_realtor_agency_elem.text.strip(
    ) if co_realtor_agency_elem else "N/A"

    return {
        'YEAR BUILT': year_built,
        'DESCRIPTION': description,
        'LISTING DATE': listing_date,
        'DAYS ON ZILLOW': days_on_zillow,
        'TOTAL VIEWS': views,
        'TOTAL SAVED': total_save,
        'REALTOR NAME': realtor_name,
        'REALTOR CONTACT NO': realtor_contact,
        'AGENCY': agency_name,
        'CO-REALTOR NAME': co_realtor_name,
        'CO-REALTOR CONTACT NO': co_realtor_contact,
        'CO-REALTOR AGENCY': co_realtor_agency_name
    }


def ensure_output_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created output directory: {directory}")


def load_progress(output_file):
    if os.path.exists(output_file):
        return pd.read_csv(output_file)
    return pd.DataFrame()


def save_progress(df, output_file):
    df.to_csv(output_file, index=False)
    logging.info(f"Progress saved to {output_file}")


def main():
    input_file = './OUTPUT_1/house_details.csv'

    output_directory = 'OUTPUT_2'
    file_name = 'house_details_scraped.csv'
    output_file = os.path.join(output_directory, file_name)
    ensure_output_directory(output_directory)

    df = pd.read_csv(input_file)

    # Load existing progress
    result_df = load_progress(output_file)

    # Determine which URLs have already been scraped
    scraped_urls = set(result_df['HOUSE URL']
                       ) if 'HOUSE URL' in result_df.columns else set()

    # Scrape data for each house URL
    for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Scraping Progress"):
        house_url = row['HOUSE URL']

        # Skip if already scraped
        if house_url in scraped_urls:
            continue

        logging.info(f"Scraping data for {house_url}")
        data = scrape_house_data(house_url)

        if data:
            # Combine the original row data with the scraped data
            combined_data = {**row.to_dict(), **data}
            new_row = pd.DataFrame([combined_data])

            # Append the new row to the result DataFrame
            result_df = pd.concat([result_df, new_row], ignore_index=True)

            # Save progress after each successful scrape
            save_progress(result_df, output_file)

        # Add a random delay between requests (1 to 5 seconds)
        time.sleep(random.uniform(1, 5))

    logging.info(f"Scraping completed. Final results saved to {output_file}")
    print(
        f"Scraping completed. Check {output_file} for results and scraper.log for detailed logs.")


if __name__ == "__main__":
    main()
