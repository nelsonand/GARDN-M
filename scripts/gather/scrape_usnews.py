"""
This script scrapes the US News Best States website for the equality rank of all 50 US states and writes the results to a CSV file.

When this code breaks, we probably need to change the "soup.find('span', {'data-test-id': 'equality-rank'})" line to match the new HTML structure.

"""

from utils import get_soup, write_array_to_csv


list_of_states = [
    'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
    'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho',
    'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
    'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
    'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada',
    'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
    'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon',
    'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
    'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
    'West Virginia', 'Wisconsin', 'Wyoming'
]


def get_state_data(state):
    '''
    Returns the equality rank of a state, given the state name as a string.

    Parameters:
    state (str): The name of the state to look up.

    Returns:
    int: The equality rank of the state, as an integer, -1 if the equality rank is not found.
    '''

    # if there is a space in the state name, replace it with a dash
    if ' ' in state:
        state = state.replace(' ', '-')

    # Base URL for the US News Best States website
    base_url = 'https://www.usnews.com/news/best-states/'

    # Get the parsed HTML content of the webpage
    soup = get_soup(base_url + state.lower())

    # Extract the equality rank from the webpage
    equality_rank_span = soup.find('span', {'data-test-id': 'equality-rank'})

    # Raise an AttributeError if the equality rank element is not found
    if equality_rank_span is None:
        return -1

    # Extract the integer value from the equality rank element and return it
    equality_rank = int(equality_rank_span.text.strip('#'))
    return equality_rank


def get_all_state_data():
    '''
    Retrieves the equality rank of all 50 US states and returns the results as a NumPy array.

    Returns:
    numpy.ndarray: A NumPy array containing the state name and its equality rank for all 50 US states.
    '''

    results = []

    results.append(['State', 'Equality Rank'])

    # Loop through all 50 states and get their equality rank
    for i, state in enumerate(list_of_states):
        equality_rank = get_state_data(state)
        results.append([state, equality_rank])

        # Print the progress counter
        print(f'\rReading states: {i+1}/{len(list_of_states)}', end='')

    print()

    write_array_to_csv(results, 'usnews_state_equality_rankings.csv')

    return results


if __name__ == '__main__':

    get_all_state_data()
