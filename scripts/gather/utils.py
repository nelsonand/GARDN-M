"""

Useful functions for the gathering scripts

"""

import requests
from bs4 import BeautifulSoup
import time
import csv
import os


def get_soup(url):
    '''
    Retrieves and parses the HTML content of a webpage using Beautiful Soup.

    Parameters:
    url (str): The URL of the webpage to retrieve and parse.

    Returns:
    BeautifulSoup object: The parsed HTML content of the webpage.
    '''

    # Set the headers to simulate a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }

    # Sleep for half a second to avoid overloading the website
    time.sleep(.5) 

    # Make a GET request to the website for the specified state
    response = requests.get(url, headers=headers)

    # Parse the HTML content using BeautifulSoup
    return BeautifulSoup(response.content, 'html.parser')


def write_array_to_csv(results, csv_file_name):
    '''
    Writes the results of a state equality ranking to a CSV file.

    Parameters:
    results (numpy.ndarray): A NumPy array containing the state name and its equality rank.
    csv_file (str): The name of the CSV file to write the results to.
    '''

    processed_data_directory = get_processed_data_directory()
    save_path = os.path.join(processed_data_directory, csv_file_name)

    # Open the CSV file for writing
    with open(save_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write each result row
        for row in results:
            writer.writerow(row)


def get_processed_data_directory():
    '''
    Returns the path to the processed data directory.
    '''

    return os.path.abspath(f"{__file__}/../../../data/processed_data")



if __name__ == '__main__':

    pass
