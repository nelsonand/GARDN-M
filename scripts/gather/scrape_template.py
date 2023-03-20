
import requests
from bs4 import BeautifulSoup

#! This isn't working. All my requests to usnews.com are timing out. It works for other sites though...

def main():
    """
    """

    # Make a request to the website
    url = '##### FILL THIS IN #####'
    headers = {'##### FILL THIS IN #####'}
       
    response = requests.get(url, headers=headers)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # save soup to txt file
    with open('soup.txt', 'w') as f:
        f.write(str(soup))



if __name__ == '__main__':
    main()


