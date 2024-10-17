import os
import requests
from bs4 import BeautifulSoup
import json
import csv
from dotenv import load_dotenv

load_dotenv()

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
        print(f"Error fetching data: {e}")
        return None


def parse_data(content):
    soup = BeautifulSoup(content, 'html.parser')
    script_content = soup.find('script', id='__NEXT_DATA__')

    if script_content:
        json_content = script_content.string
        return json.loads(json_content)
    else:
        print("Could not find the required script tag.")
        return None


def save_to_csv(house_details, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)

        csvwriter.writerow([
            'HOUSE URL', 'PHOTO URLs', 'PRICE', 'FULL ADDRESS',
            'STREET', 'CITY', 'STATE', 'ZIP CODE',
            'NUMBER OF BEDROOMS', 'NUMBER OF BATHROOMS',
            'HOUSE SIZE', 'LOT SIZE', 'HOUSE TYPE'
        ])

        for detail in house_details:
            home_info = detail['hdpData']['homeInfo']
            photo_urls = ','.join([photo['url']
                                  for photo in detail['carouselPhotos']])

            # Concatenate lot area value and unit
            lot_size = f"{home_info.get('lotAreaValue')} {home_info.get('lotAreaUnit')}"

            csvwriter.writerow([
                detail['detailUrl'],
                photo_urls,
                detail['price'],
                detail['address'],
                detail['addressStreet'],
                detail['addressCity'],
                detail['addressState'],
                detail['addressZipcode'],
                home_info.get('bedrooms'),
                home_info.get('bathrooms'),
                home_info.get('livingArea'),
                lot_size,
                home_info.get('homeType').replace('_', ' ')
            ])


def main():
    URL = "https://www.zillow.com/ne"
    content = fetch_data(URL)

    output_directory = 'OUTPUT_1'
    os.makedirs(output_directory, exist_ok=True)
    file_name = 'house_details_first_page.csv'
    output_file = os.path.join(output_directory, file_name)

    if content:
        data = parse_data(content)
        if data:
            house_details = data['props']['pageProps']['searchPageState']['cat1']['searchResults']['listResults']
            save_to_csv(house_details, output_file)
            print(f"Data has been saved to {output_file}")


if __name__ == "__main__":
    main()
