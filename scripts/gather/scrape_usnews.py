
import requests
from bs4 import BeautifulSoup

#! This isn't working. All my requests to usnews.com are timing out. It works for other sites though...

def main():
    """
    """

    # Make a request to the website
    url = 'https://www.usnews.com/news/best-states/articles/maryland-is-the-best-state-for-gender-equality'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    response = requests.get(url, headers=headers)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # save soup to txt file
    with open('soup.txt', 'w') as f:
        f.write(str(soup))



if __name__ == '__main__':
    main()


