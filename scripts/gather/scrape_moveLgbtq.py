import numpy as np
from utils import get_soup, write_array_to_csv


def scrape_movelgbtq():
    '''
    Retrieves the equality rank of all 50 US states and saves the results to a CSV file.
    '''

    # url for the move.org website
    base_url = 'https://www.move.org/best-worst-states-start-lgbtq-family/'

    # Get the parsed HTML content of the webpage
    soup = get_soup(base_url)

    # Find all table rows on the page
    rows = soup.find_all('tr', class_='dynamic-table__row')

    # Find the starting row
    starting_row = find_starting_row(rows)

    # Extract rank and state values
    rank, state = extract_rank_and_state(rows, starting_row)

    # Convert to numpy arrays
    rank_np = np.array(rank)
    state_np = np.array(state)

    # Combine into one array
    equality_rank = np.stack((state_np, rank_np), axis=1)

    # Write the results to a CSV file
    write_array_to_csv(equality_rank, 'move_stateRankingsEquality.csv')


# Find the starting row where the first column value is 'Rank'
def find_starting_row(rows):
    for index, row in enumerate(rows):
        values = [td.text for td in row.find_all('td')]
        if len(values) > 0 and values[0] == 'Rank':
            return index
    return None


# Extract rank and state values from the table rows
def extract_rank_and_state(rows, starting_row):
    rank = ['Rank']
    state = ['State']

    for i, row in enumerate(rows[starting_row+1:], start=1):
        values = [td.text for td in row.find_all('td')]

        rank.append(i)
        state.append(values[0])

    return rank, state


if __name__ == '__main__':

    scrape_movelgbtq()