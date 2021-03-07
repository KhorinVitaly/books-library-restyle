import requests
import os
from bs4 import BeautifulSoup
import urllib3
from pathvalidate import sanitize_filename


def download_txt_file(url, filename, folder='books/'):
    response = requests.get(url, verify=False, allow_redirects=True)
    check_for_redirect(response)
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, sanitize_filename(filename))
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def get_book_title(url):
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.find('div', id='content')
    if not content:
        return
    title_tag = content.find('h1')
    parts_of_title = title_tag.text.split('::')
    return parts_of_title[0].strip()


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    for id in range(1, 11):
        book_url = f'http://tululu.org/b{id}/'
        title = get_book_title(book_url)
        if not title:
            print(f'Title not found at {book_url} check the url!')
            continue
        filename = f'{id}.{title}.txt'
        try:
            download_url = f'https://tululu.org/txt.php?id={id}'
            filepath = download_txt_file(download_url, filename)
            print(f'The book loaded successfully {filepath}')
        except requests.HTTPError:
            print(f'Book from {download_url} not loaded something was wrong!')


# url = 'http://tululu.org/b1/'
# get_book_properties(url)

main()
