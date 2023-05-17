# -*-Python-*-
# Created by nelsonand at 09 Mar 2023

"""
This script manages all gathering of data.
"""

from scrape_moveLgbtq import scrape_movelgbtq
from scrape_usnews import scrape_usnews


def main():
    """
    Scrapes data from all sources and saves the results to CSV files in the scraped_data directory.
    """
    scrape_movelgbtq()
    scrape_usnews()


if __name__ == '__main__':
    main()

