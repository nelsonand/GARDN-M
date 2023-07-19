import numpy as np
from utils import get_soup, write_array_to_csv


def scrape_wallethub_state_data(base_url, csv_file_name):
    '''
    Retrieves the equality rank of all 50 US states from the given URL and saves the results to a CSV file.

    Parameters:
    base_url (str): The URL of the webpage containing the state equality rankings.
    csv_file_name (str): The name of the CSV file to save the results to.
    '''

    # Get the parsed HTML content of the webpage
    soup = get_soup(base_url)

    # Find the table
    table = soup.find("table", class_="cardhub-edu-table")

    # Initialize lists to store state names and rankings
    rank = ['Rank']
    state = ['State']

    # Find all rows in the table body
    rows = table.tbody.find_all("tr")

    # Iterate over the rows and extract the state names and rankings
    for row in rows:
        columns = row.find_all("td")
        state.append(columns[1].text)
        rank.append(int(columns[0].text))

    # Convert to numpy arrays
    rank_np = np.array(rank)
    state_np = np.array(state)

    # Combine into one array
    equality_rank = np.stack((state_np, rank_np), axis=1)

    # Write the results to a CSV file
    write_array_to_csv(equality_rank, csv_file_name)


def scrape_wallethub_city_data(base_url, csv_file_name):
    '''
    Retrieves the equality rank of all 50 US states from the given URL and saves the results to a CSV file.

    Parameters:
    base_url (str): The URL of the webpage containing the state equality rankings.
    csv_file_name (str): The name of the CSV file to save the results to.
    '''

    # Get the parsed HTML content of the webpage
    soup = get_soup(base_url)

    # Find the table
    table = soup.find("table", class_="cardhub-edu-table")

    # Initialize lists to store state names and rankings
    rank = ['Rank']
    city = ['City']
    # Find all rows in the table body
    rows = table.tbody.find_all("tr")

    # Iterate over the rows and extract the city names and rankings
    for row in rows:
        columns = row.find_all("td")
        city.append(columns[1].text)
        rank.append(int(columns[0].text))

    # Convert to numpy arrays
    rank_np = np.array(rank)
    city_np = np.array(city)

    # Replace commas with semicolons in the city column
    city_np = np.char.replace(city_np, ',', ';')

    # Combine into one array
    equality_rank = np.stack((city_np, rank_np), axis=1)

    # Write the results to a CSV file
    write_array_to_csv(equality_rank, csv_file_name)


def scrape_wallethub_all():

    state_urls = [
        ('https://wallethub.com/edu/state-economies-with-most-racial-equality/75810', 'wallethub_stateRankingsRacialEquity.csv'),
        ('https://wallethub.com/edu/states-with-the-most-and-least-racial-progress/18428', 'wallethub_stateRankingsRacialIntegration.csv'),
        ('https://wallethub.com/edu/best-and-worst-states-for-women-equality/5835', 'wallethub_stateRankingsWomensRights.csv')
    ]

    # Scrape data for each URL
    for state_url, csv_file_name in state_urls:
        scrape_wallethub_state_data(state_url, csv_file_name)


    city_urls = [
        ('https://wallethub.com/edu/best-worst-cities-for-people-with-disabilities/7164', 'wallethub_cityRankingsDisabilities.csv'),
    ]

    # Scrape data for each URL
    for city_url, csv_file_name in city_urls:
        scrape_wallethub_city_data(city_url, csv_file_name)


if __name__ == '__main__':

    scrape_wallethub_all()