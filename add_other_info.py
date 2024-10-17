import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

HEADERS = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

proxy = os.getenv("PROXY")

PROXIES = {
    'http': f'http://{proxy}',
    'https': f'http://{proxy}'
}


def scrape_house_data(house_url):
    response = requests.get(house_url, headers=HEADERS, proxies=PROXIES)
    if response.status_code != 200:
        print(
            f"Failed to fetch data for {house_url}. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    content = soup.find('div', class_='ds-data-view-list')

    if not content:
        print(f"Failed to find content for {house_url}")
        return None

    year = content.find('span', class_='Text-c11n-8-100-2__sc-aiai24-0',
                        string=lambda text: "Built in" in text)
    year_built = year.text.strip().replace('Built in ', '') if year else "N/A"

    description_elem = content.find(
        'div', attrs={'data-testid': 'description'})
    description = description_elem.text.strip() if description_elem else "N/A"

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
    agency_name = agency_elem.text.strip() if agency_elem else "N/A"

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


def main():
    # Read the input CSV file
    input_file = './OUTPUT_1/house_SAMPLE.csv'

    output_directory = 'OUTPUT_2'
    os.makedirs(output_directory, exist_ok=True)
    file_name = 'house_SAMPLE_UPDATED.csv'
    output_file = os.path.join(output_directory, file_name)

    df = pd.read_csv(input_file)

    # Scrape data for each house URL
    scraped_data = []
    for index, row in df.iterrows():
        house_url = row['HOUSE URL']
        print(f"Scraping data for {house_url}")
        data = scrape_house_data(house_url)
        if data:
            scraped_data.append(data)

    # Create a new DataFrame with scraped data
    scraped_df = pd.DataFrame(scraped_data)

    # Combine the original DataFrame with the scraped data
    result_df = pd.concat([df, scraped_df], axis=1)

    # Save the combined data to a new CSV file
    result_df.to_csv(output_file, index=False)

    print(f"Scraped data has been saved to {output_file}")


if __name__ == "__main__":
    main()
