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


def fetch_book_data(book_url, id, dest_folder, skip_imgs, skip_txt):
    try:
        response = requests.get(book_url, verify=False)
        check_response(response)
        book_properties = parse_book_page(response.text)
        book_filename = f'{id}.{book_properties["autor"]} {book_properties["name"]}.txt'
        if not skip_txt:
            book_path = download_txt_file(urljoin(ROOT_URL, 'txt.php'), {'id': id}, book_filename, dest_folder)
            book_properties['book_path'] = book_path
        if not skip_imgs:
            download_image(urljoin(ROOT_URL, book_properties["img_url"]), dest_folder)
        return book_properties
    except requests.HTTPError as e:
        tqdm.write(f'Book from {book_url} not loaded something was wrong: {str(e)}')
    except requests.ConnectionError:
        tqdm.write(f'Error, cant connected to site!')


def write_to_json_file(data, filepath):
    with open(filepath, "w", encoding='utf8') as my_file:
        json.dump(data, my_file, ensure_ascii=False, sort_keys=True, indent=4)


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_page', help='Номер начальной страницы', default=1, type=int)
    parser.add_argument('--end_page', help='Номер конечной страницы', default=11, type=int)
    parser.add_argument('--dest_folder', help='Путь каталогу для сохранения данных', default='parse_results', type=str)
    parser.add_argument('--skip_imgs', help='Не скачивать обложки (0 или 1)', default=0, type=int)
    parser.add_argument('--skip_txt', help='Не скачивать текст книги (0 или 1)', default=0, type=int)
    parser.add_argument('--json_path', help='Путь к файлу с результатами парсинга', default='books.json', type=str)
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
            book_properties = fetch_book_data(book_url, id, args.dest_folder, args.skip_imgs, args.skip_txt)
            if book_properties:
                science_fiction_category_books.append(book_properties)
    write_to_json_file(science_fiction_category_books, args.json_path)


main()
