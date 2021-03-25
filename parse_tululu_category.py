import requests
from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urljoin
from book_loader import parse_book_page, download_txt_file, download_image, check_response
from tqdm import tqdm
import json
import argparse


ROOT_URL = 'https://tululu.org'
BOOK_CATEGORY = 'l55'


def fetch_book_data(book_url, id):
    try:
        response = requests.get(book_url, verify=False)
        check_response(response)
        book_properties = parse_book_page(response.text)
        book_filename = f'{id}.{book_properties["autor"]} {book_properties["name"]}.txt'
        book_path = download_txt_file(urljoin(ROOT_URL, 'txt.php'), {'id': id}, book_filename)
        download_image(urljoin(ROOT_URL, book_properties["img_url"]))
        book_properties['book_path'] = book_path
        return book_properties
    except requests.HTTPError as e:
        tqdm.write(f'Book from {book_url} not loaded something was wrong: {str(e)}')
    except requests.ConnectionError:
        tqdm.write(f'Error, cant connected to site!')


def write_to_json_file(data, filename):
    with open(f"{filename}.json", "w", encoding='utf8') as my_file:
        json.dump(data, my_file, ensure_ascii=False, sort_keys=True, indent=4)


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_page', help='Начальная страница', default=1)
    parser.add_argument('--end_page', help='Конечная страница', default=11)
    args = parser.parse_args()
    science_fiction_category_books = []
    for i in tqdm(range(args.start_page, args.end_page), desc='Pages'):
        category_url = urljoin(ROOT_URL, BOOK_CATEGORY, i)
        response = requests.get(category_url, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        links_to_books = soup.select('.d_book .bookimage a')
        for tag in tqdm(links_to_books, desc=f'Books on page({i})'):
            href = tag.attrs['href']
            book_url = urljoin(ROOT_URL, href)
            id = int(href.replace('b', '').replace('/', ''))
            book_properties = fetch_book_data(book_url, id)
            if book_properties:
                science_fiction_category_books.append(book_properties)
    write_to_json_file(science_fiction_category_books, 'books')


main()
