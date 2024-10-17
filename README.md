# Zillow Properties for Sale Scraper

## Overview

This repository contains a web scraper designed to extract property listings from Zillow. The scraper retrieves data such as property details, prices, and locations, allowing users to analyze real estate trends and opportunities.

The details tutorial can be found in Rayobyte Community Web Scraping Project page.

## Features

This Zillow Scraper consists of **TWO** parts

The **first part** consists of scraping these values:
`HOUSE URL`, `PHOTO URLs`, `PRICE`, `FULL ADDRESS`, `STREET`, `CITY`, `STATE`, `ZIP CODE`, `NUMBER OF BEDROOMS`, `NUMBER OF BATHROOMS`, `HOUSE SIZE`, `LOT SIZE` and `HOUSE TYPE`

The **second parts** consist of scraping the following values:
`YEAR BUILT`, `DESCRIPTION`, `LISTING DATE`, `DAYS ON ZILLOW`, `TOTAL VIEWS`, `TOTAL SAVED`, `REALTOR NAME`, `REALTOR CONTACT NO`, `AGENCY`, `CO-REALTOR NAME`, `CO-REALTOR CONTACT NO` and `CO-REALTOR AGENCY`

## Installation

To get started with the Zillow Properties for Sale Scraper, follow these steps:

1. Clone the Repository:

   ```
   git clone https://github.com/ainacodes/zillow_properties_for_sale_scraper.git
   ```

2. Navigate to the Directory:

   ```
   cd zillow_properties_for_sale_scraper
   ```

## Code Funcionality

- `zillow_draft.ipynb`: Consist of step-by-step elements scrape.

### The first part:

- `first_page.py`: Consist of complete code to scrape the first page that apears from the search results
- `all_pages.py`: Consist of complete code to scrape all pages or until which page you want to scrape.

### The second part:

- `add_other_info.py`: Consist of the complete code with additional data that scrape inside the properties page.
- `add_other_info_proxy_rotate.py`: Consist of the complete code with additional data that scrape inside the properties page with implementations of proxy rotation.

## Contributing

Contributions are welcome! If you have suggestions for improvements or find bugs, please open an issue or submit a pull request.

## Contact

For any inquiries, please email me at noraina.nordin16@gmail.com
